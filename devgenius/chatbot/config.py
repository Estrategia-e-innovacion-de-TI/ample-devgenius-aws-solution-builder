"""
Configuración del LLM (AWS Bedrock) y parámetros globales.
"""
import os
import boto3
from dotenv import load_dotenv

load_dotenv()

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Bedrock Model Configuration
BEDROCK_MAX_TOKENS = 128000
BEDROCK_TEMPERATURE = 0

# Resolve account ID for inference profile ARN
_sts_client = boto3.client("sts", region_name=AWS_REGION)
ACCOUNT_ID = _sts_client.get_caller_identity()["Account"]

BEDROCK_MODEL_ID = (
    f"arn:aws:bedrock:{AWS_REGION}:{ACCOUNT_ID}"
    f":inference-profile/us.anthropic.claude-sonnet-4-5-20250929-v1:0"
)

# Output directory for generated artifacts (images, diagrams, etc.)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
