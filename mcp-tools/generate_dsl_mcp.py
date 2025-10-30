import uuid
import asyncio
from typing import Optional, Dict, Any, List, Tuple
from fastmcp import FastMCP
import get_code_from_markdown
from prompts.prompt_templates import DSL_PROMPT
from utils.utils import extract_dsl_from_markdown, clean_dsl_code, validate_dsl_structure     

# Inicializar FastMCP
mcp = FastMCP("DSL Architecture Generator")

@mcp.tool()
async def generate_dsl_code(
    architecture_description: str,
    previous_messages: Optional[List[Dict[str, str]]] = None,
    model_id: str = "claude-sonnet-4-5-20250929",
    max_tokens: int = 4096
) -> Dict[str, Any]:
    """
    Genera código Structurizr DSL a partir de una descripción de arquitectura.
    
    Esta herramienta genera código DSL (Domain Specific Language) de Structurizr
    para crear diagramas C4 de arquitectura de software. El código generado puede
    ser utilizado directamente en Struajajcturizr para visualizar la arquitectura.
    
    Args:
        architecture_description: Descripción detallada de la arquitectura a modelar
        previous_messages: Mensajes previos de contexto (opcional)
        model_id: ID del modelo LLM a usar (default: Claude Sonnet 4.5)
        max_tokens: Tokens máximos para la respuesta
    
    Returns:
        Dict con:
            - success: bool indicando si fue exitoso
            - dsl_code: código DSL generado y limpio (si exitoso)
            - raw_response: respuesta completa del modelo
            - validation: resultado de validación estructural
            - error: mensaje de error (si falló)
    
    Example:
        >>> result = await generate_dsl_code(
        ...     "Sistema de e-commerce con frontend React, API REST, y base de datos PostgreSQL"
        ... )
        >>> if result["success"]:
        ...     print(result["dsl_code"])
    """
    try:
        # Construir mensajes para el LLM
        messages = previous_messages.copy() if previous_messages else []
        
        # Agregar el contexto de arquitectura y el prompt DSL
        user_message = f"""Descripción de la arquitectura:
{architecture_description}

{DSL_PROMPT}"""
        
        messages.append({"role": "user", "content": user_message})
        
        # NOTA: Aquí el cliente MCP debe invocar al LLM
        # La implementación real dependerá de cómo el cliente MCP
        # se comunique con el modelo (ej: API de Bedrock, Claude API, etc.)
        
        # Por ahora, retornamos la estructura esperada para que el cliente
        # complete la invocación
        return {
            "success": False,
            "error": "LLM invocation must be handled by MCP client",
            "messages": messages,
            "model_id": model_id,
            "max_tokens": max_tokens,
            "instructions": "Client must invoke LLM with these messages and call process_dsl_response with the result"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error preparing DSL generation: {str(e)}"
        }


@mcp.tool()
async def process_dsl_response(
    llm_response: str,
    validate: bool = True
) -> Dict[str, Any]:
    """
    Procesa la respuesta del LLM y extrae código DSL válido.
    
    Esta herramienta toma la respuesta cruda del modelo LLM, extrae el código DSL,
    lo limpia y opcionalmente lo valida.
    
    Args:
        llm_response: Respuesta completa del modelo LLM
        validate: Si se debe validar la estructura del DSL (default: True)
    
    Returns:
        Dict con:
            - success: bool indicando si fue exitoso
            - dsl_code: código DSL extraído y limpio
            - validation: Dict con resultado de validación (si validate=True)
            - raw_response: respuesta original
            - error: mensaje de error (si falló)
    
    Example:
        >>> llm_output = "```dsl\\nworkspace {...}\\n```"
        >>> result = await process_dsl_response(llm_output)
        >>> if result["success"]:
        ...     dsl_code = result["dsl_code"]
    """
    try:
        # Extraer código DSL del markdown
        raw_dsl = extract_dsl_from_markdown(llm_response)
        
        # Limpiar código
        cleaned_dsl = clean_dsl_code(raw_dsl)
        
        result = {
            "success": True,
            "dsl_code": cleaned_dsl,
            "raw_response": llm_response
        }
        
        # Validar estructura si se solicita
        if validate:
            is_valid, error_msg = validate_dsl_structure(cleaned_dsl)
            result["validation"] = {
                "is_valid": is_valid,
                "error": error_msg
            }
            
            if not is_valid:
                result["success"] = False
                result["error"] = f"DSL validation failed: {error_msg}"
        
        return result
        
    except ValueError as e:
        return {
            "success": False,
            "error": str(e),
            "raw_response": llm_response
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing DSL response: {str(e)}",
            "raw_response": llm_response
        }


