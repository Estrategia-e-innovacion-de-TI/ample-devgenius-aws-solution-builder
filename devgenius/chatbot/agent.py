"""
Orquestación del agente usando LangGraph.
Define el grafo del agente con herramientas y memoria de conversación.
"""
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_aws import ChatBedrock
from botocore.config import Config

from chatbot.config import AWS_REGION, BEDROCK_MODEL_ID, BEDROCK_MAX_TOKENS, BEDROCK_TEMPERATURE
from chatbot.tools import ALL_TOOLS

SYSTEM_PROMPT = """Eres DevGenius, un arquitecto de soluciones senior especializado en diseñar arquitecturas cloud.

Tu rol es:
1. Entender los requisitos del usuario mediante preguntas claras y específicas.
2. Proponer arquitecturas robustas siguiendo las mejores prácticas (Well-Architected Framework) o lineamientos de buenas prácticas de implementación y desarrollo.
3. Usar tus herramientas para generar artefactos cuando el usuario lo solicite.

Herramientas disponibles:
- generate_architecture: Genera un diagrama de arquitectura AWS de la solución en XML (draw.io). Exporta archivo .drawio y .html.
- generate_cdk: Genera código CDK en TypeScript para desplegar la solución.
- generate_cfn: Genera plantilla CloudFormation en YAML.
- generate_doc: Genera documentación técnica completa.
- generate_dsl: Genera diagrama C4 en Structurizr DSL y exporta imagen PNG.

Reglas:
- Responde siempre en español.
- Cuando el usuario pida generar un artefacto, usa la herramienta correspondiente pasando como contexto un resumen completo de la solución discutida.
- Si la arquitectura no está clara, haz preguntas para refinarla antes de generar artefactos.
- Resalta los nombres de servicios AWS en **negrita**.
- Sé conciso pero completo en tus explicaciones.
"""


def create_agent():
    """Crea y retorna el agente LangGraph con herramientas y memoria."""

    llm = ChatBedrock(
        model_id=BEDROCK_MODEL_ID,
        region_name=AWS_REGION,
        provider="anthropic",
        model_kwargs={
            "max_tokens": BEDROCK_MAX_TOKENS,
            "temperature": BEDROCK_TEMPERATURE,
        },
        config=Config(read_timeout=1000, retries=dict(max_attempts=3)),
    )

    memory = MemorySaver()

    agent = create_react_agent(
        model=llm,
        tools=ALL_TOOLS,
        checkpointer=memory,
        prompt=SYSTEM_PROMPT,
    )

    return agent
