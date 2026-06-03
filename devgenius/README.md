# ArqGenius - Agente de Arquitectura AWS (CLI)

Agente conversacional de Arquitectura TI potenciado por **AWS Bedrock** (Claude 4.5 Sonnet) orquestado con **LangGraph**. Se ejecuta localmente como aplicación de consola (CLI).

## Arquitectura

```
chatbot/
├── main.py          # Punto de entrada CLI (bucle interactivo)
├── config.py        # Configuración LLM / Bedrock
├── agent.py         # Orquestación LangGraph (agente + memoria)
├── utils.py         # Utilidades compartidas
├── tools/
│   ├── generate_arch.py   # Diagrama de arquitectura (draw.io XML + HTML)
│   ├── generate_cdk.py    # Código AWS CDK (TypeScript)
│   ├── generate_cfn.py    # Plantilla CloudFormation (YAML)
│   ├── generate_doc.py    # Documentación técnica
│   └── dsl_code.py        # Diagrama C4 (DSL + imagen PNG)
└── output/          # Artefactos generados (diagramas, código, docs)
```

## Requisitos Previos

1. **Python 3.12+**
2. **Credenciales AWS** configuradas (`~/.aws/credentials` o variables de entorno `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`)
3. **Acceso a Amazon Bedrock** con el modelo `us.anthropic.claude-sonnet-4-5-20250929-v1:0` habilitado en tu cuenta/región.

## Instalación

Este proyecto usa [uv](https://docs.astral.sh/uv/) como gestor de paquetes y entornos virtuales.

```bash
# Clonar el repositorio
git clone <repo-url>
cd ample-devgenius-aws-solution-builder

# Instalar uv (si no lo tienes)
# Windows (PowerShell):
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# Linux/Mac:
# curl -LsSf https://astral.sh/uv/install.sh | sh

# Crear entorno virtual e instalar dependencias (un solo comando)
uv sync --native-tls

# Configurar variables de entorno
cp .env
# Editar .env con tu región AWS
```

> **Nota:** Si estás detrás de un proxy corporativo, usa siempre `--native-tls` para que uv utilice los certificados del sistema.

## Uso

```bash
uv run python -m chatbot.main

# O usando el entry point directamente:
uv run devgenius
```

### Comandos en la CLI

| Comando  | Descripción                          |
|----------|--------------------------------------|
| `/new`   | Iniciar nueva conversación           |
| `/tools` | Listar herramientas disponibles      |
| `/exit`  | Salir de la aplicación               |

### Ejemplo de uso

```
Tú: Necesito un data lake empresarial con ingesta en tiempo real y batch

DevGenius: Para diseñar tu data lake, necesito entender algunos requisitos...
    - ¿Cuál es el volumen estimado de datos diarios?
    - ¿Qué fuentes de datos tienes (bases de datos, streams, APIs)?
    ...

Tú: Genera el diagrama de arquitectura

DevGenius: Diagrama de arquitectura generado.
    - Archivo XML: chatbot/output/architecture_20260526_143022.drawio
    - Archivo HTML: chatbot/output/architecture_20260526_143022.html
```

## Herramientas del Agente

Las 5 herramientas comparten el contexto de la conversación actual:

| Herramienta | Descripción | Salida |
|-------------|-------------|--------|
| `generate_architecture` | Diagrama de arquitectura AWS | `.drawio` + `.html` |
| `generate_cdk` | Código CDK TypeScript | `.md` |
| `generate_cfn` | Plantilla CloudFormation | `.yaml` + `.md` |
| `generate_doc` | Documentación técnica | `.md` |
| `generate_dsl` | Diagrama C4 Structurizr | `.dsl` + `.png` |

Los artefactos se exportan a `chatbot/output/`.

## Configuración

| Variable | Descripción | Default |
|----------|-------------|---------|
| `AWS_REGION` | Región de AWS para Bedrock | `us-east-1` |

El modelo se configura en `chatbot/config.py`. Por defecto usa el inference profile de Claude 4.5 Sonnet con Cross-Region Inference.
