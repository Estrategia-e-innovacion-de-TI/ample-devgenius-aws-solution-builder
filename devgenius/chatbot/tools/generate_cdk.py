"""
Herramienta: Generar código AWS CDK (TypeScript).
"""
import os
import json
import datetime
from langchain_core.tools import tool

from chatbot.config import OUTPUT_DIR


@tool
def generate_cdk(conversation_context: str) -> str:
    """
    Genera código de infraestructura como código (IaC) usando AWS CDK en TypeScript
    para la solución discutida en la conversación.

    Args:
        conversation_context: Resumen de la solución/arquitectura discutida en la conversación.

    Returns:
        El código CDK generado y la ruta del archivo exportado.
    """
    from chatbot.config import BEDROCK_MODEL_ID, BEDROCK_MAX_TOKENS, AWS_REGION
    import boto3
    from botocore.config import Config

    config = Config(read_timeout=1000, retries=dict(max_attempts=3))
    bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION, config=config)

    cdk_prompt = """
    Para la solución dada, genera un script de CDK en TypeScript para automatizar y desplegar los recursos necesarios de AWS.
    Proporciona el código fuente real para todos los trabajos cuando corresponda.
    El código CDK debe aprovisionar todos los recursos y componentes sin restricciones de versión.
    Si se necesita código en Python, genera un ejemplo "Hello, World!".
    Al final, genera comandos de ejemplo para desplegar el código CDK.
    """

    messages = [
        {"role": "user", "content": f"Contexto de la solución:\n{conversation_context}"},
        {"role": "user", "content": cdk_prompt},
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

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"cdk_stack_{timestamp}.md")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_response)

    return f"Código CDK generado.\n- Archivo: {output_file}\n\n{full_response}"
