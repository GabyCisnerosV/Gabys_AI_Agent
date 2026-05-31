import streamlit as st
from src.tools.strava_tools import get_strava_stats
from src.tools.calendar_tools import get_full_schedule
import src.tools.ai_tools as ai_t
from config import (
    name, cv_path, cv_filename, personal_facts,
    linkedin_user, github_user,
    personality, agents_description, initial_message, extra_instructions
)

# --- Load all context data the AI will use ---
context_data = {
    "CV": ai_t.get_pdf_text(cv_path),
    "Strava": get_strava_stats(),
    "Calendar": get_full_schedule(),
    "Facts": ai_t.read_text_file(personal_facts)
}

# --- Sidebar ---
st.sidebar.markdown(f"📣 Connect with {name}")
linkedin_icon = ai_t.get_image_as_base64("data/linkedin_icon.png")
github_icon = ai_t.get_image_as_base64("data/github_icon.png")

st.sidebar.markdown(
    f"""
    <div style="display: flex; flex-direction: column; gap: 15px;">
        <a href="https://www.linkedin.com/in/{linkedin_user}/" target="_blank" style="text-decoration: none; color: inherit;">
            <img src="data:image/png;base64,{linkedin_icon}" width="25" style="vertical-align:middle;">
            <span style="margin-left: 10px; font-weight: 500;">LinkedIn</span>
        </a>
        <a href="https://github.com/{github_user}" target="_blank" style="text-decoration: none; color: inherit;">
            <img src="data:image/png;base64,{github_icon}" width="25" style="vertical-align:middle;">
            <span style="margin-left: 10px; font-weight: 500;">GitHub</span>
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.write("---")
st.sidebar.markdown(f"✨ {name}'s CV")
ai_t.download_file_button(path=cv_path, filename=cv_filename, object="CV", name=name)

# --- Chat interface ---
st.title(f"🤖 {name}'s Agent")
st.write(agents_description)

# Start the conversation — the system message is hidden from the user, only the AI sees it
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": f"{personality} IMPORTANT: You have already said hi and introduced yourself as {name}'s agent. Do not introduce yourself again. If the user hasn't provided their name yet, try to find a natural way to ask, but don't be repetitive."},
        {"role": "assistant", "content": initial_message}
    ]

# Show the chat history — skip the system message so the user only sees the actual conversation
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Handle new user messages
if prompt := st.chat_input("Say something..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Give me a sec..."):
        response = ai_t.get_agent_response(st.session_state.messages, context_data, personality, name, extra_instructions)

    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
