import streamlit as st
from utils import BEDROCK_MODEL_ID
from utils import store_in_s3
from utils import save_conversation
from utils import collect_feedback
from utils import invoke_bedrock_model_streaming
import uuid
from styles import apply_custom_styles


# Generate Cost Estimates
@st.fragment
def generate_cost_estimates(cost_messages):
    apply_custom_styles()
    cost_messages = cost_messages[:]

    # Retain messages and previous insights in the chat section
    if 'cost_messages' not in st.session_state:
        st.session_state.cost_messages = []

    # Create the radio button for cost estimate selection
    if 'cost_user_select' not in st.session_state:
        print("not in session_state")
        st.session_state.cost_user_select = False  # Initialize the value if it doesn't exist

    # Concatenate all 'content' from messages where 'role' is 'assistant'
    concatenated_message = ' '.join(
        message['content'] for message in cost_messages if message['role'] == 'assistant'
    )

    left, middle, right = st.columns([3, 1, 0.5])

    with left:
        # st.markdown("**Use the checkbox below to get cost estimates of AWS services in the proposed solution**")
        st.markdown(
            "<div style='font-size: 18px'><b>Usa la casilla de verificación de abajo para obtener estimaciones de costos de los servicios de AWS</b></div>",  # noqa
            unsafe_allow_html=True)
        st.divider()
        st.markdown("<div class=stButton gen-style'>", unsafe_allow_html=True)
        select_cost = st.checkbox(
            "Check this box to get the cost estimates",
            key="cost",
        )
        print(select_cost)
        # Only update the session state when the checkbox value changes
        if select_cost != st.session_state.cost_user_select:
            print(select_cost)
            st.session_state.cost_user_select = select_cost
        print("st.session_state.cost_user_select", st.session_state.cost_user_select)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        if st.session_state.cost_user_select:
            st.markdown("<div class=stButton gen-style'>", unsafe_allow_html=True)
            if st.button(label="⟳ Retry", key="retry-cost", type="secondary"):
                st.session_state.cost_user_select = True  # Probably redundant
            st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.cost_user_select:
        cost_prompt = f"""
        Calcula el costo mensual aproximado para la arquitectura generada con base en la siguiente descripción:
        {concatenated_message}
        Usa https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/price-changes.html para obtener los precios más recientes.
        Proporciona un resumen breve en formato tabular para facilitar la comprensión: nombre del servicio, configuración, precio y costo total.
        Ordena los servicios por el **costo total** en orden descendente al mostrar la tabla.
        El formato tabular debe verse **muy profesional y legible**, con una estructura clara y fácil de interpretar.
        Asegúrate de que los servicios estén ordenados por **Costo Total** de mayor a menor para resaltar los más costosos primero.
        Usa el siguiente ejemplo como referencia para generar los detalles de precios en formato tabular.

        <example>
        Con base en la arquitectura descrita y utilizando la información de precios más reciente de AWS, aquí tienes una estimación aproximada de los costos mensuales para la solución de data lake empresarial. Ten en cuenta que estas son estimaciones y los costos reales pueden variar según el uso, la transferencia de datos y otros factores.

        | Nombre del Servicio | Configuración | Precio (por unidad) | Costo Mensual Estimado |
        |---------------------|---------------|---------------------|-------------------------|
        | Amazon ECS (Fargate) | 2 tareas, 0.25 vCPU, 0.5 GB RAM, corriendo 24/7 | $0.04048 por hora | $59.50 |
        | Amazon OpenSearch | 1 instancia t3.small.search, 10 GB EBS | $0.036 por hora + $0.10 por GB-mes | $27.40 |
        | Amazon S3 | 100 GB almacenamiento, 100 GB transferencia de datos | $0.023 por GB-mes + $0.09 por GB transferido | $11.30 |
        | Amazon CloudFront | 100 GB transferencia de datos, 1M solicitudes | $0.085 por GB + $0.0075 por 10,000 solicitudes | $9.25 |
        | Application Load Balancer | 1 ALB, corriendo 24/7 | $0.0225 por hora + $0.008 por LCU-hora | $16.74 |
        | Amazon DynamoDB | 25 GB almacenamiento, 1M escrituras, 1M lecturas | $0.25 por GB-mes + $1.25 por millón de escrituras + $0.25 por millón de lecturas | $7.75 |
        | AWS Lambda | 1M invocaciones, 128 MB memoria, 100ms duración promedio | $0.20 por 1M solicitudes + $0.0000166667 por GB-segundo | $0.41 |
        | Amazon CloudWatch | 5 GB logs ingeridos, 5 métricas personalizadas | $0.50 por GB ingerido + $0.30 por métrica al mes | $4.00 |
        | Amazon VPC | 1 NAT Gateway, corriendo 24/7 | $0.045 por hora + $0.045 por GB procesado | $33.48 |
        | **Costo Mensual Estimado Total** | | | $169.83 |

        Ten en cuenta:
        1. Estas estimaciones suponen un uso moderado y pueden variar según la carga real de trabajo.
        2. Los costos de transferencia de datos entre servicios dentro de la misma región no están incluidos, ya que normalmente son gratuitos.
        3. Los costos de AWS CDK, CloudFormation e IAM no están incluidos ya que generalmente son servicios gratuitos.
        4. Los costos de Bedrock Agent y el modelo Claude no están incluidos ya que la información de precios de estos servicios no estaba disponible al momento de esta estimación.
        5. Los costos reales pueden ser menores con instancias reservadas, savings plans u otros descuentos disponibles en tu cuenta de AWS.
        </example>
        """

        cost_messages.append({"role": "user", "content": cost_prompt})

        cost_response, stop_reason = invoke_bedrock_model_streaming(cost_messages)
        cost_response = cost_response.replace("$", "USD ")
        st.session_state.cost_messages.append({"role": "assistant", "content": cost_response})

        with st.container(height=350):
            st.markdown(cost_response)

        st.session_state.interaction.append({"type": "Cost Analysis", "details": cost_response})
        store_in_s3(content=cost_response, content_type='cost')
        save_conversation(st.session_state['conversation_id'], cost_prompt, cost_response)
        collect_feedback(str(uuid.uuid4()), cost_response, "generate_cost", BEDROCK_MODEL_ID)
