# DevGenius - Generador de Soluciones AWS

DevGenius es una aplicación impulsada por IA que transforma ideas de proyectos en soluciones completas y listas para desplegar en AWS. Utiliza Amazon Bedrock y los modelos de Claude AI para proporcionar diagramas de arquitectura, estimaciones de costos, infraestructura como código y documentación técnica integral.

![Mira el video demo](demo/DevGenius_Demo.gif)

**Construcción Conversacional de Arquitecturas de Solución:**  
DevGenius permite a los clientes diseñar arquitecturas de solución de forma conversacional. Los usuarios pueden crear diagramas de arquitectura (en formato draw.io) y refinarlos interactivamente. Una vez finalizado el diseño, pueden generar automatización de código de extremo a extremo usando CDK o plantillas de CloudFormation, y desplegarlo en su cuenta de AWS con un solo clic. Además, los clientes pueden recibir estimaciones de costos para ejecutar la arquitectura en producción, junto con documentación detallada de la solución.

**Construcción de Arquitecturas desde Dibujos en Pizarra:**  
Para clientes que ya tengan su arquitectura en forma de imagen (por ejemplo, dibujos en pizarra), DevGenius les permite subir la imagen. Una vez cargada, DevGenius analiza la arquitectura y proporciona una explicación detallada. Luego, el cliente puede refinar el diseño de manera conversacional y, una vez finalizado, generar la automatización de código de extremo a extremo con CDK o CloudFormation. También se incluyen estimaciones de costos y documentación integral.

## Características

- **Generación de Arquitecturas de Solución**: Crear arquitecturas AWS basadas en tus requisitos de proyecto  
- **Creación de Diagramas de Arquitectura**: Generar representaciones visuales de tus soluciones en AWS  
- **Infraestructura como Código**: Generar tanto plantillas AWS CDK como CloudFormation  
- **Estimación de Costos**: Obtener desglose detallado de costos para todos los servicios AWS propuestos  
- **Documentación Técnica**: Generar documentación completa de tus soluciones  
- **Análisis de Arquitecturas Existentes**: Subir y analizar diagramas de arquitectura existentes  

## Descripción de la Arquitectura

DevGenius está construido con una arquitectura moderna nativa en la nube:

- **Frontend**: Interfaz basada en Streamlit para interacción intuitiva  
- **Motor de IA**: Amazon Bedrock con modelos Claude AI para generación de soluciones  
- **Base de Conocimiento**: Amazon Bedrock Knowledge Base con fuentes de documentación AWS  
- **Almacenamiento Vectorial**: Amazon OpenSearch Serverless para embeddings vectoriales  
- **Almacenamiento de Datos**:  
  - Amazon S3 para almacenar artefactos generados  
  - DynamoDB para seguimiento de conversaciones y sesiones  
- **Despliegue**:  
  - AWS ECS Fargate para alojamiento de aplicaciones en contenedores  
  - CloudFront para distribución de contenido  
  - Application Load Balancer para gestión de tráfico  
- **Autenticación**: Amazon Cognito para autenticación de usuarios  

## Requisitos Previos

- Cuenta AWS con permisos apropiados  
- AWS CLI configurado con credenciales  
- Python 3.12 o posterior  
- Docker (para compilación de contenedores y desarrollo local)  
- Acceso a modelos Amazon Bedrock (Claude-3-Sonnet/Claude-3-5-Sonnet)  

## Instalación y Configuración

### Desarrollo Local

1. Clona el repositorio:

   ```bash
   git clone https://github.com/aws-samples/sample-devgenius-aws-solution-builder.git devgenius
   cd devgenius

   ```

2. Instala las dependencias requeridas:

   ```bash
   npm install
   ```

3. Configura las variables de entorno necesarias. Reemplaza todos los valores que siguen el patrón <REPLACE_ME_XXX>:

   ```bash
   export AWS_REGION="us-west-2"
   export BEDROCK_AGENT_ID="<REPLACE_ME_BEDROCK_AGENT_ID>"
   export BEDROCK_AGENT_ALIAS_ID="<REPLACE_ME_BEDROCK_AGENT_ALIAS_ID>"
   export S3_BUCKET_NAME="<REPLACE_ME_S3_BUCKET_NAME>"
   export CONVERSATION_TABLE_NAME="<REPLACE_ME_CONVERSATION_TABLE_NAME>"
   export FEEDBACK_TABLE_NAME="<REPLACE_ME_FEEDBACK_TABLE_NAME>"
   export SESSION_TABLE_NAME="<REPLACE_ME_SESSION_TABLE_NAME>"
   ```

4. Ejecuta la aplicación:

   ```bash
   streamlit run chatbot/agent.py
   ```

### Despliegue con Docker

Construye y ejecuta usando Docker después de reemplazar los valores <REPLACE_ME_XXX>:

```bash
cd chatbot
docker build -t devgenius .
docker run -p 8501:8501 \
  -e AWS_REGION="us-west-2" \
  -e BEDROCK_AGENT_ID="<REPLACE_ME_BEDROCK_AGENT_ID>" \
  -e BEDROCK_AGENT_ALIAS_ID="<REPLACE_ME_BEDROCK_AGENT_ALIAS_ID>" \
  -e S3_BUCKET_NAME="<REPLACE_ME_S3_BUCKET_NAME>" \
  -e CONVERSATION_TABLE_NAME="<REPLACE_ME_CONVERSATION_TABLE_NAME>" \
  -e FEEDBACK_TABLE_NAME="<REPLACE_ME_FEEDBACK_TABLE_NAME>" \
  -e SESSION_TABLE_NAME="<REPLACE_ME_SESSION_TABLE_NAME>" \
  devgenius
```

