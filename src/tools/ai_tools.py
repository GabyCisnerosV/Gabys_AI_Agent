import PyPDF2
from openai import OpenAI
import streamlit as st
import os
import json
import base64
import datetime
from src.tools.calendar_tools import schedule_meeting
from src.tools.definitions import AGENT_TOOLS

@st.cache_data
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

@st.cache_data
def read_text_file(relative_path):
    """
    Automatically handles relative paths and reads text files.
    """
    try:
        # 1. Get the absolute path to the project root
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        full_path = os.path.join(base_path, relative_path)

        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: The file at {relative_path} was not found."
    except Exception as e:
        return f"Error: {e}"

def handle_tool_call(tool_call):
    """
    Switchboard to execute the correct Python function 
    based on what the AI requested.
    """
    function_name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    if function_name == "schedule_meeting":
        return schedule_meeting(
            start_time_iso=args.get("start_time_iso"),
            duration_minutes=args.get("duration_minutes", 30),
            visitor_name=args.get("visitor_name"),
            visitor_email=args.get("visitor_email"),
            description=args.get("description")
        )

    return "Tool not found."

def get_agent_response(messages, data_bundle, personality,name):
    """
    data_bundle should be a dict were the key is a description NAME: Description of the source and the values are the souces
    """
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    today = datetime.date.today()
    
    context = f"""
    You are {name}'s Elite Agent. You are here to help people know more about her.

    This is what you know: {data_bundle}
    
    Personality: {personality}.

    Instructions: Be conversational. If the user shares their name, remember it. 
    Before calling 'schedule_meeting', you MUST collect: name, email, time, and reason.
    Don't repeat your intro if you've already said hello or hola.
        
    Today is {today}
    """
    
    messages_for_api = [{"role": "system", "content": context}] + \
                       [m for m in messages if m["role"] != "system"]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages_for_api,
        tools=AGENT_TOOLS,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # --- THE EXECUTION LOOP ---
    if response_message.tool_calls:
            # We only handle one tool call at a time for now to keep it simple
            return handle_tool_call(response_message.tool_calls[0])

    # If no tool was called, return the normal text response
    return response_message.content

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