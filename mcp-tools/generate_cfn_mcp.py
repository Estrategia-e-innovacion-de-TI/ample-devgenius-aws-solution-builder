from fastmcp import FastMCP
import uuid
import boto3
import os
from botocore.config import Config
import get_code_from_markdown
from utils import BEDROCK_MODEL_ID, invoke_bedrock_model_streaming, retrieve_environment_variables
from utils import store_in_s3, save_conversation, collect_feedback
from prompts.prompt_templates import CFN_GENERATION_PROMPT

# Initialize FastMCP
mcp = FastMCP("CloudFormation Generator")

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION")
config = Config(read_timeout=1000, retries=(dict(max_attempts=5)))
s3_client = boto3.client('s3', region_name=AWS_REGION)

@mcp.tool()
def generate_cloudformation_template(
    solution_description: str,
    conversation_messages: list[dict] = None,
    conversation_id: str = None
) -> dict:
    """
    Generar plantilla de AWS CloudFormation en YAML para desplegar infraestructura de AWS.
    
    Args:
        solution_description: Descripción de la solución de AWS
        conversation_messages: Mensajes de conversación anteriores para contexto (opcional)
        conversation_id: ID de la conversación para seguimiento (opcional)
    
    Returns:
        Dict con la plantilla generada y URL de despliegue
    """
    
    # Initialize defaults
    if conversation_messages is None:
        conversation_messages = []
    
    if conversation_id is None:
        conversation_id = str(uuid.uuid4())
    
    # Prepare messages for the model
    cfn_messages = conversation_messages[:]
    
    cfn_prompt = CFN_GENERATION_PROMPT.format(solution_description=solution_description)
    
    cfn_messages.append({"role": "user", "content": cfn_prompt})
    
    try:
        # Generate CloudFormation template
        cfn_response, stop_reason = invoke_bedrock_model_streaming(cfn_messages)
        
        # Extract YAML from markdown
        cfn_yaml = get_code_from_markdown.get_code_from_markdown(cfn_response, language="yaml")[0]
        
        # Store results
        store_in_s3(content=cfn_response, content_type='cfn')
        save_conversation(conversation_id, cfn_prompt, cfn_response)
        collect_feedback(str(uuid.uuid4()), cfn_response, "generate_cfn", BEDROCK_MODEL_ID)
        
        # Upload to S3 and generate deployment URL
        S3_BUCKET_NAME = retrieve_environment_variables("S3_BUCKET_NAME")
        object_name = f"{conversation_id}/template.yaml"
        s3_client.put_object(Body=cfn_yaml, Bucket=S3_BUCKET_NAME, Key=object_name)
        template_object_url = f"https://s3.amazonaws.com/{S3_BUCKET_NAME}/{object_name}"
        stack_url = f"https://console.aws.amazon.com/cloudformation/home?region={AWS_REGION}#/stacks/new?stackName=myteststack&templateURL={template_object_url}"
        
        return {
            "success": True,
            "content": f"# AWS CloudFormation Template Generated\n\n{cfn_response}",
            "yaml_template": cfn_yaml,
            "s3_template_url": template_object_url,
            "cloudformation_deploy_url": stack_url,
            "aws_signup_url": "https://signin.aws.amazon.com/signup?request_type=register",
            "conversation_id": conversation_id
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error generating CloudFormation template: {str(e)}",
            "conversation_id": conversation_id
        }

if __name__ == "__main__":
    mcp.run()