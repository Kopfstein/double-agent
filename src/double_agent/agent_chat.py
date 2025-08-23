from typing import Optional

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

    def start_agent_response(self) -> tuple:
        """Start displaying an agent response with steps container.

        Returns
        -------
        tuple
            (response_container, steps_container) for updating the UI
        """
        chat_container = st.chat_message("assistant")
        with chat_container:
            response_container = st.empty()
            steps_container = st.expander("Agent Steps", expanded=True)
            return response_container, steps_container

    def update_agent_step(self, steps_container, step_text: str) -> None:
        """Update the agent steps display.

        Parameters
        ----------
        steps_container
            Streamlit container for steps
        step_text : str
            Text to display for current step
        """
        with steps_container:
            st.write(f"🔍 {step_text}")

    def show_agent_error(self, steps_container, error_msg: str) -> None:
        """Show an error in the agent steps.

        Parameters
        ----------
        steps_container
            Streamlit container for steps
        error_msg : str
            Error message to display
        """
        with steps_container:
            st.error(f"❌ {error_msg}")

    def show_agent_success(self, steps_container) -> None:
        """Show success status in agent steps.

        Parameters
        ----------
        steps_container
            Streamlit container for steps
        """
        with steps_container:
            st.write("✅ Task completed successfully!")

    def display_final_response(self, response_container, response: str) -> None:
        """Display the final agent response.

        Parameters
        ----------
        response_container
            Streamlit container for the response
        response : str
            The agent's response text
        """
        response_container.markdown(response)

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

    def handle_chat_interaction(self, agent_runner_callback) -> None:
        """Handle complete chat interaction flow.

        Parameters
        ----------
        agent_runner_callback : callable
            Function that takes (agent_interface, prompt) and runs the agent
        """
        # Display chat history
        self.display_chat_history()

        # Get user input
        if prompt := self.get_user_input():
            # Add user message
            self.add_user_message(prompt)

            # Run agent via callback
            agent_runner_callback(self, prompt)
