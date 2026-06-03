"""
Skill: Generar diagrama de arquitectura AWS (XML draw.io).
Exporta el archivo .drawio y .html a la carpeta output/.
"""
import os
import json
import datetime

from chatbot.config import OUTPUT_DIR
from chatbot.utils import get_code_from_markdown, convert_xml_to_html


def run(conversation_context: str) -> str:
    """Ejecuta la generación del diagrama de arquitectura AWS."""
    from chatbot.config import BEDROCK_MODEL_ID, BEDROCK_MAX_TOKENS, AWS_REGION
    import boto3
    from botocore.config import Config

    config = Config(read_timeout=1000, retries=dict(max_attempts=3))
    bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION, config=config)

    architecture_prompt = """
    Genera un diagrama de arquitectura y flujo de datos en AWS para la solución dada, aplicando las buenas prácticas de AWS. Sigue estos pasos:
    1. Crea un archivo XML adecuado para draw.io que capture la arquitectura y el flujo de datos.
    2. Haz referencia a los íconos de arquitectura más recientes de AWS: https://aws.amazon.com/architecture/icons/. Usa SIEMPRE los íconos de AWS más recientes.
    3. Responde únicamente con el XML en formato markdown—sin texto adicional.
    4. Asegura que el XML esté completo, con todas las etiquetas de apertura y cierre correctamente formadas.
    5. Confirma que todos los servicios/íconos de AWS estén correctamente conectados y contenidos dentro de un ícono de AWS Cloud, desplegados dentro de una VPC cuando corresponda.
    6. Elimina espacios en blanco innecesarios para optimizar el tamaño.
    7. Usa íconos válidos de arquitectura de AWS para representar los servicios.
    8. El diagrama debe estar claramente definido, ordenado y legible. El flujo debe ser limpio, con todas las flechas conectadas sin superposiciones.
    9. El XML final debe ser sintácticamente correcto y cubrir todos los componentes de la solución dada.
    """

    messages = [
        {"role": "user", "content": f"Contexto de la solución:\n{conversation_context}"},
        {"role": "user", "content": architecture_prompt},
    ]

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": BEDROCK_MAX_TOKENS,
        "messages": messages,
        "temperature": 0,
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

    # Extraer XML y guardar archivo
    try:
        xml_code = get_code_from_markdown(full_response, language="xml")[0]
    except (IndexError, Exception):
        xml_code = full_response

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    xml_file = os.path.join(OUTPUT_DIR, f"architecture_{timestamp}.drawio")
    with open(xml_file, "w", encoding="utf-8") as f:
        f.write(xml_code)

    # También guardar HTML para visualización
    html_file = None
    try:
        html_content = convert_xml_to_html(xml_code)
        html_file = os.path.join(OUTPUT_DIR, f"architecture_{timestamp}.html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)
    except Exception:
        pass

    result = f"Diagrama de arquitectura generado.\n- Archivo XML: {xml_file}"
    if html_file:
        result += f"\n- Archivo HTML (visualizable en navegador): {html_file}"

    return result
