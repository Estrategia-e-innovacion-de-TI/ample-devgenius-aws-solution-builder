# Skill: generate_architecture

## Descripción

Genera un diagrama de arquitectura AWS en formato XML (draw.io) basado en el contexto de la conversación. Exporta archivo `.drawio` y `.html` visualizable en navegador.

## Triggers

- "genera el diagrama de arquitectura"
- "diagrama de arquitectura AWS"
- "genera un diagrama visual de la solución"
- "diagrama draw.io"
- "genera la arquitectura"

## Parámetros

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| conversation_context | str | Resumen completo de la solución/arquitectura discutida en la conversación |

## Ejecución

1. Enviar el contexto de la solución al LLM con el prompt de generación de XML draw.io.
2. Extraer el bloque XML del markdown de la respuesta.
3. Guardar el XML como archivo `.drawio` en `output/`.
4. Convertir el XML a HTML embebible para visualización en navegador.
5. Guardar el HTML en `output/`.
6. Retornar las rutas de ambos archivos.

## Prompt de generación

El prompt instruye al LLM a:
- Crear un XML válido para draw.io con la arquitectura y flujo de datos AWS.
- Usar los íconos de arquitectura más recientes de AWS.
- Asegurar que todos los servicios estén correctamente conectados dentro de un ícono AWS Cloud.
- Desplegar dentro de una VPC cuando corresponda.
- Producir un diagrama limpio, ordenado y legible.

## Configuración del modelo

- Temperature: 0
- Thinking: deshabilitado

## Salida

- `architecture_{timestamp}.drawio` — Diagrama XML editable en draw.io
- `architecture_{timestamp}.html` — Visualización en navegador

## Manejo de errores

- Si no se puede extraer XML del markdown, usa la respuesta completa.
- Si falla la conversión a HTML, solo se reporta el archivo XML.