## Despliegue de Infraestructura AWS

DevGenius incluye un stack CDK que despliega toda la infraestructura requerida:

1. Instala la herramienta CDK:

   ```bash
   npm install -g aws-cdk
   ```

2. Desde la raíz del repositorio, instala dependencias:

   ```bash
   npm install
   ```

3. Inicializa la cuenta:

   ```bash
   cdk bootstrap
   ```

4. Despliega el stack:

   ```bash
   cdk deploy --all --context stackName=devgenius
   ```

5. Para destruir la infraestructura cuando ya no sea necesaria:

   ```bash
   cdk destroy --all --context stackName=devgenius
   ```

   Este comando eliminará todos los recursos AWS creados por el stack. Se pedirá confirmación antes de proceder. Nota que esta acción es irreversible y eliminará todos los datos de la aplicación almacenados en los recursos desplegados.

El stack CDK despliega:

VPC con subredes públicas/privadas
   - Servicio ECS Fargate con contenedor Streamlit
   - Application Load Balancer
   - Distribución CloudFront con Lambda@Edge para autenticación
   - Pool de usuarios e identidad Cognito
   - Tablas DynamoDB para seguimiento de conversaciones
   - Bucket S3 para almacenar artefactos generados
   - Agente Bedrock con Base de Conocimiento
   - Colección OpenSearch Serverless para embeddings vectoriales

## Guía de uso

### Autenticación

1. Accede a la URL de la aplicación proporcionada en la salida de CDK (llamada StreamlitUrl)
2. Regístrate (Sign up) para una nueva cuenta en Cognito en la página de inicio o inicia sesión con credenciales existentes
3. Acepta los términos y condiciones

### Construcción de una nueva solución

1. Navega a la pestaña "Build a solution"
2. Selecciona un tema (Data Lake, Log Analytics)
3. Responde las preguntas de descubrimiento sobre tus requisitos
4. Revisa la solución generada
5. Use the option tabs to generate additional assets:
   - Estimación de Costos: desglose detallado de precios
   - Diagrama de Arquitectura: representación visual de la solución
   - Código CDK: infraestructura como código
   - Código CloudFormation: plantillas YAML
   - Documentación Técnica: documentación completa de la solución

### Análisis de Arquitecturas Existentes

1. Navega a la pestaña "Modify your existing architecture"
2. Sube una imagen del diagrama de arquitectura (formato PNG/JPG)
3. La aplicación analizará el diagrama y proporcionará información
4. Usa las pestañas de opciones para generar modificaciones y mejoras

## Componentes Clave

### Agente Bedrock y Base de Conocimiento

DevGenius utiliza Agentes de Amazon Bedrock con una Base de Conocimiento personalizada que contiene documentación, whitepapers y blogs de AWS. El agente está configurado con prompts especializados para generar soluciones AWS siguiendo mejores prácticas.

Fuentes de la base de conocimiento incluyen:

- AWS Well-Architected Analytics Lens
- Whitepapers de AWS sobre arquitecturas de streaming y analítica de datos
- Documentación AWS sobre data lakes
- Publicaciones del blog de arquitectura AWS
- Anuncios de servicios AWS

### Búsqueda Vectorial con OpenSearch Serverless

La información de arquitectura se almacena como embeddings vectoriales en Amazon OpenSearch Serverless, lo que permite búsqueda semántica y recuperación de patrones arquitectónicos relevantes.

### Generación de Infraestructura como Código

La aplicación puede generar tanto plantillas AWS CDK (TypeScript) como CloudFormation (YAML) para desplegar las soluciones propuestas.

## Estructura del Proyecto

```txt
├── chatbot/                      # Code for chatbot
   ├── agent.py                   # Main application entry point
   ├── cost_estimate_widget.py    # Cost estimation functionality
   ├── generate_arch_widget.py    # Architecture diagram generation
   ├── generate_cdk_widget.py     # CDK code generation
   ├── generate_cfn_widget.py     # CloudFormation template generation
   ├── generate_doc_widget.py     # Documentation generation
   ├── layout.py                  # UI layout components
   ├── styles.py                  # UI styling
   ├── utils.py                   # Utility functions
   ├── Dockerfile                 # Container definition
   ├── requirements.txt           # Python dependencies
├── lib/                          # CDK stack definition
   ├── layer/                     # Lambda layer containing dependencies
   ├── lambda/                    # Lambda function code
   └── edge-lambda/               # CloudFront Lambda@Edge function
```

## Seguridad

DevGenius incluye varias características de seguridad:

- Autenticación con Cognito para gestión de usuarios
- CloudFront con Lambda@Edge para validación de solicitudes
- Roles IAM con permisos de menor privilegio
- VPC con grupos de seguridad para aislamiento de red
- Bucket S3 con cifrado para almacenamiento de artefactos
- Tablas DynamoDB con cifrado para almacenamiento de datos


