import uuid
from typing import Optional, Dict, Any, List
from fastmcp import FastMCP
import get_code_from_markdown
from prompts.prompt_templates import ARCHITECTURE_PROMPT
from utils.utils import convert_xml_to_html

# Inicializar FastMCP
mcp = FastMCP("Architecture Diagram Generator")

@mcp.tool()
async def generate_architecture_diagram(
    solution_description: str,
    previous_messages: Optional[List[Dict[str, str]]] = None,
    model_id: str = "claude-sonnet-4-5-20250929",
    max_tokens: int = 8192,
    enable_reasoning: bool = True
) -> Dict[str, Any]:
    """
    Genera un diagrama de arquitectura AWS en formato draw.io XML.
    
    Esta herramienta genera diagramas de arquitectura profesionales usando
    íconos oficiales de AWS en formato XML compatible con draw.io. El diagrama
    incluye todos los servicios, conexiones, VPCs y mejores prácticas de AWS.
    
    Args:
        solution_description: Descripción detallada de la solución AWS a diagramar
        previous_messages: Mensajes previos de contexto (opcional)
        model_id: ID del modelo LLM a usar (default: Claude Sonnet 4.5)
        max_tokens: Tokens máximos para la respuesta (default: 8192)
        enable_reasoning: Si habilitar razonamiento extendido en el modelo
    
    Returns:
        Dict con:
            - success: bool indicando si fue exitoso
            - messages: lista de mensajes para invocar al LLM
            - model_id: ID del modelo a usar
            - max_tokens: límite de tokens
            - enable_reasoning: si usar razonamiento extendido
            - max_attempts: número máximo de intentos para respuestas largas
            - instructions: instrucciones para el cliente MCP
            - error: mensaje de error (si falló)
    
    Example:
        >>> result = await generate_architecture_diagram(
        ...     "Sistema web escalable con ALB, ECS Fargate, RDS Aurora y ElastiCache"
        ... )
        >>> # El cliente MCP debe invocar al LLM con result["messages"]
        >>> # Puede necesitar múltiples intentos si stop_reason == "max_tokens"
        >>> # Luego llamar a process_architecture_response con la(s) respuesta(s)
    """
    try:
        # Construir mensajes para el LLM
        messages = previous_messages.copy() if previous_messages else []
        
        # Construir prompt usando el template importado
        architecture_prompt = f"""Para la siguiente solución de AWS:

{solution_description}

{ARCHITECTURE_PROMPT}"""
        
        messages.append({"role": "user", "content": architecture_prompt})
        
        # Retornar instrucciones para que el cliente MCP invoque al LLM
        return {
            "success": False,
            "error": "LLM invocation must be handled by MCP client",
            "messages": messages,
            "model_id": model_id,
            "max_tokens": max_tokens,
            "enable_reasoning": enable_reasoning,
            "max_attempts": 4,  # Número máximo de intentos si la respuesta es muy larga
            "instructions": """Client must:
1. Invoke LLM with these messages
2. Check if stop_reason == 'max_tokens'
3. If max_tokens reached and attempt < max_attempts:
   - Call prepare_continuation_prompt with current response
   - Invoke LLM again with continuation messages
   - Append new response to previous responses
4. Once complete (stop_reason != 'max_tokens' or max_attempts reached):
   - Call process_architecture_response with full concatenated response
"""
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error preparing architecture generation: {str(e)}"
        }


@mcp.tool()
async def prepare_continuation_prompt(
    original_prompt: str,
    partial_response: str
) -> Dict[str, Any]:
    """
    Prepara mensajes para continuar una respuesta truncada por max_tokens.
    
    Args:
        original_prompt: El prompt original de arquitectura
        partial_response: La respuesta parcial recibida hasta ahora
    
    Returns:
        Dict con nuevos mensajes para continuar la generación
    """
    try:
        continuation_messages = [
            {"role": "user", "content": original_prompt},
            {"role": "assistant", "content": partial_response},
            {"role": "user", "content": "Continue from where you left off. Complete the XML diagram."}
        ]
        
        return {
            "success": True,
            "messages": continuation_messages
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error preparing continuation: {str(e)}"
        }


