import uuid
import get_code_from_markdown
import streamlit as st
from utils import BEDROCK_MODEL_ID
from utils import store_in_s3
from utils import save_conversation
from utils import collect_feedback
from utils import continuation_prompt
from utils import invoke_bedrock_model_streaming


@st.fragment
def generate_dsl(dsl_messages):

    dsl_messages = dsl_messages[:]

    # Retain messages and previous insights in the chat section
    if 'dsl_messages' not in st.session_state:
        st.session_state.dsl_messages = []

    if 'dsl_user_select' not in st.session_state:
        st.session_state.dsl_user_select = False

    left, middle, right = st.columns([3, 1, 0.5])

    with left:
        st.markdown(
            "<div style='font-size: 18px'><b>Use the checkbox below to generate an architecture diagram in DSL</b></div>",  # noqa
            unsafe_allow_html=True)
        st.divider()
        st.markdown("<div class=stButton gen-style'>", unsafe_allow_html=True)
        select_dsl = st.checkbox(
            "Check this box to generate DSL code",
            key="dsl"
        )
        if select_dsl != st.session_state.dsl_user_select:
            st.session_state.dsl_user_select = select_dsl
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        if st.session_state.dsl_user_select:
            st.markdown("<div class=stButton gen-style'>", unsafe_allow_html=True)
            if st.button(label="⟳ Retry", key="retry-dsl", type="secondary"):
                st.session_state.dsl_user_select = True
            st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.dsl_user_select:
        dsl_prompt = """
            Generate a software architecture diagram in Structurizr DSL.
            Follow these strict rules:

            1. Respond ONLY with valid Structurizr DSL code enclosed in a markdown code block (```dsl).
            2. The DSL MUST strictly follow the official Structurizr DSL syntax:
            - Use 'workspace', 'model', 'views', and 'styles' sections when appropriate.
            - All elements (persons, software systems, containers, components) must be defined inside 'model'.
            - Relationships must be explicitly declared using '->' with appropriate labels.
            3. Organize the diagram following the C4 model:
            - Level 1: Persons and Software Systems.
            - Level 2: Containers (if relevant).
            - Level 3: Components (if more detail is requested).
            4. When including cloud services or external systems (optional), define them as 'Software System' or 'Container' with tags like 'AWS', 'Azure', or 'GCP' if applicable.
            5. Ensure:
            - All identifiers (IDs) are unique and syntactically correct (no spaces, use camelCase).
            - All relationships reference valid defined elements.
            - The code is COMPLETE and executable without requiring manual fixes.
            6. Include at least one view (SystemContext or Container) and ensure it references valid model elements.
            7. Add a 'styles' section with simple styling for readability (e.g., different colors for Person, Software System, Container).
            8. Do NOT add explanations, comments, or text outside the DSL block.
            9. Double-check that:
            - Every relationship references existing elements.
            - Views do not include undefined elements.
            - The DSL compiles in Structurizr without errors.
            """  # noqa  

        st.session_state.dsl_messages.append({"role": "user", "content": dsl_prompt})
        dsl_messages.append({"role": "user", "content": dsl_prompt})

        max_attempts = 4
        full_response_array = []
        full_response = ""

        for attempt in range(max_attempts):
            dsl_response, stop_reason = invoke_bedrock_model_streaming(dsl_messages, enable_reasoning=True)
            full_response_array.append(dsl_response)

            if stop_reason != "max_tokens":
                break

            if attempt == 0:
                full_response = ''.join(str(x) for x in full_response_array)
                dsl_messages = continuation_prompt(dsl_prompt, full_response)

        if attempt == max_attempts - 1:
            st.error("Reached maximum number of attempts. Final result is incomplete. Please try again.")

        try:
            full_response = ''.join(str(x) for x in full_response_array)
            # Extraemos el bloque de DSL del markdown
            dsl_code = get_code_from_markdown.get_code_from_markdown(full_response, language="dsl")[0]

            # Mostrar el DSL en un text area (copiable)
            st.text_area("DSL Output", value=dsl_code, height=350)

            st.session_state.dsl_messages.append({"role": "assistant", "content": "DSL"})

            st.session_state.interaction.append({"type": "DSL Diagram", "details": full_response})
            store_in_s3(content=full_response, content_type='dsl')
            save_conversation(st.session_state['conversation_id'], dsl_prompt, full_response)
            collect_feedback(str(uuid.uuid4()), dsl_code, "generate_dsl", BEDROCK_MODEL_ID)

        except Exception as e:
            st.error("Internal error occurred. Please try again.")
            print(f"Error occurred when generating DSL: {str(e)}")
            del st.session_state.dsl_messages[-1]
            del dsl_messages[-1]
