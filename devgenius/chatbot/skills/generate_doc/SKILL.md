# Skill: generate_doc

## Descripción

Genera documentación técnica completa y profesional para la solución discutida en la conversación. Incluye tabla de contenidos expandida con todos los temas desarrollados.

## Triggers

- "genera la documentación"
- "genera documentación técnica"
- "documenta la solución"
- "genera un documento técnico"
- "documentación de arquitectura"

## Parámetros

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| conversation_context | str | Resumen completo de la solución/arquitectura discutida en la conversación |

## Ejecución

1. Enviar el contexto de la solución al LLM con el prompt de documentación.
2. Recibir la documentación completa con tabla de contenidos expandida.
3. Guardar como archivo `.md` en `output/`.
4. Retornar la ruta y el contenido.

## Prompt de generación

El prompt instruye al LLM a:
- Generar documentación técnica completa y profesional.
- Incluir tabla de contenidos.
- Expandir todos los temas de la tabla de contenidos.

## Configuración del modelo

- Temperature: 0
- Thinking: deshabilitado

## Salida

- `documentation_{timestamp}.md` — Documentación técnica completa

## Manejo de errores

- La respuesta se guarda directamente como markdown.
