import streamlit as st
import requests
import pprint
import re
import pickle
from pdfParser import get_pdf_text

api_key = st.secrets.hf_credentials.hf_api

model_id = "meta-llama/Llama-2-13b-chat-hf"
system_message = """
    Your role is to take PDF documents and extract their raw text into a table format that can be uploaded into a database.
    Return the table only. For example if you need to extract information about a report written on 2nd February 2011 with an author called Jane Mary then return this only: 
    | report_written_date | author_name | \n | --- | --- | \n | 02/02/2011 | Jane Mary |
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
pattern = r".*\[/INST\]([\s\S]*)$"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Include PDF upload ability
pdf_upload = st.file_uploader(
    "Upload a .PDF here",
    type=".pdf",
)

if pdf_upload is not None:
    pdf_text = get_pdf_text(pdf_upload)


if "key_inputs" not in st.session_state:
    st.session_state.key_inputs = {}

col1, col2, col3 = st.columns([3, 3, 2])

with col1:
    key_name = st.text_input("Key/Column Name (e.g. patient_name)", key="key_name")

with col2:
    key_description = st.text_area(
        "*(Optional) Description of key/column", key="key_description"
    )

with col3:
    if st.button("Extract this column"):
        if key_description:
            st.session_state.key_inputs[key_name] = key_description
        else:
            st.session_state.key_inputs[key_name] = "No further description provided"

if st.session_state.key_inputs:
    keys_title = st.write("\nKeys/Columns for extraction:")
    keys_values = st.write(st.session_state.key_inputs)

    if st.button("Extract data!"):
        user_message = f"""
            Use the text provided and denoted by 3 backticks ```{pdf_text}```. 
            Extract the following columns and return a table that could be uploaded to an SQL database. 
            {'; '.join([key + ': ' + st.session_state.key_inputs[key] for key in st.session_state.key_inputs])}
        """
        the_prompt = prompt_generator(
            system_message=system_message, user_message=user_message
        )
        response = query(
            {
                "inputs": the_prompt,
                "parameters": {"max_new_tokens": 500, "temperature": 0.1},
            },
            model_id,
        )
        match = re.search(
            pattern, response[0]["generated_text"], re.MULTILINE | re.DOTALL
        )
        if match:
            response = match.group(1).strip()

        st.markdown(f"Data Extracted!\n{response}")
