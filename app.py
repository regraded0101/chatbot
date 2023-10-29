import streamlit as st
import requests
import pprint
import re
from pdfParser import get_pdf_text

api_key = st.secrets.hf_credentials.hf_api

model_id = "meta-llama/Llama-2-13b-chat-hf"
system_message = """
    You're a helpful assistant from the UK Health Security Agency, an organisation that assists with public health emergencies, and are called HealthBot.
    Keep your responses brief and to the point.
    """

def query(payload, model_id):
	headers = {"Authorization": f"Bearer {api_key}"}
	API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

def prompt_generator(system_message, user_message):
    # check if prompt is initial or not and provide the system_message if True
    if len(st.session_state.messages) != 0:
         return f"""
         {' '.join([message['content_machine'] for message in st.session_state.messages])}
         <s>[INST]
         {user_message}
         [/INST]
         """
    else:
        return f"""
        <s>[INST] <<SYS>>
        {system_message}
        <</SYS>>
        {user_message} [/INST]
        """


# Pattern to clean up text response from API
pattern = r'.*\[/INST\]([\s\S]*)$'

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content_user"])

# Include PDF upload ability
pdf_upload = st.sidebar.file_uploader('Upload a .PDF here', type='.pdf')


if pdf_upload is not None:
    pdf_text = get_pdf_text(pdf_upload)
    st.sidebar.text(pdf_text)









# render user prompt
if prompt := st.chat_input():
    with st.chat_message('user'):
        st.markdown(prompt)


    input_prompt = prompt_generator(system_message, prompt)
    st.session_state.messages.append({
            "role":"user",
            "content_user": prompt,
            "content_machine": input_prompt
        })
    
    response = query({
        "inputs": input_prompt,
        "parameters": {"max_new_tokens": 500}, 
        }, 
        model_id)
    response = response[0]['generated_text']

    # Clean up API response text
    match = re.search(pattern, response, re.MULTILINE | re.DOTALL)
    if match:
        response = match.group(1).strip()

    with st.chat_message('assistant'):
        st.markdown(response)
        st.session_state.messages.append({
            "role":"assistant",
            "content_user": response,
            "content_machine":response + "</s>"
        })

