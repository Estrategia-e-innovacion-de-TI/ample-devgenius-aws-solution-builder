"""
Herramienta: Generar diagrama C4 en Structurizr DSL.
Exporta la imagen PNG del diagrama a la carpeta output/.
"""
import os
import json
import datetime
from langchain_core.tools import tool

from chatbot.config import OUTPUT_DIR
from chatbot.utils import get_code_from_markdown, clean_dsl_code, structurizr_to_diagram


@tool
def generate_dsl(conversation_context: str) -> str:
    """
    Genera un diagrama de arquitectura C4 usando Structurizr DSL y lo convierte
    a imagen PNG exportada a la carpeta output/. Usa esta herramienta cuando el
    usuario pida un diagrama C4 o un diagrama DSL de la solución.

    Args:
        conversation_context: Resumen de la solución/arquitectura discutida en la conversación.

    Returns:
        El código DSL generado y la ruta de la imagen exportada.
    """
    from chatbot.config import BEDROCK_MODEL_ID, BEDROCK_MAX_TOKENS, AWS_REGION
    import boto3
    from botocore.config import Config

    config = Config(read_timeout=1000, retries=dict(max_attempts=3))
    bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION, config=config)

    dsl_prompt = """Genera un diagrama de arquitectura de software en código Structurizr DSL para la solución dada.

    REGLAS CRÍTICAS PARA UN DSL VÁLIDO:
    1. Responde solo con código DSL en markdown (```dsl).
    2. Usa EXACTAMENTE los mismos nombres de variables de forma consistente.
    3. NUNCA crees relaciones entre elementos padre e hijo.
    4. Todas las relaciones deben ser entre elementos del MISMO nivel jerárquico o entre diferentes sistemas/contenedores.
    5. Cada elemento debe estar declarado antes de ser referenciado.
    6. Usa camelCase para todas las variables.
    7. Incluye siempre la estructura de workspace, model y views.

    Estructura esperada:
    ```dsl
    workspace "Name" {
        model {
            // Personas
            user = person "User" "Description"
            // Sistemas
            system = softwareSystem "System" "Description" {
                container1 = container "Container" "Description" "Technology"
            }
            // Relaciones (NUNCA padre->hijo)
            user -> system "Uses"
        }
        views {
            systemContext system {
                include *
                autoLayout
            }
            container system {
                include *
                autoLayout
            }
        }
    }
    ```

    PATRONES CORRECTOS:
    - person -> softwareSystem
    - softwareSystem -> externalSystem
    - container -> container (en sistemas diferentes)
    - container -> externalSystem

    ERRORES A EVITAR:
    - mainSystem -> containerInsideMainSystem (relación padre-hijo)
    - Nombres de variable inconsistentes
    """

    messages = [
        {"role": "user", "content": f"Contexto de la solución:\n{conversation_context}"},
        {"role": "user", "content": dsl_prompt},
    ]

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": BEDROCK_MAX_TOKENS,
        "messages": messages,
        "temperature": 1,
        "thinking": {"type": "enabled", "budget_tokens": 4096},
    }

    response = bedrock_client.invoke_model(
        body=json.dumps(body),
        modelId=BEDROCK_MODEL_ID,
        contentType="application/json",
        accept="application/json",
    )

    response_body = json.loads(response["body"].read())
    full_response = ""
    for block in response_body.get("content", []):
        if block.get("type") == "text":
            full_response += block["text"]

    # Extraer y limpiar código DSL
    try:
        raw_dsl = get_code_from_markdown(full_response, language="dsl")[0]
        dsl_code = clean_dsl_code(raw_dsl)
    except (IndexError, Exception):
        dsl_code = clean_dsl_code(full_response)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Guardar DSL como texto
    dsl_file = os.path.join(OUTPUT_DIR, f"diagram_c4_{timestamp}.dsl")
    with open(dsl_file, "w", encoding="utf-8") as f:
        f.write(dsl_code)

    # Generar imagen PNG usando Kroki
    png_file = None
    diagram_bytes = structurizr_to_diagram(dsl_code, fmt="png")
    if diagram_bytes:
        png_file = os.path.join(OUTPUT_DIR, f"diagram_c4_{timestamp}.png")
        with open(png_file, "wb") as f:
            f.write(diagram_bytes)

    result = f"Diagrama C4 DSL generado.\n- Archivo DSL: {dsl_file}"
    if png_file:
        result += f"\n- Imagen PNG: {png_file}"
    else:
        result += "\n- [WARN] No se pudo generar la imagen PNG. Revisa la sintaxis DSL."

    return result
