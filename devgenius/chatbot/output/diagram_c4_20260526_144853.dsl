workspace "Sistema de Clasificación de Imágenes con IA en AWS" {
    model {
        // Personas
        imageUploader = person "Usuario Cargador" "Usuario que carga imágenes al sistema para su clasificación"
        apiConsumer = person "Usuario Consultor" "Usuario que consulta resultados de clasificación vía API o dashboard"
        
        // Sistema principal
        imageClassificationSystem = softwareSystem "Sistema de Clasificación de Imágenes" "Procesa y clasifica imágenes usando IA, almacena resultados y expone datos vía API y dashboard" {
            s3SourceBucket = container "S3 Source Bucket" "Almacena imágenes entrantes sin procesar" "Amazon S3"
            s3ProcessedBucket = container "S3 Processed Bucket" "Almacena imágenes procesadas organizadas por categoría" "Amazon S3"
            processingLambda = container "Lambda de Procesamiento" "Orquesta la clasificación de imágenes invocando servicios de IA" "AWS Lambda (Python/Node.js)"
            dynamoDb = container "DynamoDB" "Almacena metadatos y resultados de clasificación de imágenes" "Amazon DynamoDB"
            apiGateway = container "API Gateway" "Expone API REST para consultar resultados de clasificación" "Amazon API Gateway"
            apiLambda = container "Lambda de API" "Funciones backend para endpoints de consulta de resultados" "AWS Lambda (Python/Node.js)"
            quickSight = container "Dashboard QuickSight" "Dashboard interactivo para visualizar métricas y resultados" "Amazon QuickSight"
        }
        
        // Sistemas externos
        rekognitionService = softwareSystem "Amazon Rekognition" "Servicio de IA pre-entrenado para detección de objetos y análisis de documentos (>90% precisión)" "AWS Managed Service"
        textractService = softwareSystem "Amazon Textract" "Servicio para extracción avanzada de texto en documentos" "AWS Managed Service"
        cloudWatchService = softwareSystem "Amazon CloudWatch" "Servicio de monitoreo, logs, métricas y alarmas" "AWS Managed Service"
        xRayService = softwareSystem "AWS X-Ray" "Servicio de trazabilidad y análisis de rendimiento del procesamiento" "AWS Managed Service"
        
        // Relaciones principales
        imageUploader -> s3SourceBucket "Sube imágenes para clasificar" "HTTPS/S3 API"
        apiConsumer -> apiGateway "Consulta resultados de clasificación" "HTTPS/REST"
        apiConsumer -> quickSight "Visualiza métricas y resultados" "HTTPS"
        
        // Flujo de procesamiento
        s3SourceBucket -> processingLambda "Dispara evento cuando se carga imagen" "S3 Event Notification"
        processingLambda -> rekognitionService "Invoca para clasificar imagen" "AWS SDK"
        processingLambda -> textractService "Invoca para extraer texto (opcional)" "AWS SDK"
        processingLambda -> dynamoDb "Guarda resultados y metadatos" "AWS SDK"
        processingLambda -> s3ProcessedBucket "Mueve imagen procesada a carpeta clasificada" "AWS SDK"
        
        // Flujo de API
        apiGateway -> apiLambda "Enruta peticiones REST" "AWS Integration"
        apiLambda -> dynamoDb "Consulta resultados de clasificación" "AWS SDK"
        
        // Visualización
        quickSight -> dynamoDb "Lee datos para dashboard" "Direct Query/SPICE"
        
        // Monitoreo
        processingLambda -> cloudWatchService "Envía logs y métricas" "CloudWatch Logs"
        apiLambda -> cloudWatchService "Envía logs y métricas" "CloudWatch Logs"
        processingLambda -> xRayService "Envía trazas de ejecución" "X-Ray SDK"
        apiLambda -> xRayService "Envía trazas de ejecución" "X-Ray SDK"
    }
    
    views {
        systemContext imageClassificationSystem "SystemContext" {
            include *
            autoLayout
        }
        
        container imageClassificationSystem "Containers" {
            include *
            autoLayout
        }
        
        styles {
            element "Person" {
                shape Person
                background #08427B
                color #ffffff
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "AWS Managed Service" {
                background #FF9900
                color #ffffff
            }
        }
        
        theme default
    }
}