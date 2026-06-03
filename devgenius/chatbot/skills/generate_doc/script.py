"""
Skill: Generar documentación técnica.
"""
import os
import json
import datetime

from chatbot.config import OUTPUT_DIR


def run(conversation_context: str) -> str:
    """Ejecuta la generación de documentación técnica."""
    from chatbot.config import BEDROCK_MODEL_ID, BEDROCK_MAX_TOKENS, AWS_REGION
    import boto3
    from botocore.config import Config

    config = Config(read_timeout=1000, retries=dict(max_attempts=3))
    bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION, config=config)

    doc_prompt = """
    Para la solución dada, genera una documentación técnica completa y profesional que incluya una tabla de contenidos,
    para la siguiente arquitectura. Expande todos los temas de la tabla de contenidos para crear una documentación técnica profesional integral.
    """

    messages = [
        {"role": "user", "content": f"Contexto de la solución:\n{conversation_context}"},
        {"role": "user", "content": doc_prompt},
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
    output_file = os.path.join(OUTPUT_DIR, f"documentation_{timestamp}.md")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_response)

    return f"Documentación técnica generada.\n- Archivo: {output_file}\n\n{full_response}"
