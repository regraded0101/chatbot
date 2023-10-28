import streamlit as st
import requests
import pprint
import re

api_key = st.secrets.hf_credentials.hf_api

model_id = "meta-llama/Llama-2-13b-chat-hf"
system_message = """
    You're a helpful assistance from the UKHSA, an organisation that assists with public health emergencies. 
    Keep your responses brief and to the point.
    """

def query(payload, model_id):
	headers = {"Authorization": f"Bearer {api_key}"}
	API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

def prompt_generator(system_message, user_message):
    return f"""
    <s>[INST] <<SYS>>
    {system_message}
    <</SYS>>

    {user_message} [/INST]
    """

# Pattern to clean up text response from API
pattern = r'\[/INST\]\n*([\s\S]+)'





# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input():
    with st.chat_message('user'):
        st.markdown(prompt)
        st.session_state.messages.append({
            "role":"user",
            "content":prompt
        })

    response = query({
        "inputs": prompt_generator(system_message, prompt),
        "parameters": {"max_new_tokens": 500}, 
        }, 
        model_id)
    
    response = response[0]['generated_text']

    # Clean up API response text
    response = re.findall(pattern, response)[0]
    with st.chat_message('assistant'):
        st.markdown(response)
        st.session_state.messages.append({
            "role":"assistant",
            "content":response
        })
