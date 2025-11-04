DSL_PROMPT = """Genera un diagrama de arquitectura de software en código Structurizr DSL para la solución dada siguiendo este proceso de razonamiento paso a paso:

        Paso 1: Analiza el alcance y el contexto del sistema
        Primero, lee y comprende cuidadosamente los requisitos del sistema. Pregúntate:
        - ¿Cuál es el propósito principal de este sistema?
        - ¿Quiénes son los usuarios/actores principales?
        - ¿Cuáles son los procesos o flujos de trabajo clave del negocio?
        - ¿Cuál es el nivel del modelo C4 apropiado para este diagrama (System Context, Container, Component o Code)?

        Paso 2: Identifica los elementos centrales
        Con base en tu análisis, identifica y clasifica los elementos:
        - Personas: ¿Quién interactúa con el sistema? (usuarios finales, administradores, sistemas externos que actúan como usuarios)
        - Sistemas de software: ¿Cuáles son los principales sistemas de software involucrados? (sistemas internos, externos, legados)
        - Contenedores: ¿Cuáles son las unidades desplegables/ejecutables? (aplicaciones web, APIs, bases de datos, colas de mensajes, etc.)
        - Componentes: ¿Cuáles son los principales bloques estructurales dentro de los contenedores? (controladores, servicios, repositorios, etc.)

        Paso 3: Determina relaciones y flujo de datos
        Para cada elemento identificado, piensa en:
        - ¿Con qué interactúa este elemento?
        - ¿Qué tipo de interacción es? (usa, envía datos a, se autentica con, etc.)
        - ¿Qué protocolos o tecnologías se usan? (HTTP, HTTPS, SQL, colas de mensajes, etc.)
        - ¿Cuál es la dirección del flujo de datos?

        Paso 4: Considera servicios en la nube y dependencias externas
        Evalúa si el sistema incluye:
        - Servicios en la nube (AWS S3, Azure Functions, Google Cloud Storage, etc.)
        - APIs o servicios de terceros
        - Bases de datos o fuentes de datos externas
        - Servicios de monitoreo y registro (logging)

        Paso 5: Estructura y organiza
        Planifica la disposición y organización:
        - Agrupa lógicamente los elementos relacionados
        - Considera las relaciones jerárquicas (los sistemas contienen contenedores, los contenedores contienen componentes)
        - Piensa en el flujo visual y la legibilidad del diagrama

        Paso 6: Genera el código DSL
        Ahora genera el código DSL siguiendo estas REGLAS CRÍTICAS:

        REGLAS CRÍTICAS PARA UN DSL VÁLIDO:
        1. Responde solo con código DSL en markdown (```dsl).
        2. Usa EXACTAMENTE los mismos nombres de variables de forma consistente en todo el código; nunca cambies un nombre de variable una vez declarado.
        3. NUNCA crees relaciones entre elementos padre e hijo (por ejemplo, un softwareSystem no puede tener una relación con sus propios contenedores).
        4. Todas las relaciones deben ser entre elementos del MISMO nivel jerárquico o entre diferentes sistemas/contenedores.
        5. Cada elemento debe estar debidamente declarado antes de ser referenciado en relaciones.
        6. Usa una convención de nombres consistente (camelCase) para todas las variables.
        7. Incluye siempre la estructura de workspace, model y views.

        Plantilla de estructura DSL:
        <example>
        workspace "Workspace Name" {
        model {
        // Personas
        variableName = person "Display Name" "Description"
            // Sistemas externos
            externalSystem = softwareSystem "External System Name" "Description" "External"
            
            // Sistema de software principal
            mainSystem = softwareSystem "Main System Name" "Description" {
                // Contenedores dentro del sistema
                containerName = container "Container Display Name" "Description" "Technology"
            }
            
            // Relaciones: SOLO entre sistemas/contenedores diferentes; NUNCA padre-hijo
            variableName -> mainSystem "Relationship description"
            mainSystem -> externalSystem "Relationship description"
            // Para relaciones entre contenedores, usa directamente las variables de contenedor
            containerName -> externalSystem "Relationship description"
        }

        views {
            systemContext mainSystem {
                include *
                autoLayout
            }
            
            container mainSystem {
                include *
                autoLayout
            }
        }
        }
        </example>

        LISTA DE VERIFICACIÓN antes de generar:
        - [ ] Todos los nombres de variables son consistentes (sin errores tipográficos o variaciones)
        - [ ] No hay relaciones entre sistemas padre y sus contenedores hijos
        - [ ] Todas las variables referenciadas están correctamente declaradas
        - [ ] Sintaxis DSL correcta con llaves y estructura adecuadas
        - [ ] Etiquetas de tecnología entre corchetes cuando sea aplicable

        ERRORES COMUNES A EVITAR:
        1. ❌ `mainSystem -> containerInsideMainSystem` (relación padre-hijo)
        2. ❌ Usar nombres de variables diferentes para el mismo elemento
        3. ❌ Falta de declaraciones antes de usar variables en relaciones
        4. ❌ Sintaxis incorrecta en definiciones de contenedor o componente

        ✅ PATRONES CORRECTOS:
        1. `person -> softwareSystem`
        2. `softwareSystem -> externalSystem`
        3. `container -> container` (cuando están en sistemas diferentes)
        4. `container -> externalSystem`

        Ahora aplica este proceso de razonamiento para generar tu código en Structurizr DSL, asegurando que se sigan estrictamente todas las reglas."""

