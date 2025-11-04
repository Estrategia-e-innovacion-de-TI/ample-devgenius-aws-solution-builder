import uuid
from typing import Optional, Dict, Any, List
from fastmcp import FastMCP
from prompts.prompt_templates import COST_PROMPT

# Inicializar FastMCP
mcp = FastMCP("AWS Cost Estimator")


@mcp.tool()
async def generate_cost_estimate(
    architecture_messages: List[Dict[str, str]],
    model_id: str = "claude-sonnet-4-5-20250929",
    max_tokens: int = 4096
) -> Dict[str, Any]:
    """
    Genera estimaciones de costos mensuales para arquitecturas AWS.
    
    Esta herramienta analiza una descripción de arquitectura AWS y genera
    estimaciones detalladas de costos mensuales para cada servicio utilizado,
    presentadas en formato tabular profesional.
    
    Args:
        architecture_messages: Lista de mensajes con la descripción de arquitectura.
                              Debe incluir mensajes con role='assistant' que contengan
                              la descripción de la arquitectura AWS.
        model_id: ID del modelo LLM a usar (default: Claude Sonnet 4.5)
        max_tokens: Tokens máximos para la respuesta
    
    Returns:
        Dict con:
            - success: bool indicando si la preparación fue exitosa
            - messages: mensajes preparados para invocar al LLM
            - model_id: modelo a utilizar
            - max_tokens: límite de tokens
            - instructions: instrucciones para el cliente MCP
            - error: mensaje de error (si falló)
    
    Example:
        >>> messages = [
        ...     {"role": "assistant", "content": "Arquitectura con EC2, S3, RDS..."}
        ... ]
        >>> result = await generate_cost_estimate(messages)
        >>> # Cliente debe invocar LLM con result["messages"]
    """
    try:
        # Concatenar mensajes de arquitectura
        concatenated_message = ' '.join(
            message['content'] for message in architecture_messages 
            if message.get('role') == 'assistant'
        )
        
        if not concatenated_message:
            return {
                "success": False,
                "error": "No architecture description found in messages with role='assistant'"
            }
        
        # Construir prompt de costos (importar desde prompts si existe)
        cost_prompt = f"""
        Calcula el costo mensual aproximado para la arquitectura generada con base en la siguiente descripción:
        {concatenated_message}
        {COST_PROMPT}
        """
        
        # Preparar mensajes para el LLM
        messages = architecture_messages.copy()
        messages.append({"role": "user", "content": cost_prompt})
        
        return {
            "success": False,
            "error": "LLM invocation must be handled by MCP client",
            "messages": messages,
            "model_id": model_id,
            "max_tokens": max_tokens,
            "instructions": "Client must invoke LLM with these messages and call process_cost_response with the result"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error preparing cost estimation: {str(e)}"
        }


@mcp.tool()
async def process_cost_response(
    llm_response: str,
    normalize_currency: bool = True
) -> Dict[str, Any]:
    """
    Procesa la respuesta del LLM con estimaciones de costos.
    
    Esta herramienta toma la respuesta del modelo y opcionalmente normaliza
    el formato de moneda ($ a USD).
    
    Args:
        llm_response: Respuesta completa del modelo LLM con estimaciones
        normalize_currency: Si se debe convertir $ a USD (default: True)
    
    Returns:
        Dict con:
            - success: bool indicando si fue exitoso
            - cost_estimate: estimación procesada
            - raw_response: respuesta original
            - metadata: información adicional (total estimado, servicios, etc.)
            - error: mensaje de error (si falló)
    
    Example:
        >>> result = await process_cost_response(llm_output)
        >>> if result["success"]:
        ...     print(result["cost_estimate"])
    """
    try:
        processed_response = llm_response
        
        # Normalizar moneda si se solicita
        if normalize_currency:
            processed_response = llm_response.replace("$", "USD ")
        
        # Extraer metadata básica
        metadata = {
            "has_table": "|" in processed_response,
            "line_count": len(processed_response.split("\n")),
            "analysis_id": str(uuid.uuid4())
        }
        
        # Intentar extraer costo total si está presente
        if "Costo Mensual Estimado Total" in processed_response or "Total" in processed_response:
            # Búsqueda simple del total
            lines = processed_response.split("\n")
            for line in lines:
                if "total" in line.lower() and ("USD" in line or "$" in line):
                    metadata["estimated_total_found"] = True
                    break
        
        return {
            "success": True,
            "cost_estimate": processed_response,
            "raw_response": llm_response,
            "metadata": metadata
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing cost response: {str(e)}",
            "raw_response": llm_response
        }


