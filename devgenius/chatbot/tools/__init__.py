from chatbot.tools.generate_arch import generate_architecture
from chatbot.tools.generate_cdk import generate_cdk
from chatbot.tools.generate_cfn import generate_cfn
from chatbot.tools.generate_doc import generate_doc
from chatbot.tools.dsl_code import generate_dsl

ALL_TOOLS = [
    generate_architecture,
    generate_cdk,
    generate_cfn,
    generate_doc,
    generate_dsl,
]
