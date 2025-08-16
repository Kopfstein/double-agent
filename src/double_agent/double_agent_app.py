# Double Agent Streamlit app
import os

import streamlit as st

def initialize_agent():
    """Initialize the agent only when needed."""
    from smolagents import CodeAgent, DuckDuckGoSearchTool, OpenAIServerModel
    
    # Initialize a model
    model = OpenAIServerModel(
        # model_id="deepseek/deepseek-r1-0528",
        model_id="qwen/qwen3-235b-a22b-2507",
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
        st.session_state.agent = initialize_agent()
    
    response = st.session_state.agent.run(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
