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
            "<div style='font-size: 18px'><b>Usa la casilla de verificación de abajo para generar un diagrama de arquitectura en DSL</b></div>",  # noqa
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
        dsl_prompt = """Generate a software architecture diagram in Structurizr DSL code for the given solution by following this step-by-step thinking process:

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
        Now generate the DSL code following these CRITICAL rules:

        CRITICAL RULES FOR VALID DSL:
        1. Respond only with DSL code in markdown (```dsl).
        2. Use EXACT variable names consistently throughout - never change a variable name once declared.
        3. NEVER create relationships between parent and child elements (e.g., a softwareSystem cannot have a relationship with its own containers).
        4. All relationships must be between elements at the SAME hierarchical level or between different systems/containers.
        5. Each element must be properly declared before being referenced in relationships.
        6. Use consistent naming convention (camelCase) for all variable names.
        7. Always include the workspace, model, and views structure.

        DSL Structure Template:
        workspace "Workspace Name" {
        model {
        // Persons
        variableName = person "Display Name" "Description"
            // External Systems
            externalSystem = softwareSystem "External System Name" "Description" "External"
            
            // Main Software System
            mainSystem = softwareSystem "Main System Name" "Description" {
                // Containers within the system
                containerName = container "Container Display Name" "Description" "Technology"
            }
            
            // Relationships - ONLY between different systems/containers, NEVER parent-child
            variableName -> mainSystem "Relationship description"
            mainSystem -> externalSystem "Relationship description"
            // For container relationships, use the container variables directly
            containerName -> externalSystem "Relationship description"
        }

        views {
            systemContext mainSystem {
                include *
                autoLayout
            }
            
            container mainSystem {
                include *
                autoLayout
            }
        }
        }

        VALIDATION CHECKLIST before generating:
        - [ ] All variable names are consistent (no typos or variations)
        - [ ] No relationships between parent systems and their child containers
        - [ ] All referenced variables are properly declared
        - [ ] Proper DSL syntax with correct braces and structure
        - [ ] Technology tags in square brackets where applicable

        COMMON ERRORS TO AVOID:
        1. ❌ `mainSystem -> containerInsideMainSystem` (parent-child relationship)
        2. ❌ Using different variable names for the same element
        3. ❌ Missing variable declarations before relationships
        4. ❌ Incorrect syntax in container or component definitions

        ✅ CORRECT PATTERNS:
        1. `person -> softwareSystem`
        2. `softwareSystem -> externalSystem`
        3. `container -> container` (when in different systems)
        4. `container -> externalSystem`

        Now apply this thinking process to generate your Structurizr DSL code, ensuring all rules are followed strictly."""
   

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
