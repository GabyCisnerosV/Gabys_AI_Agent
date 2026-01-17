import streamlit as st
from src.tools.strava_tool import get_strava_stats
from src.tools.calendar_tool import get_next_events
import src.tools.ai_tools as ai_t

# 1. Setup & Data
name="Gaby"
cv_path="data/Gaby_CV.pdf"
cv_filename="Gaby_Cisneros_V.pdf"
context_data = {
    f"CV: This is {name}'s updated CV": ai_t.get_cv_text(cv_path),
    f"Strava: {name}'s recent fitness and running stats": get_strava_stats(),
    f"Calendar: {name}'s upcoming availability and meetings": get_next_events()
}
linkedin_user="gabrielacisneros"
github_user="GabyCisnerosV"

personality=f"You are a bubbly agent, you are like {name} PR agent. You are kind, high energy, and always positive. " \
f"You speak in british english. You never lie. You are trying to make people like {name}. "\
f"The first time somebody talks to you introduce yourself as {name}' AI agent and also ask who is talking to you."\
f" If somebody asks, {name} is interested in data science related roles involving AI and new technologies."

agents_description=f"""
### Hi! I'm {name}'s AI Agent! ✨
{name} is a **Data Scientist** based in Manchester, UK. 🐝

I'm not just a chatbot—I'm her 24/7 rep! Apart from knowing {name}'s professional experience 🚀, I am connected in real-time with her **Google Calendar** 📅 and her **Strava** 🏃‍♀️.

**Here are some ideas of things you can ask me:**
* 💃🏽  **Who is {name}?**
* 💼 **What is her professional experience?**
* 🗓️ **Is she free to talk next Friday?**
* ✈️ **What is her next trip?**
* 👟 **What was her last run?**

*Feel free to ask me anything else!*
"""

# 2. Sidebar & Dashboard UI
st.sidebar.title(f"✨ {name}'s CV")
ai_t.download_file_button(path=cv_path,filename=cv_filename,object="CV",name=name)

st.sidebar.write("---") # separator line
st.sidebar.header(f"📣 Connect with {name}")

# Using markdown to create clickable links with icons
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

# 3. Chat interface
st.title(f"🤖 {name}'s Agent")
st.write(agents_description)

# Initialize chat history so it doesn't disappear when you click things
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Say something..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get the AI response using your modular function
    with st.spinner("Give me a sec, I'm thinking..."):
        response = ai_t.get_agent_response(prompt, context_data, personality, name)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
