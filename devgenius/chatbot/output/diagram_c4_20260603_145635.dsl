workspace "Ecommerce Scalable Multi-Region" {
    model {
        // Personas
        user = person "Usuario" "Cliente que compra productos en la plataforma de ecommerce"
        admin = person "Administrador" "Gestiona productos, pedidos e inventario"
        
        // Sistema Principal
        ecommercePlatform = softwareSystem "Plataforma Ecommerce" "Sistema de comercio electrónico serverless escalable y multi-región" {
            // Frontend
            webFrontend = container "Web Application" "Aplicación Angular para navegadores web" "Angular + S3" {
                tags "Frontend"
            }
            mobileFrontend = container "Mobile Application" "Aplicación móvil nativa" "AWS Amplify" {
                tags "Frontend"
            }
            cloudFront = container "CloudFront CDN" "Distribución global de contenido estático y dinámico" "Amazon CloudFront" {
                tags "CDN"
            }
            
            // Autenticación
            cognitoAuth = container "Authentication Service" "Gestión de usuarios y autenticación con soporte social login" "Amazon Cognito" {
                tags "Authentication"
            }
            
            // API y Backend
            apiGateway = container "API Gateway" "API REST para operaciones de ecommerce" "Amazon API Gateway" {
                tags "API"
            }
            lambdaFunctions = container "Business Logic Functions" "Funciones serverless para productos, pedidos, carrito y pagos" "AWS Lambda" {
                tags "Compute"
            }
            
            // Base de Datos
            dynamoDb = container "Database" "Base de datos NoSQL con Global Tables y replicación multi-región" "Amazon DynamoDB" {
                tags "Database"
            }
            
            // Procesamiento Asíncrono
            sqsQueue = container "Payment Queue" "Cola para procesamiento asíncrono de pagos" "Amazon SQS" {
                tags "Queue"
            }
            eventBridge = container "Event Bus" "Orquestación de eventos de inventario y pedidos" "Amazon EventBridge" {
                tags "Events"
            }
            
            // Búsqueda
            openSearch = container "Search Service" "Motor de búsqueda avanzada de productos con filtros" "Amazon OpenSearch" {
                tags "Search"
            }
            
            // Almacenamiento
            s3Images = container "Image Storage" "Almacenamiento de imágenes de productos" "Amazon S3" {
                tags "Storage"
            }
            
            // Monitoreo
            cloudWatch = container "Monitoring & Logging" "Métricas, logs y trazabilidad de requests" "CloudWatch + X-Ray" {
                tags "Monitoring"
            }
            
            // Seguridad
            secretsManager = container "Secrets Manager" "Almacenamiento seguro de API keys de servicios de pago" "AWS Secrets Manager" {
                tags "Security"
            }
        }
        
        // Sistemas Externos
        stripePayment = softwareSystem "Stripe/PayPal" "Procesador de pagos externo" {
            tags "External"
        }
        snsService = softwareSystem "SNS" "Servicio de notificaciones push móviles" "Amazon SNS" {
            tags "External"
        }
        sesService = softwareSystem "SES" "Servicio de emails transaccionales" "Amazon SES" {
            tags "External"
        }
        
        // Relaciones de Usuario
        user -> ecommercePlatform "Navega, busca productos y realiza compras"
        user -> webFrontend "Accede desde navegador web"
        user -> mobileFrontend "Accede desde dispositivo móvil"
        admin -> ecommercePlatform "Gestiona catálogo e inventario"
        
        // Relaciones Frontend
        webFrontend -> cloudFront "Distribuido a través de"
        mobileFrontend -> cloudFront "Obtiene recursos desde"
        cloudFront -> apiGateway "Enruta peticiones API a"
        cloudFront -> s3Images "Distribuye imágenes desde"
        
        // Relaciones de Autenticación
        webFrontend -> cognitoAuth "Autentica usuarios con"
        mobileFrontend -> cognitoAuth "Autentica usuarios con"
        
        // Relaciones API y Backend
        webFrontend -> apiGateway "Realiza operaciones CRUD mediante"
        mobileFrontend -> apiGateway "Realiza operaciones CRUD mediante"
        apiGateway -> lambdaFunctions "Invoca"
        apiGateway -> cognitoAuth "Valida tokens con"
        
        // Relaciones Lambda Functions
        lambdaFunctions -> dynamoDb "Lee y escribe datos en"
        lambdaFunctions -> openSearch "Consulta búsquedas en"
        lambdaFunctions -> sqsQueue "Envía mensajes de pago a"
        lambdaFunctions -> eventBridge "Publica eventos a"
        lambdaFunctions -> s3Images "Almacena imágenes en"
        lambdaFunctions -> secretsManager "Obtiene credenciales desde"
        lambdaFunctions -> stripePayment "Procesa pagos con"
        lambdaFunctions -> cloudWatch "Envía logs y métricas a"
        
        // Relaciones de Procesamiento
        sqsQueue -> lambdaFunctions "Dispara procesamiento de pagos en"
        dynamoDb -> eventBridge "Streams de cambios a"
        eventBridge -> lambdaFunctions "Dispara actualización de inventario en"
        
        // Relaciones de Notificaciones
        lambdaFunctions -> snsService "Envía notificaciones push mediante"
        lambdaFunctions -> sesService "Envía emails transaccionales mediante"
        snsService -> user "Notifica a"
        sesService -> user "Envía emails a"
        
        // Relaciones de Sistemas Externos
        stripePayment -> lambdaFunctions "Confirma pago a"
        
        // Relaciones de Monitoreo
        apiGateway -> cloudWatch "Registra métricas en"
        dynamoDb -> cloudWatch "Envía métricas a"
        sqsQueue -> cloudWatch "Monitorea colas en"
    }
    
    views {
        systemContext ecommercePlatform "SystemContext" {
            include *
            autoLayout
        }
        
        container ecommercePlatform "Containers" {
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
            element "External" {
                background #999999
                color #ffffff
            }
            element "Frontend" {
                background #FF6B6B
                color #ffffff
            }
            element "CDN" {
                background #4ECDC4
                color #ffffff
            }
            element "Authentication" {
                background #FFE66D
                color #000000
            }
            element "API" {
                background #95E1D3
                color #000000
            }
            element "Compute" {
                background #F38181
                color #ffffff
            }
            element "Database" {
                background #AA96DA
                color #ffffff
            }
            element "Queue" {
                background #FCBAD3
                color #000000
            }
            element "Events" {
                background #A8D8EA
                color #000000
            }
            element "Search" {
                background #FFA500
                color #ffffff
            }
            element "Storage" {
                background #90EE90
                color #000000
            }
            element "Monitoring" {
                background #DDA15E
                color #ffffff
            }
            element "Security" {
                background #BC6C25
                color #ffffff
            }
        }
        
        theme default
    }
}