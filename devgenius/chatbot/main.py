"""
DevGenius CLI - Punto de entrada principal.
Bucle interactivo de conversación con el agente de arquitectura AWS.
"""
import uuid
import sys

from chatbot.agent import create_agent


WELCOME_MESSAGE = """
╔══════════════════════════════════════════════════════════════╗
║                    🏗️  DevGenius CLI                        ║
║         Arquitecto de Soluciones AWS con IA                 ║
╠══════════════════════════════════════════════════════════════╣
║  Comandos especiales:                                       ║
║    /new     - Iniciar nueva conversación                    ║
║    /tools   - Listar herramientas disponibles               ║
║    /exit    - Salir                                         ║
╠══════════════════════════════════════════════════════════════╣
║  Los artefactos generados se guardan en: chatbot/output/    ║
╚══════════════════════════════════════════════════════════════╝

Bienvenido a DevGenius: convirtiendo ideas en realidad.
Juntos diseñaremos tu arquitectura y solución AWS.
¡Comencemos a construir!
"""

TOOLS_INFO = """
Herramientas disponibles:
  1. generate_architecture - Diagrama de arquitectura AWS (XML/draw.io + HTML)
  2. generate_cdk          - Código AWS CDK en TypeScript
  3. generate_cfn          - Plantilla AWS CloudFormation (YAML)
  4. generate_doc          - Documentación técnica completa
  5. generate_dsl          - Diagrama C4 (Structurizr DSL + imagen PNG)

Pide al agente que genere cualquiera de estos artefactos durante la conversación.
"""


def run_cli():
    """Ejecuta el bucle principal de la CLI."""
    print(WELCOME_MESSAGE)

    agent = create_agent()
    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}

    print(f"[Sesión: {session_id[:8]}...]\n")

    while True:
        try:
            user_input = input("\n👤 Tú: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nHasta luego! 👋")
            sys.exit(0)

        if not user_input:
            continue

        # Comandos especiales
        if user_input.lower() == "/exit":
            print("\nHasta luego! 👋")
            sys.exit(0)
        elif user_input.lower() == "/new":
            session_id = str(uuid.uuid4())
            config = {"configurable": {"thread_id": session_id}}
            print(f"\n--- Nueva conversación iniciada [Sesión: {session_id[:8]}...] ---\n")
            continue
        elif user_input.lower() == "/tools":
            print(TOOLS_INFO)
            continue

        # Invocar el agente
        print("\n🤖 DevGenius: ", end="", flush=True)
        try:
            response = agent.invoke(
                {"messages": [("user", user_input)]},
                config=config,
            )

            # Extraer la última respuesta del asistente
            ai_messages = [
                msg for msg in response["messages"]
                if hasattr(msg, "type") and msg.type == "ai" and msg.content
            ]

            if ai_messages:
                final_response = ai_messages[-1].content
                # Si el contenido es una lista (multi-block), concatenar textos
                if isinstance(final_response, list):
                    text_parts = [
                        block.get("text", "") if isinstance(block, dict) else str(block)
                        for block in final_response
                    ]
                    final_response = "\n".join(text_parts)
                print(final_response)
            else:
                print("[Sin respuesta del agente]")

        except Exception as e:
            print(f"\n[ERROR] {e}")
            print("Intenta de nuevo o escribe /new para reiniciar la conversación.")


def main():
    """Entry point."""
    run_cli()


if __name__ == "__main__":
    main()
