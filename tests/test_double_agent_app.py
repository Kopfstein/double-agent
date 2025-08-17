# Unit tests for Double Agent Streamlit app
import os
from unittest.mock import MagicMock, patch

from streamlit.testing.v1 import AppTest


def test_app_title():
    # Mock the environment variable and Langfuse client to avoid API key issues
    with (
        patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key"}),
        patch("langfuse.get_client") as mock_langfuse,
        patch("openinference.instrumentation.smolagents.SmolagentsInstrumentor"),
    ):
        # Mock Langfuse client to return successful auth check
        mock_client = MagicMock()
        mock_client.auth_check.return_value = True
        mock_langfuse.return_value = mock_client

        app = AppTest.from_file("../src/double_agent/double_agent_app.py").run(timeout=10)
        assert "Double Agent" in app.title[0].value


def test_app_without_api_key():
    # Test that app shows error when API key is missing
    with (
        patch.dict(os.environ, {}, clear=True),
        patch("dotenv.load_dotenv"),
        patch("langfuse.get_client") as mock_langfuse,
        patch("openinference.instrumentation.smolagents.SmolagentsInstrumentor"),
    ):
        # Mock Langfuse client to return successful auth check
        mock_client = MagicMock()
        mock_client.auth_check.return_value = True
        mock_langfuse.return_value = mock_client

        app = AppTest.from_file("../src/double_agent/double_agent_app.py").run(timeout=10)
        # The app should show an error message
        assert len(app.error) > 0
        assert "OPENROUTER_API_KEY" in app.error[0].value
