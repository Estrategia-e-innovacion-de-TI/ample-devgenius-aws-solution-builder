from fastmcp import FastMCP
from typing import Any
import uuid
from utils import BEDROCK_MODEL_ID, store_in_s3, save_conversation, collect_feedback, invoke_bedrock_model_streaming

# Initialize FastMCP
mcp = FastMCP("CDK Generator")

@mcp.tool()
def generate_cdk_code(
    solution_description: str,
    conversation_messages: list[dict] = None,
    conversation_id: str = None
) -> str:
    """
    Generar código AWS CDK en TypeScript para desplegar infraestructura de AWS para una solución dada.
    
    Args:
        solution_description: Descripción de la solución de AWS para la cual generar código CDK
        conversation_messages: Mensajes de conversación anteriores para contexto (opcional)
        conversation_id: ID de la conversación para seguimiento (opcional)
    
    Returns:
        Generated AWS CDK TypeScript code and deployment commands
    """
    
    # Initialize defaults
    if conversation_messages is None:
        conversation_messages = []
    
    if conversation_id is None:
        conversation_id = str(uuid.uuid4())
    
    # Prepare messages for the model
    cdk_messages = conversation_messages[:]
    
    cdk_prompt = f"""
    Para la siguiente solución: {solution_description}
    
    Genera un script de CDK en TypeScript para automatizar y desplegar los recursos necesarios de AWS.
    Proporciona el código fuente real para todos los trabajos cuando corresponda.
    El código CDK debe aprovisionar todos los recursos y componentes sin restricciones de versión.
    Si se necesita código en Python, genera un ejemplo "Hello, World!".
    Al final, genera comandos de ejemplo para desplegar el código CDK.
    """
    
    # Add the prompt to messages
    cdk_messages.append({"role": "user", "content": cdk_prompt})
    
    try:
        # Invoke the Bedrock model to get the CDK response
        cdk_response, stop_reason = invoke_bedrock_model_streaming(cdk_messages)
        
        # Store results and collect feedback (these run synchronously in FastMCP)
        store_in_s3(content=cdk_response, content_type='cdk')
        save_conversation(conversation_id, cdk_prompt, cdk_response)
        collect_feedback(str(uuid.uuid4()), cdk_response, "generate_cdk", BEDROCK_MODEL_ID)
        
        return f"# AWS CDK Code Generated\n\n{cdk_response}"
        
    except Exception as e:
        return f"Error generating CDK code: {str(e)}"


# Server setup and execution
if __name__ == "__main__":
    # Run the FastMCP server
    mcp.run()