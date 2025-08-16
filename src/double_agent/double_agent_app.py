# Double Agent Streamlit app
import os

import streamlit as st


def initialize_agent(model_id: str):
    """Initialize the agent with the specified model."""
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


# Check if API key is present
if not os.getenv("OPENROUTER_API_KEY"):
    st.error("OPENROUTER_API_KEY environment variable is not set. Please set it and restart the application.")
    st.stop()

# Follow tutorial: https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps

st.title("Double Agent")

# Sidebar for model selection
with st.sidebar:
    st.header("Model Selection")
    model_options = [
        "qwen/qwen3-235b-a22b-2507",
        "deepseek/deepseek-r1-0528",
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4o",
        "meta-llama/llama-3.3-70b-instruct",
    ]
    
    selected_model = st.selectbox(
        "Choose a model:",
        model_options,
        index=0,
        help="Select the AI model to use for the conversation"
    )
    
    # Clear agent if model changes
    if "current_model" not in st.session_state:
        st.session_state.current_model = selected_model
    elif st.session_state.current_model != selected_model:
        st.session_state.current_model = selected_model
        if "agent" in st.session_state:
            del st.session_state.agent
        st.rerun()

# Initialize history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Enter your instructions"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Initialize agent only when needed
    if "agent" not in st.session_state:
        st.session_state.agent = initialize_agent(selected_model)

    response = st.session_state.agent.run(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
