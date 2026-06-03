# Skill: generate_dsl

## Descripción

Genera un diagrama de arquitectura de software en modelo C4 usando Structurizr DSL y lo convierte a imagen PNG. Usa esta skill cuando el usuario pida un diagrama modelo C4 o un diagrama DSL de la solución.

## Triggers

- "genera un diagrama C4"
- "diagrama DSL"
- "diagrama Structurizr"
- "genera diagrama modelo C4"
- "diagrama de contenedores"

## Parámetros

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| conversation_context | str | Resumen completo de la solución/arquitectura discutida en la conversación |

## Ejecución

1. Enviar el contexto de la solución al LLM con el prompt de generación DSL.
2. Extraer el bloque DSL del markdown de la respuesta.
3. Limpiar y validar el código DSL (función `clean_dsl_code`).
4. Guardar el DSL como archivo `.dsl` en `output/`.
5. Convertir el DSL a imagen PNG usando Kroki (función `structurizr_to_diagram`).
6. Guardar la imagen PNG en `output/`.
7. Retornar las rutas de ambos archivos.

## Prompt de generación

El prompt instruye al LLM a:
- Generar código Structurizr DSL válido con workspace, model y views.
- Usar camelCase para variables.
- NUNCA crear relaciones padre-hijo.
- Todas las relaciones entre elementos del mismo nivel o diferentes sistemas.
- Incluir vistas systemContext y container.

## Configuración del modelo

- Temperature: 1
- Thinking: habilitado (budget: 4096 tokens)

## Salida

- `diagram_c4_{timestamp}.dsl` — Código DSL
- `diagram_c4_{timestamp}.png` — Imagen del diagrama

## Manejo de errores

- Si no se puede extraer DSL del markdown, limpia la respuesta completa.
- Si Kroki falla, reporta advertencia pero entrega el DSL.