@mcp.tool()
async def validate_dsl(dsl_code: str) -> Dict[str, Any]:
    """
    Valida código Structurizr DSL existente.
    
    Verifica que el código DSL tenga la estructura correcta y elementos requeridos.
    
    Args:
        dsl_code: Código DSL a validar
    
    Returns:
        Dict con:
            - valid: bool indicando si el DSL es válido
            - cleaned_code: código DSL limpio
            - errors: lista de errores encontrados
            - warnings: lista de advertencias (opcional)
    
    Example:
        >>> dsl = "workspace {...}"
        >>> result = await validate_dsl(dsl)
        >>> if result["valid"]:
        ...     print("DSL is valid!")
    """
    try:
        # Limpiar código
        cleaned = clean_dsl_code(dsl_code)
        
        # Validar estructura
        is_valid, error_msg = validate_dsl_structure(cleaned)
        
        result = {
            "valid": is_valid,
            "cleaned_code": cleaned,
            "errors": [error_msg] if error_msg else []
        }
        
        # Advertencias adicionales
        warnings = []
        if "autoLayout" not in cleaned:
            warnings.append("Consider adding 'autoLayout' to views for better diagram layout")
        
        if warnings:
            result["warnings"] = warnings
        
        return result
        
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Validation error: {str(e)}"]
        }


@mcp.tool()
async def refine_dsl(
    current_dsl: str,
    refinement_request: str,
    model_id: str = "claude-sonnet-4-5-20250929"
) -> Dict[str, Any]:
    """
    Refina o mejora código DSL existente según una solicitud.
    
    Args:
        current_dsl: Código DSL actual
        refinement_request: Descripción de los cambios deseados
        model_id: ID del modelo LLM a usar
    
    Returns:
        Dict con instrucciones para que el cliente invoque al LLM
    
    Example:
        >>> result = await refine_dsl(
        ...     current_dsl="workspace {...}",
        ...     refinement_request="Agrega un componente de caché Redis"
        ... )
    """
    try:
        refinement_prompt = f"""Tienes el siguiente código Structurizr DSL:

```dsl
{current_dsl}
```

El usuario solicita el siguiente refinamiento:
{refinement_request}

Por favor, modifica el código DSL para incorporar este cambio, manteniendo toda la estructura existente y siguiendo las mejores prácticas de Structurizr DSL.

REGLAS CRÍTICAS:
1. Mantén todos los elementos existentes a menos que el usuario solicite eliminarlos
2. Asegúrate de que los nombres de variables sean consistentes
3. No crees relaciones padre-hijo inválidas
4. Mantén la sintaxis correcta del DSL

Responde SOLO con el código DSL actualizado en un bloque de markdown ```dsl```."""

        messages = [
            {"role": "user", "content": refinement_prompt}
        ]
        
        return {
            "success": False,
            "error": "LLM invocation must be handled by MCP client",
            "messages": messages,
            "model_id": model_id,
            "instructions": "Client must invoke LLM and call process_dsl_response with the result"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error preparing refinement: {str(e)}"
        }


@mcp.tool()
async def explain_dsl(dsl_code: str) -> Dict[str, Any]:
    """
    Analiza y explica la estructura de un código DSL.
    
    Args:
        dsl_code: Código DSL a analizar
    
    Returns:
        Dict con análisis de elementos, relaciones y estructura
    
    Example:
        >>> result = await explain_dsl(my_dsl_code)
        >>> print(result["summary"])
    """
    try:
        cleaned = clean_dsl_code(dsl_code)
        
        # Análisis básico
        analysis = {
            "success": True,
            "elements": {
                "has_workspace": "workspace" in cleaned.lower(),
                "has_model": "model" in cleaned.lower(),
                "has_views": "views" in cleaned.lower(),
                "has_persons": "person" in cleaned.lower(),
                "has_systems": "softwareSystem" in cleaned.lower(),
                "has_containers": "container" in cleaned.lower(),
                "has_components": "component" in cleaned.lower()
            },
            "statistics": {
                "total_lines": len(cleaned.split("\n")),
                "brace_pairs": cleaned.count("{"),
                "relationship_count": cleaned.count("->")
            }
        }
        
        # Resumen
        element_types = [k.replace("has_", "") for k, v in analysis["elements"].items() if v]
        analysis["summary"] = f"DSL contains: {', '.join(element_types)}"
        
        return analysis
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error analyzing DSL: {str(e)}"
        }


# Servidor MCP
if __name__ == "__main__":
    # Iniciar servidor MCP
    mcp.run()