@mcp.tool()
async def process_architecture_response(
    llm_response: str,
    convert_to_html: bool = True
) -> Dict[str, Any]:
    """
    Procesa la respuesta del LLM y extrae el XML de draw.io.
    
    Esta herramienta toma la respuesta del modelo LLM (o respuestas concatenadas
    si hubo múltiples intentos), extrae el XML, lo valida y opcionalmente lo
    convierte a HTML para visualización.
    
    Args:
        llm_response: Respuesta completa del modelo LLM (puede ser concatenación)
        convert_to_html: Si convertir el XML a HTML para preview (default: True)
    
    Returns:
        Dict con:
            - success: bool indicando si fue exitoso
            - xml_content: XML de draw.io extraído
            - html_content: HTML para visualización (si convert_to_html=True)
            - validation: resultado de validación del XML
            - raw_response: respuesta original
            - error: mensaje de error (si falló)
    
    Example:
        >>> # Después de una o más invocaciones al LLM
        >>> full_response = "".join(response_array)
        >>> result = await process_architecture_response(full_response)
        >>> if result["success"]:
        ...     xml = result["xml_content"]
        ...     html = result["html_content"]  # Para mostrar en UI
    """
    try:
        # Extraer XML del markdown
        xml_blocks = get_code_from_markdown.get_code_from_markdown(llm_response, language="xml")
        
        if not xml_blocks:
            return {
                "success": False,
                "error": "No XML code block found in response",
                "raw_response": llm_response
            }
        
        # Tomar el primer bloque XML (debería ser el único)
        xml_content = xml_blocks[0]
        
        # Validar estructura básica del XML
        validation = validate_xml_structure(xml_content)
        
        result = {
            "success": validation["valid"],
            "xml_content": xml_content,
            "validation": validation,
            "raw_response": llm_response
        }
        
        # Convertir a HTML si se solicita
        if convert_to_html and validation["valid"]:
            try:
                html_content = convert_xml_to_html(xml_content)
                result["html_content"] = html_content
            except Exception as e:
                result["success"] = False
                result["error"] = f"Failed to convert XML to HTML: {str(e)}"
        
        if not validation["valid"]:
            result["error"] = f"XML validation failed: {validation.get('error', 'Unknown error')}"
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing architecture response: {str(e)}",
            "raw_response": llm_response
        }


def validate_xml_structure(xml_content: str) -> Dict[str, Any]:
    """
    Valida la estructura básica del XML de draw.io.
    
    Args:
        xml_content: Contenido XML a validar
    
    Returns:
        Dict con resultado de validación
    """
    try:
        import re
        
        issues = []
        warnings = []
        
        # Validar estructura básica
        if not xml_content.strip().startswith('<'):
            issues.append("XML does not start with an opening tag")
        
        if not xml_content.strip().endswith('>'):
            issues.append("XML does not end with a closing tag")
        
        # Validar etiquetas balanceadas
        opening_tags = re.findall(r'<(\w+)[^>]*(?<!/)>', xml_content)
        closing_tags = re.findall(r'</(\w+)>', xml_content)
        
        # Contar etiquetas principales
        if 'mxGraphModel' not in xml_content and 'diagram' not in xml_content:
            warnings.append("No mxGraphModel or diagram tag found - might not be valid draw.io format")
        
        # Verificar balance de etiquetas críticas
        critical_tags = ['mxGraphModel', 'root', 'mxCell']
        for tag in critical_tags:
            open_count = len(re.findall(f'<{tag}[^>]*(?<!/)>', xml_content))
            close_count = len(re.findall(f'</{tag}>', xml_content))
            if open_count != close_count:
                issues.append(f"Unbalanced {tag} tags: {open_count} opening, {close_count} closing")
        
        # Verificar presencia de íconos AWS
        if 'aws' not in xml_content.lower() and 'amazon' not in xml_content.lower():
            warnings.append("No AWS icons detected in diagram")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "statistics": {
                "total_lines": len(xml_content.split("\n")),
                "total_tags": len(opening_tags) + len(closing_tags),
                "has_graph_model": 'mxGraphModel' in xml_content,
                "has_cells": 'mxCell' in xml_content
            }
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": f"Validation error: {str(e)}"
        }


