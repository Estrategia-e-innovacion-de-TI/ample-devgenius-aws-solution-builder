"""
Herramienta: Generar diagrama C4 Nivel C1 (System Context Diagram) en Structurizr DSL.
Exporta la imagen PNG del diagrama a la carpeta output/.
"""
import os
import json
import datetime
from langchain_core.tools import tool

from chatbot.config import OUTPUT_DIR
from chatbot.utils import get_code_from_markdown, clean_dsl_code, structurizr_to_diagram


@tool
def generate_c1_context(conversation_context: str) -> str:
    """
    Genera un diagrama C4 Nivel C1 (System Context Diagram) usando Structurizr DSL
    y lo convierte a imagen PNG exportada a la carpeta output/. Usa esta herramienta
    cuando el usuario pida un diagrama de contexto del sistema, un diagrama C1,
    o un diagrama que muestre el sistema principal con sus actores y sistemas externos.

    Un diagrama C1 muestra ÚNICAMENTE:
    - El sistema principal (System Under Design).
    - Personas/actores que interactúan con el sistema.
    - Sistemas externos relacionados.
    - Relaciones de alto nivel entre ellos.

    NO incluye contenedores internos, componentes, clases ni detalles de implementación.

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

    c1_prompt = """Genera un diagrama C4 Nivel C1 (System Context Diagram) en código Structurizr DSL para la solución dada.

    #### Regla del C1
    El System Context SOLO responde a la pregunta:
    > "¿Quién usa el sistema y con qué sistemas externos se comunica?"

    El foco está en ACTORES y SISTEMAS EXTERNOS DE NEGOCIO, NO en tecnología de infraestructura.

    REGLAS CRÍTICAS PARA UN DSL C1 VÁLIDO:
    1. Responde solo con código DSL en markdown (```dsl).
    2. Modela ÚNICAMENTE:
       - El sistema principal como un softwareSystem (una caja única que representa TODO el sistema).
       - Personas/actores de negocio como person (quién usa el sistema).
       - Sistemas externos de negocio como softwareSystem (con qué se comunica a nivel de negocio).
       - Relaciones de alto nivel entre ellos describiendo el propósito de negocio.
    3. NO incluyas NUNCA:
       - Servicios de infraestructura o cloud (AWS, Azure, GCP): NO S3, NO Lambda, NO DynamoDB, NO RDS, NO SQS, NO SNS, NO API Gateway, NO CloudFront, NO EC2, etc.
       - Contenedores (container) dentro de ningún sistema.
       - Componentes (component).
       - Clases o código.
       - Bases de datos internas, APIs internas, microservicios u otros detalles internos.
       - Tecnologías de implementación como nombres de frameworks, servicios cloud o herramientas.
    4. Los sistemas externos deben ser sistemas de NEGOCIO (ej: "Payment Provider", "Email Service", "ERP System", "Identity Provider"), NO servicios de infraestructura cloud.
    5. Las relaciones deben describir INTENCIÓN de negocio (ej: "Procesa pagos", "Envía notificaciones", "Consulta inventario"), NO protocolos técnicos.
    6. Usa EXACTAMENTE los mismos nombres de variables de forma consistente.
    7. Cada elemento debe estar declarado antes de ser referenciado.
    8. Usa camelCase para todas las variables.
    9. La vista debe ser SOLO systemContext (NO container ni component views).
    10. Incluye siempre la estructura de workspace, model y views.

    Estructura esperada:
    ```dsl
    workspace "System Context" {
        model {
            // Personas/Actores de negocio
            customer = person "Customer" "End user who interacts with the platform"
            admin = person "Administrator" "Manages the system configuration"

            // Sistema principal (una sola caja)
            mainSystem = softwareSystem "My Platform" "High-level description of what the system does for the business"

            // Sistemas externos de NEGOCIO (no servicios cloud)
            paymentProvider = softwareSystem "Payment Provider" "Processes financial transactions" "Existing System"
            emailService = softwareSystem "Email Service" "Delivers notifications to users" "Existing System"
            erpSystem = softwareSystem "ERP System" "Source of truth for business data" "Existing System"

            // Relaciones con intención de negocio
            customer -> mainSystem "Browses catalog and places orders"
            admin -> mainSystem "Configures products and monitors operations"
            mainSystem -> paymentProvider "Processes payments"
            mainSystem -> emailService "Sends order confirmations and alerts"
            erpSystem -> mainSystem "Provides product and inventory data"
        }
        views {
            systemContext mainSystem "SystemContext" {
                include *
                autoLayout
            }
        }
    }
    ```

    PATRONES CORRECTOS PARA C1:
    - person -> softwareSystem (actor de negocio usa el sistema)
    - softwareSystem -> softwareSystem (sistema se comunica con otro sistema externo de negocio)

    ERRORES A EVITAR:
    - NO incluir servicios AWS/cloud como sistemas externos (S3, Lambda, RDS, etc. son detalles de implementación del nivel C2/C3)
    - NO declarar containers dentro de softwareSystem
    - NO crear vistas de tipo container o component
    - NO incluir detalles de implementación interna
    - NO usar nombres técnicos de infraestructura como nombres de sistemas
    - Nombres de variable inconsistentes

    IMPORTANTE: Piensa en este diagrama como una explicación para un stakeholder de negocio.
    No debe aparecer NINGÚN servicio cloud ni tecnología específica. Solo actores, el sistema
    como caja negra, y sistemas externos de negocio con los que interactúa.
    """

    messages = [
        {"role": "user", "content": f"Contexto de la solución:\n{conversation_context}"},
        {"role": "user", "content": c1_prompt},
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
    dsl_file = os.path.join(OUTPUT_DIR, f"diagram_c1_context_{timestamp}.dsl")
    with open(dsl_file, "w", encoding="utf-8") as f:
        f.write(dsl_code)

    # Generar imagen PNG usando Kroki
    png_file = None
    diagram_bytes = structurizr_to_diagram(dsl_code, fmt="png")
    if diagram_bytes:
        png_file = os.path.join(OUTPUT_DIR, f"diagram_c1_context_{timestamp}.png")
        with open(png_file, "wb") as f:
            f.write(diagram_bytes)

    result = f"Diagrama C4 Nivel C1 (System Context) generado.\n- Archivo DSL: {dsl_file}"
    if png_file:
        result += f"\n- Imagen PNG: {png_file}"
    else:
        result += "\n- [WARN] No se pudo generar la imagen PNG. Revisa la sintaxis DSL."

    return result
