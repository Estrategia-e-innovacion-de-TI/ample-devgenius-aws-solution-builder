import uuid
import get_code_from_markdown
import streamlit as st
from utils import BEDROCK_MODEL_ID
from utils import store_in_s3
from utils import save_conversation
from utils import collect_feedback
from utils import continuation_prompt
from utils import convert_xml_to_html
from utils import invoke_bedrock_model_streaming


@st.fragment
def generate_arch(arch_messages):

    arch_messages = arch_messages[:]

    # Retain messages and previous insights in the chat section
    if 'arch_messages' not in st.session_state:
        st.session_state.arch_messages = []

    # Create the radio button for cost estimate selection
    if 'arch_user_select' not in st.session_state:
        st.session_state.arch_user_select = False  # Initialize the value if it doesn't exist

    left, middle, right = st.columns([3, 1, 0.5])

    with left:
        st.markdown(
            "<div style='font-size: 18px'><b>Usa la casilla de verificación de abajo para generar una representación visual de la solución propuesta.</b></div>",  # noqa
            unsafe_allow_html=True)
        st.divider()
        st.markdown("<div class=stButton gen-style'>", unsafe_allow_html=True)
        select_arch = st.checkbox(
            "Check this box to generate architecture",
            key="arch"
        )
        # Only update the session state when the checkbox value changes
        if select_arch != st.session_state.arch_user_select:
            st.session_state.arch_user_select = select_arch
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        if st.session_state.arch_user_select:
            st.markdown("<div class=stButton gen-style'>", unsafe_allow_html=True)
            if st.button(label="⟳ Retry", key="retry", type="secondary"):
                st.session_state.arch_user_select = True  # Probably redundant
            st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.arch_user_select:
        architecture_prompt = """
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
 

        st.session_state.arch_messages.append({"role": "user", "content": architecture_prompt})
        arch_messages.append({"role": "user", "content": architecture_prompt})

        max_attempts = 4
        full_response_array = []
        full_response = ""

        for attempt in range(max_attempts):
            arch_gen_response, stop_reason = invoke_bedrock_model_streaming(arch_messages, enable_reasoning=True)
            # full_response += arch_gen_response
            full_response_array.append(arch_gen_response)

            if stop_reason != "max_tokens":
                break

            if attempt == 0:
                full_response = ''.join(str(x) for x in full_response_array)
                arch_messages = continuation_prompt(architecture_prompt, full_response)

        if attempt == max_attempts - 1:
            st.error("Reached maximum number of attempts. Final result is incomplete. Please try again.")

        try:
            full_response = ''.join(str(x) for x in full_response_array)
            arch_content_xml = get_code_from_markdown.get_code_from_markdown(full_response, language="xml")[0]
            arch_content_html = convert_xml_to_html(arch_content_xml)
            st.session_state.arch_messages.append({"role": "assistant", "content": "XML"})

            with st.container():
                st.components.v1.html(arch_content_html, scrolling=True, height=350)

            st.session_state.interaction.append({"type": "Solution Architecture", "details": full_response})
            store_in_s3(content=full_response, content_type='architecture')
            save_conversation(st.session_state['conversation_id'], architecture_prompt, full_response)
            collect_feedback(str(uuid.uuid4()), arch_content_xml, "generate_architecture", BEDROCK_MODEL_ID)

        except Exception as e:
            st.error("Internal error occurred. Please try again.")
            print(f"Error occurred when generating architecture: {str(e)}")
            # Removing last element from list so we can retry request by hitting "No" and "Yes"
            del st.session_state.arch_messages[-1]
            del arch_messages[-1]
