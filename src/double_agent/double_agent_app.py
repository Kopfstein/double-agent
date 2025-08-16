# Double Agent Streamlit app
import os

import streamlit as st
from smolagents import CodeAgent, DuckDuckGoSearchTool, OpenAIServerModel

# Check if API key is present
if not os.getenv("OPENROUTER_API_KEY"):
    st.error("OPENROUTER_API_KEY environment variable is not set. Please set it and restart the application.")
    st.stop()

# Initialize a model
model = OpenAIServerModel(
    model_id="deepseek/deepseek-r1-0528",
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

    response = agent.run(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
