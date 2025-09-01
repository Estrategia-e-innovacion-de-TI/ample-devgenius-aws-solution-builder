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
        dsl_prompt = """Genera un diagrama de arquitectura de software en código Structurizr DSL para la solución dada siguiendo este proceso de razonamiento paso a paso:

        Paso 1: Analiza el alcance y el contexto del sistema
        Primero, lee y comprende cuidadosamente los requisitos del sistema. Pregúntate:
        - ¿Cuál es el propósito principal de este sistema?
        - ¿Quiénes son los usuarios/actores principales?
        - ¿Cuáles son los procesos o flujos de trabajo clave del negocio?
        - ¿Cuál es el nivel del modelo C4 apropiado para este diagrama (System Context, Container, Component o Code)?

        Paso 2: Identifica los elementos centrales
        Con base en tu análisis, identifica y clasifica los elementos:
        - Personas: ¿Quién interactúa con el sistema? (usuarios finales, administradores, sistemas externos que actúan como usuarios)
        - Sistemas de software: ¿Cuáles son los principales sistemas de software involucrados? (sistemas internos, externos, legados)
        - Contenedores: ¿Cuáles son las unidades desplegables/ejecutables? (aplicaciones web, APIs, bases de datos, colas de mensajes, etc.)
        - Componentes: ¿Cuáles son los principales bloques estructurales dentro de los contenedores? (controladores, servicios, repositorios, etc.)

        Paso 3: Determina relaciones y flujo de datos
        Para cada elemento identificado, piensa en:
        - ¿Con qué interactúa este elemento?
        - ¿Qué tipo de interacción es? (usa, envía datos a, se autentica con, etc.)
        - ¿Qué protocolos o tecnologías se usan? (HTTP, HTTPS, SQL, colas de mensajes, etc.)
        - ¿Cuál es la dirección del flujo de datos?

        Paso 4: Considera servicios en la nube y dependencias externas
        Evalúa si el sistema incluye:
        - Servicios en la nube (AWS S3, Azure Functions, Google Cloud Storage, etc.)
        - APIs o servicios de terceros
        - Bases de datos o fuentes de datos externas
        - Servicios de monitoreo y registro (logging)

        Paso 5: Estructura y organiza
        Planifica la disposición y organización:
        - Agrupa lógicamente los elementos relacionados
        - Considera las relaciones jerárquicas (los sistemas contienen contenedores, los contenedores contienen componentes)
        - Piensa en el flujo visual y la legibilidad del diagrama

        Paso 6: Genera el código DSL
        Ahora genera el código DSL siguiendo estas REGLAS CRÍTICAS:

        REGLAS CRÍTICAS PARA UN DSL VÁLIDO:
        1. Responde solo con código DSL en markdown (```dsl).
        2. Usa EXACTAMENTE los mismos nombres de variables de forma consistente en todo el código; nunca cambies un nombre de variable una vez declarado.
        3. NUNCA crees relaciones entre elementos padre e hijo (por ejemplo, un softwareSystem no puede tener una relación con sus propios contenedores).
        4. Todas las relaciones deben ser entre elementos del MISMO nivel jerárquico o entre diferentes sistemas/contenedores.
        5. Cada elemento debe estar debidamente declarado antes de ser referenciado en relaciones.
        6. Usa una convención de nombres consistente (camelCase) para todas las variables.
        7. Incluye siempre la estructura de workspace, model y views.

        Plantilla de estructura DSL:
        <example>
        workspace "Workspace Name" {
        model {
        // Personas
        variableName = person "Display Name" "Description"
            // Sistemas externos
            externalSystem = softwareSystem "External System Name" "Description" "External"
            
            // Sistema de software principal
            mainSystem = softwareSystem "Main System Name" "Description" {
                // Contenedores dentro del sistema
                containerName = container "Container Display Name" "Description" "Technology"
            }
            
            // Relaciones: SOLO entre sistemas/contenedores diferentes; NUNCA padre-hijo
            variableName -> mainSystem "Relationship description"
            mainSystem -> externalSystem "Relationship description"
            // Para relaciones entre contenedores, usa directamente las variables de contenedor
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
        </example>

        LISTA DE VERIFICACIÓN antes de generar:
        - [ ] Todos los nombres de variables son consistentes (sin errores tipográficos o variaciones)
        - [ ] No hay relaciones entre sistemas padre y sus contenedores hijos
        - [ ] Todas las variables referenciadas están correctamente declaradas
        - [ ] Sintaxis DSL correcta con llaves y estructura adecuadas
        - [ ] Etiquetas de tecnología entre corchetes cuando sea aplicable

        ERRORES COMUNES A EVITAR:
        1. ❌ `mainSystem -> containerInsideMainSystem` (relación padre-hijo)
        2. ❌ Usar nombres de variables diferentes para el mismo elemento
        3. ❌ Falta de declaraciones antes de usar variables en relaciones
        4. ❌ Sintaxis incorrecta en definiciones de contenedor o componente

        ✅ PATRONES CORRECTOS:
        1. `person -> softwareSystem`
        2. `softwareSystem -> externalSystem`
        3. `container -> container` (cuando están en sistemas diferentes)
        4. `container -> externalSystem`

        Ahora aplica este proceso de razonamiento para generar tu código en Structurizr DSL, asegurando que se sigan estrictamente todas las reglas."""   

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
