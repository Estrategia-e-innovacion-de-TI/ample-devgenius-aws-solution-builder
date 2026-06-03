workspace "Static Website System Context" {
    model {
        // Personas/Actores de negocio
        endUser = person "End User" "Website visitor who accesses and views the static website content through their browser"
        administrator = person "Administrator" "Manages and updates the website content"

        // Sistema principal (una sola caja)
        staticWebsiteSystem = softwareSystem "Static Website System" "Hosts and delivers static website content globally with high availability and performance"

        // Relaciones con intención de negocio
        endUser -> staticWebsiteSystem "Visits and views website content"
        administrator -> staticWebsiteSystem "Uploads and updates website content"
    }
    
    views {
        systemContext staticWebsiteSystem "SystemContext" {
            include *
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
        }
    }
}