@mcp.tool()
async def refine_cost_estimate(
    current_estimate: str,
    refinement_request: str,
    architecture_context: Optional[str] = None,
    model_id: str = "claude-sonnet-4-5-20250929"
) -> Dict[str, Any]:
    """
    Refina o ajusta una estimación de costos existente.
    
    Args:
        current_estimate: Estimación actual de costos
        refinement_request: Descripción de los ajustes deseados
                           (ej: "Agrega costos de CloudWatch", "Usa instancias reservadas")
        architecture_context: Contexto adicional de arquitectura (opcional)
        model_id: ID del modelo LLM a usar
    
    Returns:
        Dict con instrucciones para que el cliente invoque al LLM
    
    Example:
        >>> result = await refine_cost_estimate(
        ...     current_estimate="...",
        ...     refinement_request="Considera instancias reservadas con 30% descuento"
        ... )
    """
    try:
        context_section = ""
        if architecture_context:
            context_section = f"\n\nContexto adicional de arquitectura:\n{architecture_context}"
        
        refinement_prompt = f"""Tienes la siguiente estimación de costos AWS:

{current_estimate}
{context_section}

El usuario solicita el siguiente ajuste:
{refinement_request}

Por favor, actualiza la estimación de costos incorporando este cambio. Mantén el formato tabular profesional y asegúrate de:
1. Ordenar por costo total descendente
2. Actualizar el costo total final
3. Incluir notas sobre los cambios realizados
4. Mantener la claridad y profesionalismo del formato

Responde con la estimación actualizada en el mismo formato tabular."""

        messages = [
            {"role": "user", "content": refinement_prompt}
        ]
        
        return {
            "success": False,
            "error": "LLM invocation must be handled by MCP client",
            "messages": messages,
            "model_id": model_id,
            "instructions": "Client must invoke LLM and call process_cost_response with the result"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error preparing cost refinement: {str(e)}"
        }


@mcp.tool()
async def compare_cost_scenarios(
    scenario_a_messages: List[Dict[str, str]],
    scenario_b_messages: List[Dict[str, str]],
    comparison_criteria: Optional[str] = None,
    model_id: str = "claude-sonnet-4-5-20250929"
) -> Dict[str, Any]:
    """
    Compara costos entre dos escenarios de arquitectura diferentes.
    
    Args:
        scenario_a_messages: Mensajes con primera arquitectura
        scenario_b_messages: Mensajes con segunda arquitectura
        comparison_criteria: Criterios específicos de comparación (opcional)
        model_id: ID del modelo LLM a usar
    
    Returns:
        Dict con instrucciones para comparación
    
    Example:
        >>> result = await compare_cost_scenarios(
        ...     scenario_a_messages=[...],
        ...     scenario_b_messages=[...],
        ...     comparison_criteria="Enfócate en costos de compute y storage"
        ... )
    """
    try:
        # Extraer descripciones
        scenario_a = ' '.join(
            msg['content'] for msg in scenario_a_messages 
            if msg.get('role') == 'assistant'
        )
        scenario_b = ' '.join(
            msg['content'] for msg in scenario_b_messages 
            if msg.get('role') == 'assistant'
        )
        
        if not scenario_a or not scenario_b:
            return {
                "success": False,
                "error": "Both scenarios must contain assistant messages with architecture descriptions"
            }
        
        criteria_section = ""
        if comparison_criteria:
            criteria_section = f"\n\nCriterios de comparación: {comparison_criteria}"
        
        comparison_prompt = f"""Compara los costos mensuales estimados entre estos dos escenarios de arquitectura AWS:

ESCENARIO A:
{scenario_a}

ESCENARIO B:
{scenario_b}
{criteria_section}

Proporciona:
1. Tabla de costos para cada escenario (formato profesional)
2. Tabla comparativa destacando diferencias clave
3. Análisis de qué escenario es más cost-effective y por qué
4. Recomendaciones de optimización para ambos

Usa precios actuales de AWS y ordena servicios por costo total."""

        messages = [
            {"role": "user", "content": comparison_prompt}
        ]
        
        return {
            "success": False,
            "error": "LLM invocation must be handled by MCP client",
            "messages": messages,
            "model_id": model_id,
            "instructions": "Client must invoke LLM and call process_cost_response with the result"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error preparing cost comparison: {str(e)}"
        }


# Servidor MCP
if __name__ == "__main__":
    mcp.run()