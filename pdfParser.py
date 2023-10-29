import PyPDF2
import streamlit as st

@st.cache_resource
def get_pdf_text(filepath):
    # Open the PDF file in read-binary mode
    # Create a PDF object
    pdf = PyPDF2.PdfReader(filepath)
    pdf_text = ' '.join([page.extract_text() for page in pdf.pages])
    return pdf_text

