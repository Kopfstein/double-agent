# Double Agent Streamlit app
import os
from typing import Any

import langfuse
import streamlit as st
from dotenv import load_dotenv
from openinference.instrumentation.smolagents import SmolagentsInstrumentor

from double_agent.agent_chat import AgentChatInterface


def initialize_agent(model_id: str) -> Any:
    """Initialize the agent with the specified model.

    Parameters
    ----------
    model_id : str
        The model identifier to use for the agent (e.g., "qwen/qwen3-235b-a22b-2507").

    Returns
    -------
    Any
        A configured CodeAgent instance with the specified model and DuckDuckGo search tool.

    Raises
    ------
    Exception
        If the OPENROUTER_API_KEY environment variable is not set or if model initialization fails.
    """
    from smolagents import CodeAgent, DuckDuckGoSearchTool, OpenAIServerModel

    # Initialize a model
    model = OpenAIServerModel(
        model_id=model_id,
        api_base="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    # Create agent without tools
    agent = CodeAgent(
        model=model,
        name="double_agent",
        description="AI agent helping users to explore opposing views.",
        tools=[DuckDuckGoSearchTool()],
    )
    return agent


def run_agent_with_ui_updates(chat_interface: AgentChatInterface, prompt: str) -> None:
    """Run agent and update UI in real-time.
    
    Parameters
    ----------
    chat_interface : AgentChatInterface
        The chat interface for UI updates
    prompt : str
        User prompt/instructions
    """
    # Start agent response display
    response_container, steps_container = chat_interface.start_agent_response()
    
    # Initialize steps tracking
    agent_steps = []
    
    # Show initial status
    chat_interface.update_agent_step(steps_container, "Agent is thinking...")
    agent_steps.append("Agent is thinking...")
    
    try:
        # Show processing step
        chat_interface.update_agent_step(steps_container, "Processing your request...")
        agent_steps.append("Processing your request...")
        
        # Execute agent
        response = st.session_state.agent.run(prompt)
        
        # Show success
        chat_interface.show_agent_success(steps_container)
        agent_steps.append("Task completed successfully!")
        
        # Display final response
        chat_interface.display_final_response(response_container, response)
        
        # Add to chat history
        chat_interface.add_assistant_message(response, agent_steps)
        
    except Exception as e:
        error_msg = f"Error occurred: {str(e)}"
        chat_interface.show_agent_error(steps_container, error_msg)
        agent_steps.append(error_msg)
        
        error_response = f"I encountered an error: {str(e)}"
        chat_interface.display_final_response(response_container, error_response)
        
        # Add error to chat history
        chat_interface.add_assistant_message(error_response, agent_steps)


# Load environment variables from .env file\
load_dotenv()

# Check if API key is present
if not os.getenv("OPENROUTER_API_KEY"):
    st.error("OPENROUTER_API_KEY environment variable is not set. Please set it and restart the application.")
    st.stop()

# Initialize Langfuse client
langfuse_client = langfuse.get_client()
if not langfuse_client.auth_check():
    st.error("Failed to initialize Langfuse client. Please check your configuration.")
    st.stop()

# Initialize Smolagents instrumentation
SmolagentsInstrumentor().instrument()

st.title("Double Agent")

# Sidebar for model selection
with st.sidebar:
    st.header("Model Selection")
    model_options = [
        "qwen/qwen3-235b-a22b-2507",
        "mistralai/mistral-small-3.2-24b-instruct",
        "deepseek/deepseek-r1-0528",
        "anthropic/claude-sonnet-4",
    ]

    selected_model = st.selectbox(
        "Choose a model:", model_options, index=0, help="Select the AI model to use for the conversation"
    )

    # Clear agent if model changes
    if "current_model" not in st.session_state:
        st.session_state.current_model = selected_model
    elif st.session_state.current_model != selected_model:
        st.session_state.current_model = selected_model
        if "agent" in st.session_state:
            del st.session_state.agent
        st.rerun()

    st.header("Chat Controls")
    if st.button("Clear Chat History"):
        chat_interface = AgentChatInterface("double_agent_chat")
        chat_interface.clear_chat()
        st.rerun()

# Initialize chat interface
chat_interface = AgentChatInterface("double_agent_chat")

# Initialize agent only when needed
if "agent" not in st.session_state:
    with st.spinner("Initializing agent..."):
        st.session_state.agent = initialize_agent(selected_model)

# Handle chat interaction
chat_interface.handle_chat_interaction(run_agent_with_ui_updates)
