workspace "Sistema de Análisis de Adherencia de Documentos con IA" {
    model {
        // Personas
        arquitectoTI = person "Equipo de Arquitectura TI" "Usuarios que evalúan adherencia de documentos a principios organizacionales"
        
        // Sistema Principal
        sistemaAnalisis = softwareSystem "Sistema de Análisis de Adherencia" "Plataforma de análisis de documentos e imágenes con IA para evaluar cumplimiento de principios de arquitectura TI" {
            apiGateway = container "API Gateway" "Expone API REST para carga y consulta de análisis" "Amazon API Gateway"
            lambdaOrquestacion = container "Lambda Orquestación" "Funciones para coordinar procesos de ingesta y almacenamiento" "AWS Lambda"
            stepFunctions = container "Step Functions Workflow" "Orquesta workflow multi-paso de análisis" "AWS Step Functions"
            s3Documentos = container "S3 Documentos a Analizar" "Almacena documentos cargados por usuarios" "Amazon S3"
            s3Referencia = container "S3 Documentos de Referencia" "Almacena políticas y estándares organizacionales" "Amazon S3"
            s3Resultados = container "S3 Resultados" "Almacena reportes de análisis generados" "Amazon S3"
            dynamoDB = container "DynamoDB" "Almacena metadatos, resultados de análisis e histórico" "Amazon DynamoDB"
            quickSight = container "QuickSight Dashboard" "Dashboards de adherencia y métricas" "Amazon QuickSight"
        }
        
        // Sistemas Externos AWS
        textract = softwareSystem "Amazon Textract" "Servicio de extracción de texto de PDF, Word, PowerPoint, Excel e imágenes"
        rekognition = softwareSystem "Amazon Rekognition" "Servicio de análisis de imágenes, detección de logos y objetos"
        comprehend = softwareSystem "Amazon Comprehend" "Servicio de análisis de sentimiento, entidades y temas"
        bedrock = softwareSystem "Amazon Bedrock" "Modelos Claude/Titan para comparación inteligente y scoring de adherencia"
        kendra = softwareSystem "Amazon Kendra" "Búsqueda semántica en documentos de referencia"
        sns = softwareSystem "Amazon SNS" "Servicio de notificaciones para incumplimientos"
        iam = softwareSystem "AWS IAM" "Control de acceso granular"
        kms = softwareSystem "AWS KMS" "Encriptación de datos en reposo y tránsito"
        cloudWatch = softwareSystem "Amazon CloudWatch & CloudTrail" "Monitoreo, logging y auditoría de accesos"
        
        // Relaciones: Persona -> Sistema
        arquitectoTI -> apiGateway "Carga documentos y consulta resultados vía API REST" "HTTPS/JSON"
        arquitectoTI -> quickSight "Consulta dashboards de adherencia" "HTTPS"
        
        // Relaciones: Contenedores dentro del sistema (mismo nivel)
        apiGateway -> lambdaOrquestacion "Invoca funciones" "AWS SDK"
        lambdaOrquestacion -> s3Documentos "Almacena documentos" "AWS SDK"
        lambdaOrquestacion -> stepFunctions "Dispara workflow" "AWS SDK"
        stepFunctions -> s3Documentos "Lee documentos" "AWS SDK"
        stepFunctions -> s3Referencia "Lee políticas y estándares" "AWS SDK"
        stepFunctions -> dynamoDB "Guarda metadatos y resultados" "AWS SDK"
        stepFunctions -> s3Resultados "Almacena reportes" "AWS SDK"
        quickSight -> dynamoDB "Consulta datos para visualización" "AWS SDK"
        quickSight -> s3Resultados "Lee reportes" "AWS SDK"
        
        // Relaciones: Contenedores -> Sistemas Externos
        stepFunctions -> textract "Extrae texto de documentos" "AWS SDK"
        stepFunctions -> rekognition "Analiza imágenes y contenido visual" "AWS SDK"
        stepFunctions -> comprehend "Analiza sentimiento y entidades" "AWS SDK"
        stepFunctions -> bedrock "Genera scoring de adherencia con IA" "AWS SDK"
        stepFunctions -> kendra "Busca en documentos de referencia" "AWS SDK"
        stepFunctions -> sns "Envía notificaciones" "AWS SDK"
        
        lambdaOrquestacion -> iam "Valida permisos" "AWS SDK"
        lambdaOrquestacion -> kms "Encripta datos" "AWS SDK"
        
        s3Documentos -> kms "Encripta en reposo" "AWS SDK"
        s3Referencia -> kms "Encripta en reposo" "AWS SDK"
        s3Resultados -> kms "Encripta en reposo" "AWS SDK"
        dynamoDB -> kms "Encripta en reposo" "AWS SDK"
        
        apiGateway -> iam "Autenticación y autorización" "AWS SDK"
        apiGateway -> cloudWatch "Envía logs y métricas" "AWS SDK"
        lambdaOrquestacion -> cloudWatch "Envía logs y métricas" "AWS SDK"
        stepFunctions -> cloudWatch "Envía logs de ejecución" "AWS SDK"
        
        // Relación: Sistema Externo -> Persona
        sns -> arquitectoTI "Notifica incumplimientos" "Email/SMS"
    }
    
    views {
        systemContext sistemaAnalisis "DiagramaContexto" {
            include *
            autoLayout
        }
        
        container sistemaAnalisis "DiagramaContenedores" {
            include *
            autoLayout
        }
        
        theme default
    }
}