@mcp.tool()
async def refine_architecture_diagram(
    current_xml: str,
    refinement_request: str,
    model_id: str = "claude-sonnet-4-5-20250929"
) -> Dict[str, Any]:
    """
    Refina o mejora un diagrama de arquitectura existente.
    
    Args:
        current_xml: XML actual del diagrama draw.io
        refinement_request: Descripción de los cambios deseados
        model_id: ID del modelo LLM a usar
    
    Returns:
        Dict con instrucciones para que el cliente invoque al LLM
    
    Example:
        >>> result = await refine_architecture_diagram(
        ...     current_xml="<mxGraphModel>...</mxGraphModel>",
        ...     refinement_request="Agrega un bucket S3 para almacenar logs"
        ... )
    """
    try:
        refinement_prompt = f"""Tienes el siguiente diagrama de arquitectura AWS en formato draw.io XML:

```xml
{current_xml}
```

El usuario solicita el siguiente refinamiento:
{refinement_request}

Por favor, modifica el XML del diagrama para incorporar este cambio, siguiendo estas reglas:

REGLAS CRÍTICAS:
1. Mantén toda la estructura XML existente
2. Preserva todos los servicios y conexiones existentes a menos que se solicite eliminarlos
3. Usa íconos oficiales de AWS (https://aws.amazon.com/architecture/icons/)
4. Asegúrate de que el nuevo XML sea sintácticamente válido
5. Mantén el diseño limpio y organizado
6. Asegura que las nuevas flechas/conexiones estén correctamente formadas
7. Respeta el espaciado y alineación del diagrama original
8. No rompas la estructura mxGraphModel/root/mxCell

Responde SOLO con el XML actualizado completo en un bloque ```xml```."""

        messages = [
            {"role": "user", "content": refinement_prompt}
        ]
        
        return {
            "success": False,
            "error": "LLM invocation must be handled by MCP client",
            "messages": messages,
            "model_id": model_id,
            "instructions": "Client must invoke LLM and call process_architecture_response with the result"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error preparing refinement: {str(e)}"
        }


@mcp.tool()
async def analyze_architecture_diagram(xml_content: str) -> Dict[str, Any]:
    """
    Analiza un diagrama de arquitectura y extrae información.
    
    Args:
        xml_content: XML del diagrama draw.io a analizar
    
    Returns:
        Dict con análisis de servicios, conexiones y estructura
    
    Example:
        >>> result = await analyze_architecture_diagram(my_xml)
        >>> print(result["services"])
        >>> print(result["summary"])
    """
    try:
        import re
        
        # Detectar servicios AWS mencionados
        aws_services = []
        service_patterns = [
            (r'lambda', 'AWS Lambda'),
            (r's3|bucket', 'Amazon S3'),
            (r'dynamodb|dynamo', 'Amazon DynamoDB'),
            (r'api.?gateway', 'API Gateway'),
            (r'vpc', 'Amazon VPC'),
            (r'ec2', 'Amazon EC2'),
            (r'rds|aurora', 'Amazon RDS'),
            (r'cloudfront', 'Amazon CloudFront'),
            (r'cognito', 'Amazon Cognito'),
            (r'sqs|queue', 'Amazon SQS'),
            (r'sns|topic', 'Amazon SNS'),
            (r'elasticache|redis|memcached', 'Amazon ElastiCache'),
            (r'alb|elb|load.?balancer', 'Elastic Load Balancing'),
            (r'ecs|fargate', 'Amazon ECS'),
            (r'eks|kubernetes', 'Amazon EKS'),
        ]
        
        for pattern, service_name in service_patterns:
            if re.search(pattern, xml_content, re.IGNORECASE):
                aws_services.append(service_name)
        
        # Remover duplicados
        aws_services = list(set(aws_services))
        
        # Contar elementos
        cell_count = len(re.findall(r'<mxCell', xml_content))
        edge_count = len(re.findall(r'edge="1"', xml_content))
        
        # Detectar VPC
        has_vpc = bool(re.search(r'vpc', xml_content, re.IGNORECASE))
        
        analysis = {
            "success": True,
            "services": aws_services,
            "statistics": {
                "total_cells": cell_count,
                "total_connections": edge_count,
                "service_count": len(aws_services),
                "has_vpc": has_vpc,
                "xml_size_bytes": len(xml_content)
            }
        }
        
        # Resumen
        if aws_services:
            analysis["summary"] = f"Architecture diagram contains {len(aws_services)} AWS service(s): {', '.join(aws_services[:5])}"
            if len(aws_services) > 5:
                analysis["summary"] += f" and {len(aws_services) - 5} more"
        else:
            analysis["summary"] = "No AWS services detected in diagram"
        
        return analysis
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error analyzing architecture diagram: {str(e)}"
        }


# Servidor MCP
if __name__ == "__main__":
    # Iniciar servidor MCP
    mcp.run()