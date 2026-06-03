# Skill: generate_cdk

## Descripción

Genera código de infraestructura como código (IaC) usando AWS CDK en TypeScript para desplegar la solución discutida en la conversación.

## Triggers

- "genera el código CDK"
- "genera CDK en TypeScript"
- "genera infraestructura como código"
- "CDK para desplegar"
- "código de despliegue CDK"

## Parámetros

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| conversation_context | str | Resumen completo de la solución/arquitectura discutida en la conversación |

## Ejecución

1. Enviar el contexto de la solución al LLM con el prompt de generación CDK.
2. Recibir la respuesta completa con el código CDK y explicaciones.
3. Guardar la respuesta como archivo `.md` en `output/`.
4. Retornar la ruta del archivo y el contenido.

## Prompt de generación

El prompt instruye al LLM a:
- Generar un script CDK en TypeScript para automatizar el despliegue de recursos AWS.
- Proporcionar código fuente real para todos los jobs.
- Aprovisionar todos los recursos y componentes sin restricciones de versión.
- Generar comandos de ejemplo para desplegar.

## Configuración del modelo

- Temperature: 0
- Thinking: deshabilitado

## Salida

- `cdk_stack_{timestamp}.md` — Código CDK con documentación

## Manejo de errores

- La respuesta completa se guarda directamente como markdown.
