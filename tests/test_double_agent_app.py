# Unit tests for Double Agent Streamlit app
from streamlit.testing.v1 import AppTest


def test_app_title():
    app = AppTest.from_file("../src/double_agent/double_agent_app.py").run()
    assert "Double Agent" in app.title[0].value
