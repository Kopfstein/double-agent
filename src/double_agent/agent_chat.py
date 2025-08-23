from typing import Any, Optional

import streamlit as st


class AgentChatInterface:
    """Reusable chat interface for agent interactions."""

    def __init__(self, session_key: str = "agent_chat"):
        """Initialize the chat interface.

        Parameters
        ----------
        session_key : str
            Unique key for storing chat state in session
        """
        self.session_key = session_key
        self._initialize_session_state()

    def _initialize_session_state(self) -> None:
        """Initialize session state variables."""
        if f"{self.session_key}_messages" not in st.session_state:
            st.session_state[f"{self.session_key}_messages"] = []
        if f"{self.session_key}_agent_steps" not in st.session_state:
            st.session_state[f"{self.session_key}_agent_steps"] = []

    def display_chat_history(self) -> None:
        """Display the chat message history."""
        messages = st.session_state[f"{self.session_key}_messages"]
        for message in messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

                # Show agent steps if this is an assistant message with steps
                if message["role"] == "assistant" and "steps" in message:
                    with st.expander("Agent Steps", expanded=False):
                        for i, step in enumerate(message["steps"], 1):
                            st.write(f"**Step {i}:** {step}")

    def get_user_input(self) -> Optional[str]:
        """Get user input from chat input widget.

        Returns
        -------
        Optional[str]
            User input text, or None if no input
        """
        return st.chat_input("Enter your instructions for the agent")

    def add_user_message(self, content: str) -> None:
        """Add user message to chat history.

        Parameters
        ----------
        content : str
            User message content
        """
        # Display user message
        with st.chat_message("user"):
            st.markdown(content)

        # Add to history
        messages = st.session_state[f"{self.session_key}_messages"]
        messages.append({"role": "user", "content": content})

    def run_agent_with_steps(self, agent: Any, prompt: str) -> str:
        """Run agent and display steps in real-time.

        Parameters
        ----------
        agent : Any
            The agent instance to run
        prompt : str
            User prompt/instructions

        Returns
        -------
        str
            Final agent response
        """
        # Create containers for real-time updates
        with st.chat_message("assistant"):
            response_container = st.empty()
            steps_container = st.expander("Agent Steps", expanded=True)

            # Initialize steps tracking
            agent_steps = []

            # Show initial status
            with steps_container:
                status_placeholder = st.empty()
                status_placeholder.write("🤖 Agent is thinking...")

            try:
                # Run the agent (this is a simplified version - you may need to modify
                # based on how smolagents exposes step-by-step execution)
                with steps_container:
                    step_placeholder = st.empty()
                    step_placeholder.write("🔍 Processing your request...")
                    agent_steps.append("Processing your request...")

                # Execute agent
                response = agent.run(prompt)

                # Update final status
                with steps_container:
                    step_placeholder.write("✅ Task completed successfully!")
                    agent_steps.append("Task completed successfully!")

                # Display final response
                response_container.markdown(response)

            except Exception as e:
                error_msg = f"❌ Error occurred: {e!s}"
                with steps_container:
                    st.error(error_msg)
                agent_steps.append(error_msg)

                error_response = f"I encountered an error: {e!s}"
                response_container.markdown(error_response)
                return error_response

            finally:
                # Store steps for history
                st.session_state[f"{self.session_key}_agent_steps"] = agent_steps

    def add_assistant_message(self, content: str, steps: Optional[list] = None) -> None:
        """Add assistant message to chat history.

        Parameters
        ----------
        content : str
            Assistant response content
        steps : Optional[list]
            List of agent steps taken
        """
        messages = st.session_state[f"{self.session_key}_messages"]
        message_data = {"role": "assistant", "content": content}

        if steps:
            message_data["steps"] = steps

        messages.append(message_data)

    def clear_chat(self) -> None:
        """Clear chat history."""
        st.session_state[f"{self.session_key}_messages"] = []
        st.session_state[f"{self.session_key}_agent_steps"] = []

    def handle_chat_interaction(self, agent: Any) -> None:
        """Handle complete chat interaction flow.

        Parameters
        ----------
        agent : Any
            The agent instance to use for responses
        """
        # Display chat history
        self.display_chat_history()

        # Get user input
        if prompt := self.get_user_input():
            # Add user message
            self.add_user_message(prompt)

            # Run agent and get response with steps
            response = self.run_agent_with_steps(agent, prompt)

            # Add assistant response to history
            agent_steps = st.session_state.get(f"{self.session_key}_agent_steps", [])
            self.add_assistant_message(response, agent_steps)
