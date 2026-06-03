"""
Orquestación del agente usando LangGraph.
Define el grafo del agente con herramientas y memoria de conversación.
"""
import os

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_aws import ChatBedrock
from botocore.config import Config

from chatbot.config import AWS_REGION, BEDROCK_MODEL_ID, BEDROCK_MAX_TOKENS, BEDROCK_TEMPERATURE
from chatbot.utils import load_markdown_files, load_skills

# Directorio de principios de arquitectura
PRINCIPLES_DIR = os.path.join(os.path.dirname(__file__), "principles", "source")
PRINCIPLES = load_markdown_files(PRINCIPLES_DIR)

# Cargar skills dinámicamente
SKILLS_DIR = os.path.join(os.path.dirname(__file__), "skills")
ALL_TOOLS = load_skills(SKILLS_DIR)

# Generar lista de herramientas dinámicamente desde las skills cargadas
_TOOLS_LIST = "\n".join(f"- {t.name}: {t.description}" for t in ALL_TOOLS)

SYSTEM_PROMPT = f"""Eres ArqGenius, un sistema de arquitectura técnica y de soluciones senior especializado en diseñar arquitecturas cloud y empresariales.

Tu rol es:
1. Entender los requisitos del usuario mediante preguntas claras y específicas.
2. Proponer arquitecturas robustas siguiendo las mejores prácticas (Well-Architected Framework) o lineamientos de buenas prácticas de implementación y desarrollo.
3. Usar tus herramientas para generar artefactos cuando el usuario lo solicite.
4. SIEMPRE aplicar y respetar los Principios y Lineamientos de Arquitectura definidos a continuación en TODAS las soluciones que propongas.

Herramientas disponibles:
{_TOOLS_LIST}

Reglas:
- Responde siempre en Español.
- Cuando el usuario pida generar un artefacto, usa la herramienta correspondiente pasando como contexto un resumen completo de la solución discutida.
- Si la arquitectura no está clara, haz preguntas para refinarla antes de generar artefactos.
- Resalta los nombres de servicios AWS en **negrita**.
- Sé conciso pero completo en tus explicaciones.
- Toda solución propuesta DEBE cumplir con los principios de arquitectura listados abajo. Si una propuesta viola algún principio, ajústala o advierte al usuario.

== PRINCIPIOS Y LINEAMIENTOS DE ARQUITECTURA ==
Los siguientes principios son OBLIGATORIOS y deben aplicarse en toda solución propuesta:
{PRINCIPLES}
== FIN DE PRINCIPIOS ==
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