ARCHITECTURE_PROMPT = """
        Genera un diagrama de arquitectura y flujo de datos en AWS para la solución dada, aplicando las buenas prácticas de AWS. Sigue estos pasos:
        1. Crea un archivo XML adecuado para draw.io que capture la arquitectura y el flujo de datos.
        2. Haz referencia a los íconos de arquitectura más recientes de AWS aquí: https://aws.amazon.com/architecture/icons/. Usa SIEMPRE los íconos de AWS más recientes para generar la arquitectura.
        3. Responde únicamente con el XML en formato markdown—sin texto adicional.
        4. Asegura que el XML esté completo, con todas las etiquetas de apertura y cierre correctamente formadas.
        5. Confirma que todos los servicios/íconos de AWS estén correctamente conectados y que estén contenidos dentro de un ícono de AWS Cloud, desplegados dentro de una VPC cuando corresponda.
        6. Elimina espacios en blanco innecesarios para optimizar el tamaño y minimizar los tokens de salida.
        7. Usa íconos válidos de arquitectura de AWS para representar los servicios; evita imágenes aleatorias.
        8. Asegúrate de que el diagrama de arquitectura esté claramente definido, ordenado y muy legible. El flujo debe ser visualmente limpio, con todas las flechas correctamente conectadas sin superposiciones. Asegúrate de que los íconos de servicios de AWS estén alineados sin chocar con flechas u otros elementos. Si se incluyen servicios no-AWS como bases de datos on-premise, servidores o sistemas externos, utiliza íconos genéricos apropiados de draw.io para representarlos. El diagrama final debe lucir pulido, profesional y fácil de entender de un vistazo.
        9. Crea un diagrama de arquitectura claramente estructurado y de alta legibilidad. Organiza todos los íconos de servicios AWS y los componentes no-AWS (usa íconos genéricos de draw.io para servidores on-premise, bases de datos, etc.) de forma limpia, visualmente alineada y con espaciado adecuado. Asegura que las flechas sean rectas, no se solapen ni se enreden, y que indiquen el flujo sin cruzar los íconos de servicio. Mantén suficiente separación entre los elementos para evitar saturación. El diagrama en conjunto debe verse profesional, pulido, y el flujo de datos debe ser inmediatamente comprensible.
        10. El XML final debe ser sintácticamente correcto y cubrir todos los componentes de la solución dada.
        """

CDK_PROMPT = """
        Genera un script de CDK en TypeScript para automatizar y desplegar los recursos necesarios de AWS.
        Proporciona el código fuente real para todos los trabajos cuando corresponda.
        El código CDK debe aprovisionar todos los recursos y componentes sin restricciones de versión.
        Si se necesita código en Python, genera un ejemplo "Hello, World!".
        Al final, genera comandos de ejemplo para desplegar el código CDK.
        """


CFN_PROMPT = """
        Para la siguiente solución: {solution_description}
        
        Genera una plantilla de CloudFormation en YAML para automatizar el despliegue de recursos de AWS.
        Proporciona el código fuente real para todos los jobs cuando corresponda.
        La plantilla de CloudFormation debe aprovisionar todos los recursos y componentes.
        Si se necesita código en Python, genera un ejemplo "Hello, World!".
        Al final, genera comandos de ejemplo para desplegar la plantilla de CloudFormation.
        """


DOC_GENERATION_PROMPT = """
        Para la siguiente solución: {solution_description}

        Genera una documentación técnica completa y profesional que incluya una tabla de contenidos, 
        para la arquitectura especificada. Expande todos los temas de la tabla de contenidos para 
        crear una documentación técnica profesional integral de tipo: {documentation_type}.

        La documentación debe incluir:
        1. Resumen ejecutivo
        2. Arquitectura del sistema
        3. Componentes y servicios
        4. Flujos de datos
        5. Configuración y despliegue
        6. Seguridad y cumplimiento
        7. Operaciones y mantenimiento
        8. Troubleshooting
        9. Anexos técnicos
        """


