from fastmcp import FastMCP
import uuid
from utils import BEDROCK_MODEL_ID, store_in_s3, save_conversation, collect_feedback, invoke_bedrock_model_streaming
from prompts.prompt_templates import DOC_GENERATION_PROMPT, DOC_SECTION_PROMPTS

# Initialize FastMCP
mcp = FastMCP("Documentation Generator")

@mcp.tool()
def generate_technical_documentation(
    solution_description: str,
    conversation_messages: list[dict] = None,
    conversation_id: str = None,
    documentation_type: str = "comprehensive"
) -> dict:
    """
    Generar documentación técnica completa y profesional para una solución de AWS.
    
    Args:
        solution_description: Descripción de la solución de AWS para documentar
        conversation_messages: Mensajes de conversación anteriores para contexto (opcional)
        conversation_id: ID de la conversación para seguimiento (opcional)
        documentation_type: Tipo de documentación (comprehensive, technical, user, deployment)
    
    Returns:
        Dict con la documentación generada y metadatos
    """
    
    # Initialize defaults
    if conversation_messages is None:
        conversation_messages = []
    
    if conversation_id is None:
        conversation_id = str(uuid.uuid4())
    
    # Prepare messages for the model
    doc_messages = conversation_messages[:]
    
    # Use prompt template
    doc_prompt = DOC_GENERATION_PROMPT.format(
        solution_description=solution_description,
        documentation_type=documentation_type
    )
    
    doc_messages.append({"role": "user", "content": doc_prompt})
    
    try:
        # Generate documentation
        doc_response, stop_reason = invoke_bedrock_model_streaming(doc_messages)
        
        # Store results and collect feedback
        store_in_s3(content=doc_response, content_type='documentation')
        save_conversation(conversation_id, doc_prompt, doc_response)
        collect_feedback(str(uuid.uuid4()), doc_response, "generate_documentation", BEDROCK_MODEL_ID)
        
        return {
            "success": True,
            "content": f"# Technical Documentation Generated\n\n{doc_response}",
            "documentation_type": documentation_type,
            "conversation_id": conversation_id,
            "interaction_entry": {
                "type": "Technical documentation",
                "details": doc_response
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error generating documentation: {str(e)}",
            "conversation_id": conversation_id
        }

@mcp.tool()
def generate_specific_documentation_section(
    solution_description: str,
    section_type: str,
    conversation_messages: list[dict] = None,
    conversation_id: str = None
) -> dict:
    """
    Generar una sección específica de documentación técnica.
    
    Args:
        solution_description: Descripción de la solución de AWS
        section_type: Tipo de sección (architecture, deployment, security, operations, troubleshooting)
        conversation_messages: Mensajes de conversación anteriores para contexto (opcional)
        conversation_id: ID de la conversación para seguimiento (opcional)
    
    Returns:
        Dict con la sección de documentación generada
    """
    
    # Initialize defaults
    if conversation_messages is None:
        conversation_messages = []
    
    if conversation_id is None:
        conversation_id = str(uuid.uuid4())
    
    # Validate section type
    if section_type not in DOC_SECTION_PROMPTS:
        return {
            "success": False,
            "error": f"Section type '{section_type}' not supported. Available: {list(DOC_SECTION_PROMPTS.keys())}",
            "conversation_id": conversation_id
        }
    
    # Prepare messages for the model
    doc_messages = conversation_messages[:]
    doc_prompt = DOC_SECTION_PROMPTS[section_type].format(solution_description=solution_description)
    doc_messages.append({"role": "user", "content": doc_prompt})
    
    try:
        # Generate documentation section
        doc_response, stop_reason = invoke_bedrock_model_streaming(doc_messages)
        
        # Store results and collect feedback
        store_in_s3(content=doc_response, content_type=f'documentation_{section_type}')
        save_conversation(conversation_id, doc_prompt, doc_response)
        collect_feedback(str(uuid.uuid4()), doc_response, f"generate_documentation_{section_type}", BEDROCK_MODEL_ID)
        
        return {
            "success": True,
            "content": f"# {section_type.title()} Documentation\n\n{doc_response}",
            "section_type": section_type,
            "conversation_id": conversation_id,
            "interaction_entry": {
                "type": f"Technical documentation - {section_type}",
                "details": doc_response
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error generating {section_type} documentation: {str(e)}",
            "conversation_id": conversation_id
        }

if __name__ == "__main__":
    mcp.run()