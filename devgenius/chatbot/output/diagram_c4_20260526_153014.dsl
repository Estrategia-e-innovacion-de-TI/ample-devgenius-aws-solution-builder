workspace "Sistema de Análisis Inteligente de Logs" {
    model {
        # Personas
        devopsEngineer = person "DevOps Engineer" "Ingeniero que recibe alertas de anomalías y gestiona incidentes"
        dataScientist = person "Data Scientist" "Científico de datos que gestiona modelos ML"
        
        # Sistema fuente
        applicationSystem = softwareSystem "Application System" "Aplicación que genera 5TB/día de logs en formato JSON"
        
        # Sistema principal
        logAnalyticsPlatform = softwareSystem "Log Analytics Platform" "Plataforma de análisis inteligente de logs con ML para predicción de caídas" {
            # Capa de Ingesta
            kinesisStreams = container "Kinesis Data Streams" "Ingesta de logs en tiempo real con múltiples shards (58+ MB/s)" "AWS Kinesis" "streaming"
            
            # Capa de Procesamiento
            lambdaFeatureExtractor = container "Lambda Feature Extractor" "Parsing, normalización y extracción de features en ventanas de 5 min" "AWS Lambda + Python" "compute"
            lambdaScoring = container "Lambda Scoring" "Invoca endpoint ML cada 5 min y evalúa anomaly scores" "AWS Lambda + Python" "compute"
            lambdaAlertHandler = container "Lambda Alert Handler" "Gestiona alertas y envía notificaciones cuando se detectan anomalías" "AWS Lambda + Python" "compute"
            
            # Almacenamiento
            s3DataLake = container "S3 Data Lake" "Almacenamiento particionado por fecha con Intelligent-Tiering" "Amazon S3" "storage"
            
            # Machine Learning
            sagemakerEndpoint = container "SageMaker Endpoint" "Endpoint en tiempo real con Random Cut Forest para detección de anomalías" "Amazon SageMaker" "ml"
            sagemakerTraining = container "SageMaker Training Jobs" "Reentrenamiento semanal/mensual de modelos RCF" "Amazon SageMaker" "ml"
            glueEtl = container "Glue ETL" "Feature engineering batch diario para preparar datasets de entrenamiento" "AWS Glue" "etl"
            
            # Orquestación
            stepFunctions = container "Step Functions" "Orquesta workflow de reentrenamiento semanal" "AWS Step Functions" "orchestration"
            eventBridge = container "EventBridge Scheduler" "Triggers programados para entrenamientos y procesos batch" "Amazon EventBridge" "orchestration"
        }
        
        # Sistemas externos
        sesSystem = softwareSystem "Amazon SES" "Servicio de envío de emails para notificaciones de anomalías"
        cloudWatchSystem = softwareSystem "Amazon CloudWatch" "Monitoreo de métricas en tiempo real y dashboards"
        quickSightSystem = softwareSystem "Amazon QuickSight" "Análisis histórico y visualización de tendencias"
        openSearchSystem = softwareSystem "Amazon OpenSearch" "Búsqueda interactiva de logs (7-30 días)" "optional"
        systemsManagerSystem = softwareSystem "AWS Systems Manager" "Runbooks para respuestas automáticas"
        
        # Relaciones - Personas
        devopsEngineer -> logAnalyticsPlatform "Recibe alertas y monitorea anomalías"
        devopsEngineer -> cloudWatchSystem "Consulta métricas y dashboards"
        devopsEngineer -> openSearchSystem "Busca logs interactivamente"
        dataScientist -> logAnalyticsPlatform "Gestiona modelos y retrain"
        dataScientist -> quickSightSystem "Analiza tendencias históricas"
        
        # Relaciones - Flujo principal tiempo real
        applicationSystem -> kinesisStreams "Envía logs JSON vía Kinesis Agent/SDK" "HTTPS"
        kinesisStreams -> lambdaFeatureExtractor "Trigger con batch de eventos" "Event"
        lambdaFeatureExtractor -> s3DataLake "Almacena logs raw y features agregados" "S3 API"
        lambdaFeatureExtractor -> lambdaScoring "Envía features agregadas cada 5 min" "Invocación"
        lambdaScoring -> sagemakerEndpoint "Invoca para scoring de anomalías" "HTTPS/JSON"
        sagemakerEndpoint -> lambdaScoring "Retorna anomaly score" "Response"
        lambdaScoring -> lambdaAlertHandler "Notifica cuando score > threshold" "Event"
        lambdaAlertHandler -> sesSystem "Envía emails con detalles de anomalías" "SMTP/API"
        lambdaAlertHandler -> systemsManagerSystem "Ejecuta runbooks automáticos" "API"
        
        # Relaciones - Flujo batch y reentrenamiento
        eventBridge -> stepFunctions "Dispara workflow semanal" "Event"
        stepFunctions -> glueEtl "Inicia ETL diario" "API"
        stepFunctions -> sagemakerTraining "Inicia reentrenamiento" "API"
        s3DataLake -> glueEtl "Lee logs históricos" "S3 API"
        glueEtl -> s3DataLake "Escribe training dataset" "S3 API"
        s3DataLake -> sagemakerTraining "Lee training dataset" "S3 API"
        sagemakerTraining -> sagemakerEndpoint "Actualiza modelo en endpoint" "Model Registry"
        
        # Relaciones - Monitoreo y análisis
        kinesisStreams -> cloudWatchSystem "Envía métricas" "CloudWatch API"
        lambdaFeatureExtractor -> cloudWatchSystem "Envía logs y métricas" "CloudWatch API"
        lambdaScoring -> cloudWatchSystem "Envía métricas de scoring" "CloudWatch API"
        sagemakerEndpoint -> cloudWatchSystem "Envía métricas de inferencia" "CloudWatch API"
        s3DataLake -> quickSightSystem "Fuente de datos para análisis" "SPICE"
        lambdaFeatureExtractor -> openSearchSystem "Indexa logs para búsqueda" "HTTPS" "optional"
        
        # Relaciones externas
        sesSystem -> devopsEngineer "Envía alertas por email" "SMTP"
    }
    
    views {
        systemContext logAnalyticsPlatform "SystemContext" {
            include *
            autoLayout
        }
        
        container logAnalyticsPlatform "Containers" {
            include *
            autoLayout
        }
        
        dynamic logAnalyticsPlatform "RealtimeFlow" "Flujo de detección de anomalías en tiempo real" {
            applicationSystem -> kinesisStreams "1. Envía logs JSON"
            kinesisStreams -> lambdaFeatureExtractor "2. Trigger con eventos"
            lambdaFeatureExtractor -> s3DataLake "3. Almacena raw data"
            lambdaFeatureExtractor -> lambdaScoring "4. Envía features (5 min)"
            lambdaScoring -> sagemakerEndpoint "5. Solicita scoring"
            sagemakerEndpoint -> lambdaScoring "6. Retorna anomaly score"
            lambdaScoring -> lambdaAlertHandler "7. Detecta anomalía"
            lambdaAlertHandler -> sesSystem "8. Envía alerta"
            sesSystem -> devopsEngineer "9. Notifica por email"
            autoLayout
        }
        
        dynamic logAnalyticsPlatform "RetrainingFlow" "Flujo de reentrenamiento semanal" {
            eventBridge -> stepFunctions "1. Trigger programado"
            stepFunctions -> glueEtl "2. Inicia ETL"
            s3DataLake -> glueEtl "3. Lee logs históricos"
            glueEtl -> s3DataLake "4. Escribe training set"
            stepFunctions -> sagemakerTraining "5. Inicia training job"
            s3DataLake -> sagemakerTraining "6. Lee training data"
            sagemakerTraining -> sagemakerEndpoint "7. Actualiza modelo"
            autoLayout
        }
        
        styles {
            element "Person" {
                shape person
                background #08427b
                color #ffffff
            }
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "streaming" {
                background #ff6b35
            }
            element "compute" {
                background #f7931e
            }
            element "storage" {
                background #569a31
            }
            element "ml" {
                background #945bb0
            }
            element "etl" {
                background #00a1c9
            }
            element "orchestration" {
                background #e05194
            }
            element "optional" {
                background #999999
            }
        }
        
        theme default
    }
}