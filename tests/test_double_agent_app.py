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
        # The app should show an error message
        assert len(app.error) > 0
        assert "OPENROUTER_API_KEY" in app.error[0].value
