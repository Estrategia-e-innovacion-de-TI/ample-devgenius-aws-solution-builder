# Skill: generate_cfn

## Descripción

Genera una plantilla de AWS CloudFormation en YAML para desplegar la solución discutida en la conversación. Exporta tanto el template YAML como documentación en markdown.

## Triggers

- "genera la plantilla CloudFormation"
- "genera CloudFormation"
- "genera un template YAML"
- "genera CFN"
- "plantilla de despliegue CloudFormation"

## Parámetros

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| conversation_context | str | Resumen completo de la solución/arquitectura discutida en la conversación |

## Ejecución

1. Enviar el contexto de la solución al LLM con el prompt de generación CloudFormation.
2. Extraer el bloque YAML del markdown de la respuesta.
3. Guardar el YAML como archivo `.yaml` en `output/`.
4. Guardar la respuesta completa como `.md` en `output/`.
5. Retornar las rutas y el contenido.

## Prompt de generación

El prompt instruye al LLM a:
- Generar una plantilla CloudFormation en YAML para automatizar el despliegue.
- Proporcionar código fuente real para todos los jobs.
- Aprovisionar todos los recursos y componentes.
- Generar comandos de ejemplo para desplegar la plantilla.

## Configuración del modelo

- Temperature: 0
- Thinking: deshabilitado

## Salida

- `cloudformation_{timestamp}.yaml` — Template CloudFormation
- `cloudformation_{timestamp}.md` — Documentación completa

## Manejo de errores

- Si no se puede extraer YAML del markdown, usa la respuesta completa.
