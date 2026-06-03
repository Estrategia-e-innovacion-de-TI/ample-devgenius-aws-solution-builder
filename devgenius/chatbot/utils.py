"""
Utilidades compartidas: extracción de código de markdown, conversión DSL a diagrama,
carga de archivos externos, loader dinámico de skills.
"""
import os
import re
import glob
import zlib
import base64
import importlib
from typing import Optional

import requests
from langchain_core.tools import StructuredTool


def get_code_from_markdown(text: str, language: str = "") -> list[str]:
    """
    Extrae bloques de código de un texto markdown dado un lenguaje.
    """
    pattern = rf"```{language}\s*\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    if not matches:
        pattern = r"```\s*\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
    return matches if matches else [text]


def clean_dsl_code(dsl_code: str) -> str:
    """
    Limpia y valida código Structurizr DSL.
    """
    dsl_code = dsl_code.strip()

    if not dsl_code.startswith("workspace"):
        lines = dsl_code.split("\n")
        start_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith("workspace"):
                start_idx = i
                break
        if start_idx is not None:
            brace_count = 0
            end_idx = len(lines) - 1
            for i in range(start_idx, len(lines)):
                brace_count += lines[i].count("{")
                brace_count -= lines[i].count("}")
                if brace_count == 0 and i > start_idx:
                    end_idx = i
                    break
            dsl_code = "\n".join(lines[start_idx : end_idx + 1])

    return dsl_code


def structurizr_to_diagram(dsl_code: str, fmt: str = "png") -> Optional[bytes]:
    """
    Convierte código Structurizr DSL a diagrama usando la API de Kroki.
    """
    try:
        compressed = zlib.compress(dsl_code.encode("utf-8"), level=9)
        encoded = base64.urlsafe_b64encode(compressed).decode("utf-8")
        url = f"https://kroki.io/structurizr/{fmt}/{encoded}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"[ERROR] Convirtiendo DSL a diagrama: {e}")
        return None


def convert_xml_to_html(xml_string: str) -> str:
    """
    Convierte XML de draw.io a HTML embebible para abrir en navegador.
    """
    from defusedxml.ElementTree import fromstring, tostring

    root = fromstring(xml_string, forbid_entities=True)
    xml_str_bytes = tostring(root, encoding="utf8", method="xml", xml_declaration=False)
    xml_str = xml_str_bytes.decode("utf-8")
    xml_str = xml_str.replace("&", "&amp;")
    xml_str = xml_str.replace("<", "&lt;")
    xml_str = xml_str.replace(">", "&gt;")
    xml_str = xml_str.replace('"', "&quot;")
    xml_str = xml_str.replace("\n", "\\n")

    html_output = (
        '<div class="mxgraph" style="max-width:100%;border:1px solid transparent;" '
        'data-mxgraph="{{&quot;highlight&quot;:&quot;#0000ff&quot;,&quot;nav&quot;:true,'
        '&quot;resize&quot;:true,&quot;toolbar&quot;:&quot;zoom layers tags lightbox&quot;,'
        f'&quot;edit&quot;:&quot;_blank&quot;,&quot;xml&quot;:&quot;{xml_str}\\n&quot;}}"></div>\n'
        '<script type="text/javascript" src="https://www.draw.io/js/viewer.min.js"></script>'
    )
    return html_output


def load_markdown_files(directory: str) -> str:
    """
    Carga todos los archivos .md de un directorio y retorna su contenido concatenado.

    Args:
        directory: Ruta absoluta al directorio con archivos .md.

    Returns:
        Texto consolidado con el contenido de todos los archivos separados por líneas.
    """
    content_parts = []
    md_files = sorted(glob.glob(os.path.join(directory, "*.md")))
    for filepath in md_files:
        with open(filepath, "r", encoding="utf-8") as f:
            content_parts.append(f.read().strip())
    return "\n\n---\n".join(content_parts)


def load_skills(skills_dir: str) -> list:
    """
    Descubre y carga dinámicamente todas las skills del directorio dado.

    Cada skill es una subcarpeta que contiene:
    - SKILL.md: descripción y triggers (usada como docstring de la tool).
    - script.py: módulo con función run(conversation_context: str) -> str.

    Args:
        skills_dir: Ruta absoluta al directorio de skills.

    Returns:
        Lista de LangChain tools generadas dinámicamente desde las skills.
    """
    tools = []
    skills_dir = os.path.abspath(skills_dir)

    if not os.path.isdir(skills_dir):
        return tools

    for skill_name in sorted(os.listdir(skills_dir)):
        skill_path = os.path.join(skills_dir, skill_name)

        # Solo procesar directorios con SKILL.md y script.py
        skill_md = os.path.join(skill_path, "SKILL.md")
        script_py = os.path.join(skill_path, "script.py")

        if not os.path.isdir(skill_path):
            continue
        if not os.path.isfile(skill_md) or not os.path.isfile(script_py):
            continue

        # Leer descripción del SKILL.md
        with open(skill_md, "r", encoding="utf-8") as f:
            skill_description = f.read().strip()

        # Extraer la primera sección "## Descripción" como descripción corta para la tool
        short_desc = _extract_description(skill_description)

        # Importar dinámicamente el módulo script.py
        module_name = f"chatbot.skills.{skill_name}.script"
        module = importlib.import_module(module_name)
        run_fn = module.run

        # Crear LangChain tool
        tool = StructuredTool.from_function(
            func=run_fn,
            name=skill_name,
            description=short_desc,
        )
        tools.append(tool)

    return tools


def _extract_description(skill_md_content: str) -> str:
    """Extrae la descripción corta del SKILL.md (contenido bajo ## Descripción)."""
    lines = skill_md_content.split("\n")
    capture = False
    description_lines = []

    for line in lines:
        if line.strip().startswith("## Descripción"):
            capture = True
            continue
        if capture:
            if line.strip().startswith("## "):
                break
            if line.strip():
                description_lines.append(line.strip())

    return " ".join(description_lines) if description_lines else skill_md_content[:200]
