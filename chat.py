import os

import streamlit as st

from dotenv import load_dotenv
import openai

# Display the current working directory in the Streamlit app
st.write(f"Current working directory: {os.getcwd()}")

print(f"Current working directory: {os.getcwd()}")

# Load environment variables from .env file
load_dotenv(".env")

# Load environment variables from .env file
# load_dotenv()

# Ensure your OpenAI API key is loaded from the environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

from plan_pal_assistant import run_conversation


# Function to mimic processing and responding to a message
def process_message(message):
    # Here you can add your logic to process the message
    # For demonstration, we'll just echo the message
    return run_conversation(message)
    # return "Hello"


# Creating a session state to store chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Chat UI
st.title('Simple Chat App')

# Join all messages in chat_history and display in a single text_area
chat_display = "\n".join(st.session_state['chat_history'])
st.text_area("Chat", value=chat_display, height=300, disabled=True)

# Input for new message
user_message = st.text_input("Type your message here...", "")

# Button to send message
send_button = st.button('Send')

# Process and update chat history
if send_button and user_message:
    # Processing the user message
    response = process_message(user_message)
    # Appending the user message and response to the chat history
    st.session_state['chat_history'].append(f"You: {user_message}")
    st.session_state['chat_history'].append(response)
    # Clearing the input box after sending the message
    st.session_state.user_message = ""
    st.experimental_rerun()
