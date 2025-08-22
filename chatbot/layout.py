import streamlit as st
import uuid


def login_page():
    # Customer login form as sidebar and enable session tabs only when the username is entered
    if 'acknowledged' not in st.session_state:
        st.session_state.acknowledged = False

    with st.sidebar:
        logo_col, _ = st.columns([30, 1])

        with logo_col:
            st.title("🧠 DevGenius ARQ")
            st.title("Confirmar")

            acknowledged = st.checkbox(
                "Reconozco que he leído la cláusula de exención de responsabilidad y acepto los términos y condiciones",
                key="acknowledged",
                label_visibility="visible"
            )

            submit = st.button(
                "Construyamos soluciones de Arquitectura",
                disabled=not (acknowledged)
            )

            if submit:
                st.session_state.conversation_id = str(uuid.uuid4())
                st.session_state.user_authenticated = True
                st.rerun()

    # Description and Disclaimer
    # Main page content
    st.markdown("<h1 style='text-align: center;'>Bienvenido a DevGenius ARQ</h1>", unsafe_allow_html=True)

    # Description section
    st.header("Description")
    st.write("""
    DevGenius es un asistente impulsado por IA para la arquitectura de soluciones, diseñado para agilizar y mejorar tu proceso de desarrollo en la nube. 
    Esta plataforma te permite diseñar arquitecturas adaptadas a tus requisitos específicos, asegurando que tu infraestructura en la nube se alinee con los objetivos de tu proyecto. 

    DevGenius permite generar infraestructura como código de manera fluida utilizando herramientas como AWS CDK y AWS CloudFormation, lo que permite un despliegue más rápido y una gestión más sencilla de los recursos en la nube. 
    También proporciona estimaciones aproximadas de costos para los recursos de AWS, ayudando a optimizar el presupuesto y tomar decisiones informadas. 
    Además, DevGenius se adhiere a las prácticas del marco Well-Architected de AWS, garantizando que las soluciones sean seguras, confiables y operativamente sobresalientes. 
    """)  # noqa

    # Add some space between sections
    st.markdown("---")

    # Disclaimer section
    st.header("Disclaimers")
    st.write("""
    - Contenido generado por IA: La aplicación DevGenius utiliza modelos de Claude a través de Bedrock para generar respuestas. 
      Aunque nos esforzamos por ofrecer precisión, la información proporcionada puede no estar siempre completa, actualizada o libre de errores.

    - No sustituye el asesoramiento profesional: Las respuestas generadas por DevGenius no deben considerarse asesoramiento profesional, legal, financiero ni especializado. 
      Siempre consulta con profesionales de arquitectura para obtener orientación específica en estas áreas.

    - Posibles sesgos: A pesar de nuestros mejores esfuerzos por minimizarlos, la IA puede reflejar inadvertidamente sesgos presentes en sus datos de entrenamiento o en su diseño algorítmico.

    - Privacidad y uso de datos: Las interacciones de los usuarios con DevGenius pueden registrarse y analizarse con fines de mejora.

    - Sin garantía de disponibilidad o rendimiento: No garantizamos el acceso ininterrumpido al chatbot ni un funcionamiento libre de errores.

    - Limitación de responsabilidad: DevGenius no es responsable de daños o pérdidas que resulten del uso o la dependencia de la información proporcionada.

    - Responsabilidad del usuario: Los usuarios son responsables de evaluar la pertinencia y precisión de las respuestas de DevGenius para sus necesidades y circunstancias específicas.

    - Propiedad intelectual: Las respuestas del chatbot no deben usarse para infringir derechos de propiedad intelectual.

    - Actualizaciones del descargo de responsabilidad: Este descargo puede actualizarse periódicamente. Por favor, revísalo con regularidad para conocer posibles cambios.

    - Las soluciones proporcionadas son recomendaciones basadas en patrones arquitectónicos comunes.
    - Todo código generado debe revisarse antes de su implementación.
    - Las implicaciones de costos deben evaluarse antes de aplicar cualquier solución.
    - Esta herramienta está pensada para asistir en el diseño de arquitecturas, pero no reemplaza una planificación ni pruebas adecuadas.

    Al utilizar DevGenius, reconoces que has leído, comprendido y aceptado este descargo de responsabilidad.
    """)  # noqa

    # Optional: Add styling for better visual hierarchy
    st.markdown("""
        <style>
        .main h1 {
            color: #2E4B7C;
        }
        .main h2 {
            color: #4A4A4A;
            margin-top: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)


def welcome_sidebar():
    logo_col, _ = st.columns([3, 1])

    with logo_col:
        # st.image("images/DevGenius.JPG", width=150)
        st.title("DevGenius ARQ")
    # Add a horizontal line for visual separation
        st.divider()
        # Add custom CSS for button styling and text handling
        st.markdown("""
            <style>
            .stButton button {
                background-color: #4CAF50; /* Blue background color */
                color: black; /* Black text for contrast */
                font-size: 18px; /* Set font size */
                padding: 20px 50px; /* Add padding for larger button */
                border-radius: 8px; /* Rounded corners */
                width: auto; /* Let the width adjust based on the text */
                text-align: center; /* Center the text inside the button */
                white-space: nowrap; /* Prevent text from wrapping */
                font-weight: bold; /* Make the text bold */
                display: inline-block; /* Ensure the button is inline-block */
            }
            </style>
        """, unsafe_allow_html=True)

        if st.button("Nueva sesión", use_container_width=True):
            st.session_state.user_authenticated = False
            st.session_state.messages = []
            st.session_state.mod_messages = []
            st.rerun()
        
        st.divider()
    # Bottom divider and session ID
    # st.divider()
    # st.write(f"SessionID: {st.session_state.conversation_id}")
    # Add the CSS style
    st.markdown("""
        <style>
            .small-font {
                font-size: 12px;
                color: #666;
                margin: 0;
            }
        </style>
    """, unsafe_allow_html=True)

    # Use the class
    st.markdown(f"""
        <p class='small-font'>
            SessionID: {st.session_state.conversation_id}
        </p>
    """, unsafe_allow_html=True)


def create_tabs():
    """Create and return the Streamlit tabs."""
    # tabs = st.tabs(["Build a solution", "Modify your existing architecture", "Modify AWS solutions"])
    tabs = st.tabs(["Construye una solución", "Modifica una arquitectura existente"])
    return tabs


def create_option_tabs():
    """Create and return the Streamlit tabs for the various options supported by DevGenius."""
    tabs = st.tabs([
    "Estimación de costos", 
    "Diagrama de arquitectura", 
    "CDK code", 
    "CloudFormation code", 
    "Documentación técnica",
    "Código DSL"])  # noqa
    return tabs
