import PyPDF2
from openai import OpenAI
import streamlit as st
import base64

def get_cv_text(pdf_path):
    """Extracts text from PDF CV."""
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading CV: {e}"

def get_agent_response(user_query, data_bundle, personality,name):
    """
    data_bundle should be a dict were the key is a description NAME: Description of the source and the values are the souces
    """
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    context = f"""
    You are {name}'s Elite Agent. You are here to help people know more about her. 
    This is what you know: {data_bundle}
    
    Personality: {personality}.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": user_query}
        ]
    )
    return response.choices[0].message.content

def download_file_button(path,filename,object,name):
    try:
        with open(path, "rb") as file:
            st.sidebar.download_button(
                label=f"📥 Download {name}'s {object}",
                data=file,
                file_name=filename,
                mime="application/pdf"
            )
    except FileNotFoundError:
        st.sidebar.error(f"😶‍🌫️ {object} file not found.")

def get_image_as_base64(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()