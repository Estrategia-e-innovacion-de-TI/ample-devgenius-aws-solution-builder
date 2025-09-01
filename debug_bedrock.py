#!/usr/bin/env python3
"""
Script para verificar completamente qué identidad AWS está usando tu aplicación
"""
import boto3
import os
from botocore.exceptions import ClientError

def analyze_aws_identity():
    print("=== ANÁLISIS DE IDENTIDAD AWS ===\n")
    
    # 1. Verificar variables de entorno
    print("1. Variables de entorno AWS:")
    aws_env_vars = [
        'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN',
        'AWS_PROFILE', 'AWS_DEFAULT_REGION', 'AWS_REGION', 
        'AWS_CREDENTIAL_FILE', 'AWS_CONFIG_FILE'
    ]
    
    for var in aws_env_vars:
        value = os.getenv(var)
        if value:
            if 'KEY' in var or 'TOKEN' in var:
                print(f"   {var}: {value[:10]}..." if len(value) > 10 else f"   {var}: {value}")
            else:
                print(f"   {var}: {value}")
        else:
            print(f"   {var}: Not set")
    
    # 2. Verificar session boto3
    print(f"\n2. Información de sesión boto3:")
    try:
        session = boto3.Session()
        
        # Credentials
        credentials = session.get_credentials()
        if credentials:
            print(f"   Access Key: {credentials.access_key[:10]}...")
            print(f"   Method: {credentials.method if hasattr(credentials, 'method') else 'Unknown'}")
        
        # Profile
        profile = session.profile_name
        print(f"   Profile: {profile}")
        
        # Region
        region = session.region_name
        print(f"   Region: {region}")
        
    except Exception as e:
        print(f"   ❌ Error obteniendo sesión: {e}")
    
    # 3. Verificar identidad STS
    print(f"\n3. Identidad STS:")
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        print(f"   Account ID: {identity['Account']}")
        print(f"   User ID: {identity['UserId']}")
        print(f"   ARN: {identity['Arn']}")
        
        # Extraer tipo de identidad
        arn = identity['Arn']
        if ':user/' in arn:
            identity_type = "IAM User"
            identity_name = arn.split(':user/')[1]
        elif ':role/' in arn:
            identity_type = "IAM Role"
            identity_name = arn.split(':role/')[1]
        elif ':assumed-role/' in arn:
            identity_type = "Assumed Role"
            role_info = arn.split(':assumed-role/')[1]
            identity_name = role_info.split('/')[0]
        else:
            identity_type = "Unknown"
            identity_name = "Unknown"
            
        print(f"   Type: {identity_type}")
        print(f"   Name: {identity_name}")
        
    except Exception as e:
        print(f"   ❌ Error obteniendo identidad: {e}")
    
    # 4. Verificar permisos específicos de Bedrock
    print(f"\n4. Permisos de Bedrock:")
    try:
        bedrock = boto3.client('bedrock', region_name='us-east-1')
        
        # Test 1: List models
        try:
            models = bedrock.list_foundation_models()
            print(f"   ✅ list_foundation_models: OK ({len(models['modelSummaries'])} models)")
        except ClientError as e:
            print(f"   ❌ list_foundation_models: {e.response['Error']['Code']}")
        
        # Test 2: Get specific model
        try:
            model = bedrock.get_foundation_model(modelIdentifier='anthropic.claude-3-5-sonnet-20241022-v2:0')
            print(f"   ✅ get_foundation_model: OK")
        except ClientError as e:
            print(f"   ❌ get_foundation_model: {e.response['Error']['Code']}")
            
    except Exception as e:
        print(f"   ❌ Error creando cliente Bedrock: {e}")
    
    # 5. Test invoke
    print(f"\n5. Test de invocación:")
    try:
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Test con modelo que funciona
        test_models = [
            'anthropic.claude-3-5-sonnet-20240620-v1:0',
            'us.anthropic.claude-3-5-sonnet-20241022-v2:0'
        ]
        
        for model_id in test_models:
            try:
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 5,
                    "messages": [{"role": "user", "content": "Hi"}]
                }
                
                response = bedrock_runtime.invoke_model(
                    body=json.dumps(body),
                    modelId=model_id,
                    contentType='application/json',
                    accept='application/json'
                )
                
                print(f"   ✅ {model_id}: OK")
                break
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                print(f"   ❌ {model_id}: {error_code}")
                
    except Exception as e:
        print(f"   ❌ Error en test de invocación: {e}")

if __name__ == "__main__":
    import json
    analyze_aws_identity()