DOC_SECTION_PROMPTS = {
    "architecture": """
        Para la siguiente solución: {solution_description}
        
        Genera una sección de documentación de arquitectura que incluya:
        1. Diagrama de arquitectura conceptual
        2. Descripción de componentes principales
        3. Flujo de datos y comunicación entre servicios
        4. Patrones de arquitectura utilizados
        5. Decisiones de diseño y justificaciones
        """,
    "deployment": """
        Para la siguiente solución: {solution_description}
        
        Genera una sección de documentación de despliegue que incluya:
        1. Prerrequisitos del sistema
        2. Pasos detallados de instalación/despliegue
        3. Configuración de variables de entorno
        4. Validación post-despliegue
        5. Rollback procedures
        """,
    "security": """
        Para la siguiente solución: {solution_description}
        
        Genera una sección de documentación de seguridad que incluya:
        1. Modelo de seguridad y amenazas
        2. Configuraciones de IAM y permisos
        3. Cifrado de datos en tránsito y reposo
        4. Auditoría y logging de seguridad
        5. Mejores prácticas de seguridad
        """,
    "operations": """
        Para la siguiente solución: {solution_description}
        
        Genera una sección de documentación operacional que incluya:
        1. Monitoreo y alertas
        2. Procedimientos de mantenimiento
        3. Backup y recovery
        4. Escalabilidad y performance tuning
        5. Runbooks operacionales
        """,
    "troubleshooting": """
        Para la siguiente solución: {solution_description}
        
        Genera una sección de documentación de troubleshooting que incluya:
        1. Problemas comunes y soluciones
        2. Logs importantes y su ubicación
        3. Herramientas de diagnóstico
        4. Procedimientos de escalación
        5. FAQ técnico
        """
}

COST_PROMPT = """
Usa https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/price-changes.html para obtener los precios más recientes.
        Proporciona un resumen breve en formato tabular para facilitar la comprensión: nombre del servicio, configuración, precio y costo total.
        Ordena los servicios por el **costo total** en orden descendente al mostrar la tabla.
        El formato tabular debe verse **muy profesional y legible**, con una estructura clara y fácil de interpretar.
        Asegúrate de que los servicios estén ordenados por **Costo Total** de mayor a menor para resaltar los más costosos primero.
        Usa el siguiente ejemplo como referencia para generar los detalles de precios en formato tabular.

        <example>
        Con base en la arquitectura descrita y utilizando la información de precios más reciente de AWS, aquí tienes una estimación aproximada de los costos mensuales para la solución de data lake empresarial. Ten en cuenta que estas son estimaciones y los costos reales pueden variar según el uso, la transferencia de datos y otros factores.

        | Nombre del Servicio | Configuración | Precio (por unidad) | Costo Mensual Estimado |
        |---------------------|---------------|---------------------|-------------------------|
        | Amazon ECS (Fargate) | 2 tareas, 0.25 vCPU, 0.5 GB RAM, corriendo 24/7 | $0.04048 por hora | $59.50 |
        | Amazon OpenSearch | 1 instancia t3.small.search, 10 GB EBS | $0.036 por hora + $0.10 por GB-mes | $27.40 |
        | Amazon S3 | 100 GB almacenamiento, 100 GB transferencia de datos | $0.023 por GB-mes + $0.09 por GB transferido | $11.30 |
        | Amazon CloudFront | 100 GB transferencia de datos, 1M solicitudes | $0.085 por GB + $0.0075 por 10,000 solicitudes | $9.25 |
        | Application Load Balancer | 1 ALB, corriendo 24/7 | $0.0225 por hora + $0.008 por LCU-hora | $16.74 |
        | Amazon DynamoDB | 25 GB almacenamiento, 1M escrituras, 1M lecturas | $0.25 por GB-mes + $1.25 por millón de escrituras + $0.25 por millón de lecturas | $7.75 |
        | AWS Lambda | 1M invocaciones, 128 MB memoria, 100ms duración promedio | $0.20 por 1M solicitudes + $0.0000166667 por GB-segundo | $0.41 |
        | Amazon CloudWatch | 5 GB logs ingeridos, 5 métricas personalizadas | $0.50 por GB ingerido + $0.30 por métrica al mes | $4.00 |
        | Amazon VPC | 1 NAT Gateway, corriendo 24/7 | $0.045 por hora + $0.045 por GB procesado | $33.48 |
        | **Costo Mensual Estimado Total** | | | $169.83 |

        Ten en cuenta:
        1. Estas estimaciones suponen un uso moderado y pueden variar según la carga real de trabajo.
        2. Los costos de transferencia de datos entre servicios dentro de la misma región no están incluidos, ya que normalmente son gratuitos.
        3. Los costos de AWS CDK, CloudFormation e IAM no están incluidos ya que generalmente son servicios gratuitos.
        4. Los costos de Bedrock Agent y el modelo Claude no están incluidos ya que la información de precios de estos servicios no estaba disponible al momento de esta estimación.
        5. Los costos reales pueden ser menores con instancias reservadas, savings plans u otros descuentos disponibles en tu cuenta de AWS.
        </example>
        """