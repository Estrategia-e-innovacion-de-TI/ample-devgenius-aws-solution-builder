import get_code_from_markdown
from typing import Optional, Tuple
from defusedxml.ElementTree import fromstring
from defusedxml.ElementTree import tostring

def convert_xml_to_html(xml_string):
    html_output = """
    <div class="mxgraph" style="max-width:100%;border:1px solid transparent;" data-mxgraph="{{&quot;highlight&quot;:&quot;#0000ff&quot;,&quot;nav&quot;:true,&quot;resize&quot;:true,&quot;toolbar&quot;:&quot;zoom layers tags lightbox&quot;,&quot;edit&quot;:&quot;_blank&quot;,&quot;xml&quot;:&quot;{text_to_replace}\\n&quot;}}"></div>
    <script type="text/javascript" src="https://www.draw.io/js/viewer.min.js"></script>
    """  # noqa

    root = fromstring(xml_string, forbid_entities=True)
    xml_str_bytes = tostring(root, encoding='utf8', method='xml', xml_declaration=False)
    xml_str = xml_str_bytes.decode('utf-8')

    xml_str = xml_str.replace("&", "&amp;")
    xml_str = xml_str.replace("<", "&lt;")
    xml_str = xml_str.replace(">", "&gt;")
    xml_str = xml_str.replace('"', "\&quot;")  # noqa
    xml_str = xml_str.replace("\n", "\\n")

    final_html_output = html_output.format(text_to_replace=xml_str)
    return final_html_output

# Función auxiliar para limpiar y validar DSL
def clean_dsl_code(dsl_code: str) -> str:
    """
    Limpia y valida código DSL
    
    Args:
        dsl_code: Código DSL crudo
        
    Returns:
        Código DSL limpio
    """
    # Remover espacios extra y líneas vacías al inicio/final
    dsl_code = dsl_code.strip()
    
    # Si no empieza con workspace, podría estar dentro de bloques de código
    if not dsl_code.startswith('workspace'):
        # Buscar el bloque workspace
        lines = dsl_code.split('\n')
        start_idx = None
        end_idx = None
        
        for i, line in enumerate(lines):
            if line.strip().startswith('workspace'):
                start_idx = i
                break
        
        if start_idx is not None:
            # Encontrar el final del workspace (última línea con })
            brace_count = 0
            for i in range(start_idx, len(lines)):
                line = lines[i].strip()
                brace_count += line.count('{')
                brace_count -= line.count('}')
                if brace_count == 0 and i > start_idx:
                    end_idx = i
                    break
            
            if end_idx is not None:
                dsl_code = '\n'.join(lines[start_idx:end_idx+1])
    
    return dsl_code

def extract_dsl_from_markdown(text: str) -> str:
    """
    Extrae código DSL de un texto markdown.
    
    Args:
        text: Texto que puede contener bloques de código markdown
    
    Returns:
        Código DSL extraído
    
    Raises:
        ValueError: Si no se encuentra código DSL
    """
    try:
        dsl_blocks = get_code_from_markdown.get_code_from_markdown(text, language="dsl")
        if not dsl_blocks:
            raise ValueError("No DSL code blocks found")
        return dsl_blocks[0]
    except (IndexError, Exception) as e:
        raise ValueError(f"Failed to extract DSL code: {str(e)}")


def validate_dsl_structure(dsl_code: str) -> Tuple[bool, Optional[str]]:
    """
    Valida la estructura básica del código DSL.
    
    Args:
        dsl_code: Código DSL a validar
    
    Returns:
        Tupla (is_valid, error_message)
    """
    required_elements = ["workspace", "model", "views"]
    
    for element in required_elements:
        if element not in dsl_code.lower():
            return False, f"Missing required element: {element}"
    
    # Verificar balance de llaves
    open_braces = dsl_code.count("{")
    close_braces = dsl_code.count("}")
    
    if open_braces != close_braces:
        return False, f"Unbalanced braces: {open_braces} opening, {close_braces} closing"
    
    return True, None