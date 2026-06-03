# Skill: generate_c1_context

## Descripción

Genera un diagrama C4 Nivel C1 (System Context Diagram) usando Structurizr DSL y lo convierte a imagen PNG. Muestra ÚNICAMENTE el sistema principal, actores de negocio y sistemas externos de negocio.

## Triggers

- "genera un diagrama C1"
- "diagrama de contexto del sistema"
- "diagrama System Context"
- "genera el contexto del sistema"
- "quién usa el sistema"
- "diagrama de alto nivel"

## Parámetros

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| conversation_context | str | Resumen completo de la solución/arquitectura discutida en la conversación |

## Ejecución

1. Enviar el contexto de la solución al LLM con el prompt C1 especializado.
2. Extraer el bloque DSL del markdown de la respuesta.
3. Limpiar y validar el código DSL (función `clean_dsl_code`).
4. Guardar el DSL como archivo `.dsl` en `output/`.
5. Convertir el DSL a imagen PNG usando Kroki (función `structurizr_to_diagram`).
6. Guardar la imagen PNG en `output/`.
7. Retornar las rutas de ambos archivos.

## Regla del C1

El System Context SOLO responde a la pregunta:
> "¿Quién usa el sistema y con qué sistemas externos se comunica?"

El foco está en **actores y sistemas externos de negocio**, NO en tecnología de infraestructura.

### Debe modelar:
- Sistema principal (una sola caja negra).
- Personas/actores de negocio.
- Sistemas externos de negocio.
- Relaciones con intención de negocio.

### NO debe modelar:
- Servicios AWS/cloud (S3, Lambda, DynamoDB, etc.).
- Contenedores internos.
- Componentes o clases.
- Protocolos técnicos.
- Bases de datos internas, APIs internas, microservicios.

## Configuración del modelo

- Temperature: 1
- Thinking: habilitado (budget: 4096 tokens)

## Salida

- `diagram_c1_context_{timestamp}.dsl` — Código DSL
- `diagram_c1_context_{timestamp}.png` — Imagen del diagrama

## Manejo de errores

- Si no se puede extraer DSL del markdown, limpia la respuesta completa.
- Si Kroki falla, reporta advertencia pero entrega el DSL.
