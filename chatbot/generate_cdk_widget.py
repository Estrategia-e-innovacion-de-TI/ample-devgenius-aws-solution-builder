import streamlit as st
from utils import BEDROCK_MODEL_ID
from utils import store_in_s3
from utils import save_conversation
from utils import collect_feedback
from utils import invoke_bedrock_model_streaming
import uuid


# Generate CDK
@st.fragment
def generate_cdk(cdk_messages):

    cdk_messages = cdk_messages[:]

    # Retain messages and previous insights in the chat section
    if 'cdk_messages' not in st.session_state:
        st.session_state.cdk_messages = []

    # Create the radio button for cost estimate selection
    if 'cdk_user_select' not in st.session_state:
        st.session_state.cdk_user_select = False  # Initialize the value if it doesn't exist

    left, middle, right = st.columns([3, 1, 0.5])

    with left:
        st.markdown(
            "<div style='font-size: 18px'><b>Usa la casilla de verificación de abajo para generar código AWS CDK como IaaC para la solución propuesta.</b></div>",  # noqa
            unsafe_allow_html=True)
        st.divider()
        st.markdown("<div class=stButton gen-style'>", unsafe_allow_html=True)
        select_cdk = st.checkbox(
            "Check this box to generate AWS CDK code ",
            key="cdk",
            help="AWS CDK enables you to define and provision AWS infrastructure using familiar programming languages"
        )
        # Only update the session state when the checkbox value changes
        if select_cdk != st.session_state.cdk_user_select:
            st.session_state.cdk_user_select = select_cdk
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        if st.session_state.cdk_user_select:
            st.markdown("<div class=stButton gen-style'>", unsafe_allow_html=True)
            if st.button(label="⟳ Retry", key="retry-cdk", type="secondary"):
                st.session_state.cdk_user_select = True  # Probably redundant
            st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.cdk_user_select:
        cdk_prompt1 = """
        Para la solución dada, genera un script de CDK en TypeScript para automatizar y desplegar los recursos necesarios de AWS.
        Proporciona el código fuente real para todos los trabajos cuando corresponda.
        El código CDK debe aprovisionar todos los recursos y componentes sin restricciones de versión.
        Si se necesita código en Python, genera un ejemplo "Hello, World!".
        Al final, genera comandos de ejemplo para desplegar el código CDK.
        """


        # Append the prompt to the session state and messages
        st.session_state.cdk_messages.append({"role": "user", "content": cdk_prompt1})
        cdk_messages.append({"role": "user", "content": cdk_prompt1})

        # Invoke the Bedrock model to get the CDK response
        cdk_response, stop_reason = invoke_bedrock_model_streaming(cdk_messages)
        st.session_state.cdk_messages.append({"role": "assistant", "content": cdk_response})

        # Display the CDK response
        with st.container(height=350):
            st.markdown(cdk_response)

        st.session_state.interaction.append({"type": "CDK Template", "details": cdk_response})
        store_in_s3(content=cdk_response, content_type='cdk')
        save_conversation(st.session_state['conversation_id'], cdk_prompt1, cdk_response)
        collect_feedback(str(uuid.uuid4()), cdk_response, "generate_cdk", BEDROCK_MODEL_ID)
