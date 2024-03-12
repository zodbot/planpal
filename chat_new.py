import os

import streamlit as st
from dotenv import load_dotenv
import openai

# Display the current working directory in the Streamlit app
st.write(f"I am your PlanPal! ")

# Load environment variables from .env file
load_dotenv(".env")

# Ensure your OpenAI API key is loaded from the environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

from planpal_agent import llm
from planpal_agent.plan_pal import PlanPalAssistant


# Function to mimic processing and responding to a message
def process_message(message, context=""):
    llm_client = llm.client  # Assuming llm.client is already defined and configured
    planpal_assistant = PlanPalAssistant(llm_client)
    new_response = planpal_assistant.process_user_request(message, context)
    return new_response


# Creating a session state to store chat history and define context window size
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
context_window_size = 5  # Define the size of the context window

# Chat UI
st.title('PlanPal')

# Join all messages in chat_history and display in a single text_area
print("********************************")
print(st.session_state['chat_history'])
# if
# chat_display = "\n".join(st.session_state['chat_history'][-1])
# Join all messages in chat_history and display in a single text_area
chat_display = ""
if st.session_state['chat_history']:
    chat_display = f"{st.session_state['chat_history'][-1]['role'].capitalize()}: {st.session_state['chat_history'][-1]['content']}"

    # chat_display = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state['chat_history']])
st.text_area("Chat", value=chat_display, height=300, disabled=True)

# Input for new message
user_message = st.text_input("Type your message here...", "")


# Example dictionary format for each message: {'sender': 'user', 'content': 'Hi there!', 'timestamp': '2023-03-10T12:34:56'}

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

context_window_size = 5  # This represents the number of messages from history to consider as context

# Button to send message
send_button = st.button('Send')

# Assuming user_message is obtained from Streamlit input
if send_button and user_message:
    # Construct context from the recent chat history
    context = st.session_state['chat_history']

    # Process the user message along with the context
    # Here, it's assumed that process_message and the PlanPalAssistant are adjusted to work with the context as a list of dictionaries
    response_dict = process_message(user_message, context)

    # Add the user message to chat history
    # st.session_state['chat_history'].append({'sender': 'user', 'content': user_message,
    #                                          'timestamp': '2023-03-10T12:34:56'})  # Adjust timestamp as necessary

    # Add the PlanPal response to chat history
    st.session_state['chat_history'] = []
    for d in response_dict:
        st.session_state['chat_history'].append(d)  # Assuming response_dict is correctly formatted

    # Trigger a rerun to refresh the UI with the updated chat history
    st.experimental_rerun()
    # Join all messages in chat_history for display, extracting 'content' from each dictionary
    # chat_display = "\n".join(
    #     [f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state['chat_history']])
    if st.session_state['chat_history']:
        chat_display = f"{st.session_state['chat_history'][-1]['role'].capitalize()}: {st.session_state['chat_history'][-1]['content']}"
    st.text_area("Chat", value=chat_display, height=300, disabled=True)

