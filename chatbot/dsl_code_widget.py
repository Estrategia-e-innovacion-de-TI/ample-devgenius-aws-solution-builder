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
            Generate a software architecture diagram in DSL by following this step-by-step thinking process:

            Step 1: Analyze the System Scope and Context
            First, carefully read and understand the system requirements. Ask yourself:
            - What is the main purpose of this system?
            - Who are the primary users/actors?
            - What are the key business processes or workflows?
            - What is the appropriate C4 model level for this diagram (System Context, Container, Component, or Code)?

            Step 2: Identify Core Elements
            Based on your analysis, identify and categorize the elements:
            - Persons: Who interacts with the system? (end users, administrators, external systems acting as users)
            - Software Systems: What are the main software systems involved? (internal systems, external systems, legacy systems)
            - Containers: What are the deployable/executable units? (web apps, APIs, databases, message queues, etc.)
            - Components: What are the major structural building blocks within containers? (controllers, services, repositories, etc.)

            Step 3: Determine Relationships and Data Flow
            For each element identified, think about:
            - What does this element interact with?
            - What type of interaction is it? (uses, sends data to, authenticates with, etc.)
            - What protocols or technologies are used? (HTTP, HTTPS, SQL, message queues, etc.)
            - What is the direction of the data flow?

            Step 4: Consider Cloud Services and External Dependencies
            Evaluate if the system includes:
            - Cloud services (AWS S3, Azure Functions, Google Cloud Storage, etc.)
            - Third-party APIs or services
            - External databases or data sources
            - Monitoring and logging services

            Step 5: Structure and Organize
            Plan the layout and organization:
            - Group related elements logically
            - Consider hierarchical relationships (systems contain containers, containers contain components)
            - Think about the visual flow and readability of the diagram

            Step 6: Generate DSL Code
            Now generate the DSL code following these rules:

            Rules:
            1. Respond only with DSL code in markdown (```dsl).
            2. Depending on the level of detail, you may define persons, software systems, containers, and/or components, following the C4 model.
            3. If relevant, you may include cloud services (e.g., AWS, Azure, GCP) as containers or systems, but this is optional and not required.
            4. Use relationships to clearly show interactions and data flows between elements.
            5. Ensure the DSL is syntactically correct and can be used directly in a DSL tool.
            6. Organize the elements cleanly so that the generated diagram is neat and understandable.
            7. Do not add explanations or extra text outside the DSL block.

            DSL Syntax Guidelines:
            - Use clear, descriptive names for all elements
            - Include technology labels in square brackets where relevant
            - Use descriptive relationship labels that explain the interaction
            - Maintain consistent naming conventions (camelCase or snake_case)
            - Group related elements using proper indentation or grouping syntax

            Example Thinking Process:
            "I need to create an architecture for an e-commerce system. Let me think:
            1. Scope: This seems like a Container-level diagram would be appropriate
            2. Elements: I need a Customer (person), Web App (container), API (container), Database (container), and Payment Service (external system)
            3. Relationships: Customer uses Web App, Web App calls API, API reads/writes to Database, API integrates with Payment Service
            4. No specific cloud services mentioned, so I'll keep it generic
            5. I'll organize them in a logical flow from user to data storage"

            Now apply this thinking process to generate your DSL architecture diagram.
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
