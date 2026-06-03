"""
Tests unitarios para la herramienta generate_c1_context (diagrama C4 Nivel C1).
"""
import json
from unittest.mock import patch, MagicMock

import pytest

from chatbot.tools.dsl_c1_context import generate_c1_context


SAMPLE_DSL = """workspace "System Context" {
    model {
        user = person "End User" "A user of the system"
        mainSystem = softwareSystem "My System" "Does something useful"
        emailSystem = softwareSystem "Email System" "Sends emails" "Existing System"

        user -> mainSystem "Uses" "HTTPS"
        mainSystem -> emailSystem "Sends notifications" "SMTP"
    }
    views {
        systemContext mainSystem "SystemContext" {
            include *
            autoLayout
        }
    }
}"""


@pytest.fixture
def mock_bedrock_response():
    """Simula la respuesta de Bedrock con un DSL C1 válido."""
    return {
        "body": MagicMock(
            read=MagicMock(
                return_value=json.dumps(
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": f"```dsl\n{SAMPLE_DSL}\n```",
                            }
                        ]
                    }
                ).encode()
            )
        )
    }


class TestGenerateC1Context:
    """Tests para la tool generate_c1_context."""

    @patch("chatbot.tools.dsl_c1_context.structurizr_to_diagram")
    @patch("chatbot.tools.dsl_c1_context.boto3.client")
    def test_generates_dsl_file(self, mock_boto_client, mock_kroki, mock_bedrock_response, tmp_path):
        """Verifica que se genera el archivo DSL correctamente."""
        mock_client = MagicMock()
        mock_client.invoke_model.return_value = mock_bedrock_response
        mock_boto_client.return_value = mock_client
        mock_kroki.return_value = b"\x89PNG fake image bytes"

        with patch("chatbot.tools.dsl_c1_context.OUTPUT_DIR", str(tmp_path)):
            result = generate_c1_context.invoke("Un sistema de e-commerce con pagos externos")

        assert "Diagrama C4 Nivel C1 (System Context) generado" in result
        assert "diagram_c1_context_" in result
        assert ".dsl" in result

    @patch("chatbot.tools.dsl_c1_context.structurizr_to_diagram")
    @patch("chatbot.tools.dsl_c1_context.boto3.client")
    def test_generates_png_file(self, mock_boto_client, mock_kroki, mock_bedrock_response, tmp_path):
        """Verifica que se genera la imagen PNG cuando Kroki responde correctamente."""
        mock_client = MagicMock()
        mock_client.invoke_model.return_value = mock_bedrock_response
        mock_boto_client.return_value = mock_client
        mock_kroki.return_value = b"\x89PNG fake image bytes"

        with patch("chatbot.tools.dsl_c1_context.OUTPUT_DIR", str(tmp_path)):
            result = generate_c1_context.invoke("Sistema con usuarios y APIs externas")

        assert "Imagen PNG:" in result
        assert ".png" in result

    @patch("chatbot.tools.dsl_c1_context.structurizr_to_diagram")
    @patch("chatbot.tools.dsl_c1_context.boto3.client")
    def test_warns_when_png_fails(self, mock_boto_client, mock_kroki, mock_bedrock_response, tmp_path):
        """Verifica que se muestra advertencia cuando falla la generación PNG."""
        mock_client = MagicMock()
        mock_client.invoke_model.return_value = mock_bedrock_response
        mock_boto_client.return_value = mock_client
        mock_kroki.return_value = None  # Simula fallo de Kroki

        with patch("chatbot.tools.dsl_c1_context.OUTPUT_DIR", str(tmp_path)):
            result = generate_c1_context.invoke("Sistema simple")

        assert "[WARN]" in result
        assert "No se pudo generar la imagen PNG" in result

    @patch("chatbot.tools.dsl_c1_context.structurizr_to_diagram")
    @patch("chatbot.tools.dsl_c1_context.boto3.client")
    def test_dsl_content_is_valid_c1(self, mock_boto_client, mock_kroki, mock_bedrock_response, tmp_path):
        """Verifica que el DSL guardado no contiene elementos de C2/C3/C4."""
        mock_client = MagicMock()
        mock_client.invoke_model.return_value = mock_bedrock_response
        mock_boto_client.return_value = mock_client
        mock_kroki.return_value = b"\x89PNG fake"

        with patch("chatbot.tools.dsl_c1_context.OUTPUT_DIR", str(tmp_path)):
            generate_c1_context.invoke("Sistema de pagos")

        # Verificar que el DSL guardado es C1 puro
        dsl_files = list(tmp_path.glob("*.dsl"))
        assert len(dsl_files) == 1

        content = dsl_files[0].read_text(encoding="utf-8")
        assert "workspace" in content
        assert "person" in content
        assert "softwareSystem" in content
        assert "systemContext" in content
        # No debe tener elementos de niveles inferiores
        assert "container " not in content
        assert "component " not in content
