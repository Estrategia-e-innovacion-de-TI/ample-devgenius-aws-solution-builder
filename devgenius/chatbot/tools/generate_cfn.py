"""
Herramienta: Generar plantilla AWS CloudFormation (YAML).
"""
import os
import json
import datetime
from langchain_core.tools import tool

from chatbot.config import OUTPUT_DIR
from chatbot.utils import get_code_from_markdown


@tool
def generate_cfn(conversation_context: str) -> str:
    """
    Genera una plantilla de AWS CloudFormation en YAML para desplegar la solución
    discutida en la conversación.

    Args:
        conversation_context: Resumen de la solución/arquitectura discutida en la conversación.

    Returns:
        La plantilla CloudFormation generada y la ruta del archivo exportado.
    """
    from chatbot.config import BEDROCK_MODEL_ID, BEDROCK_MAX_TOKENS, AWS_REGION
    import boto3
    from botocore.config import Config

    config = Config(read_timeout=1000, retries=dict(max_attempts=3))
    bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION, config=config)

    cfn_prompt = """
    Para la solución dada, genera una plantilla de CloudFormation en YAML para automatizar el despliegue de recursos de AWS.
    Proporciona el código fuente real para todos los jobs cuando corresponda.
    La plantilla de CloudFormation debe aprovisionar todos los recursos y componentes.
    Si se necesita código en Python, genera un ejemplo "Hello, World!".
    Al final, genera comandos de ejemplo para desplegar la plantilla de CloudFormation.
    """

    messages = [
        {"role": "user", "content": f"Contexto de la solución:\n{conversation_context}"},
        {"role": "user", "content": cfn_prompt},
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

    # Extraer YAML y guardar
    try:
        yaml_code = get_code_from_markdown(full_response, language="yaml")[0]
    except (IndexError, Exception):
        yaml_code = full_response

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    yaml_file = os.path.join(OUTPUT_DIR, f"cloudformation_{timestamp}.yaml")
    with open(yaml_file, "w", encoding="utf-8") as f:
        f.write(yaml_code)

    md_file = os.path.join(OUTPUT_DIR, f"cloudformation_{timestamp}.md")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(full_response)

    return f"Plantilla CloudFormation generada.\n- Template YAML: {yaml_file}\n- Documentación: {md_file}\n\n{full_response}"
