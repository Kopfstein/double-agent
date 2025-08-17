# Unit tests for Double Agent Streamlit app
import os
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


def test_app_title():
    # Mock the environment variable to avoid API key issues
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key"}):
        app = AppTest.from_file("../src/double_agent/double_agent_app.py").run(timeout=10)
        assert "Double Agent" in app.title[0].value


def test_app_without_api_key():
    # Test that app shows error when API key is missing
    with patch.dict(os.environ, {}, clear=True):
        app = AppTest.from_file("../src/double_agent/double_agent_app.py").run(timeout=10)
        # The app should show an error message or stop execution
        # Check if there's an error element or if the app stopped
        has_error = len(app.error) > 0
        if has_error:
            assert "OPENROUTER_API_KEY" in app.error[0].value
        else:
            # If no error element, check that the app doesn't have the main UI elements
            # when API key is missing (indicating st.stop() was called)
            assert len(app.selectbox) == 0 or len(app.chat_input) == 0
