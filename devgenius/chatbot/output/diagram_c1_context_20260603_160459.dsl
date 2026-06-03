workspace "Sistema de Análisis Inteligente de Logs Bancarios" {
    model {
        // Personas/Actores de negocio
        operationsEngineer = person "Ingeniero de Operaciones" "Monitorea la salud de las aplicaciones y responde a alertas del sistema"
        securityAnalyst = person "Analista de Seguridad" "Investiga anomalías y posibles incidentes de seguridad detectados"
        itManager = person "Gerente de TI" "Visualiza métricas y KPIs ejecutivos sobre el estado de las aplicaciones"
        systemAdmin = person "Administrador del Sistema" "Configura reglas de alertas y mantiene la plataforma"

        // Sistema principal (una sola caja)
        logIntelligencePlatform = softwareSystem "Log Intelligence Platform" "Procesa y analiza logs de aplicaciones bancarias en tiempo real usando IA para detectar anomalías, predecir caídas y generar alertas"

        // Sistemas externos de NEGOCIO
        bankingApplicationServers = softwareSystem "Servidores de Aplicaciones Bancarias" "Sistemas de core banking, APIs y canales digitales que generan logs operacionales" "Existing System"
        notificationSystem = softwareSystem "Sistema de Notificaciones Corporativo" "Distribuye alertas y notificaciones a través de email, SMS y Slack" "Existing System"
        siemSystem = softwareSystem "SIEM Corporativo" "Sistema de gestión de información y eventos de seguridad empresarial" "Existing System"
        ticketingSystem = softwareSystem "Sistema de Ticketing" "Plataforma de gestión de incidentes y solicitudes (ServiceNow/Jira)" "Existing System"

        // Relaciones con intención de negocio
        operationsEngineer -> logIntelligencePlatform "Monitorea la salud de aplicaciones, visualiza dashboards y responde a alertas"
        securityAnalyst -> logIntelligencePlatform "Investiga anomalías de seguridad y analiza eventos sospechosos"
        itManager -> logIntelligencePlatform "Consulta métricas ejecutivas y KPIs de disponibilidad"
        systemAdmin -> logIntelligencePlatform "Configura reglas de detección, umbrales de alertas y parámetros del sistema"
        
        bankingApplicationServers -> logIntelligencePlatform "Envía logs operacionales en streaming para análisis en tiempo real"
        logIntelligencePlatform -> notificationSystem "Envía alertas de anomalías y predicciones de caídas"
        logIntelligencePlatform -> siemSystem "Envía eventos de seguridad detectados para correlación e investigación"
        logIntelligencePlatform -> ticketingSystem "Crea tickets automáticos para incidentes críticos"
    }
    
    views {
        systemContext logIntelligencePlatform "SystemContext" {
            include *
            autoLayout
        }
        
        styles {
            element "Person" {
                shape Person
                background #08427b
                color #ffffff
            }
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "Existing System" {
                background #999999
                color #ffffff
            }
        }
    }
}