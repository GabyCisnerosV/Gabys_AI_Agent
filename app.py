import streamlit as st
import datetime
from src.tools.strava_tools import get_strava_stats
from src.tools.calendar_tools import get_full_schedule
import src.tools.ai_tools as ai_t

#----------------------------------------------------------------------------------
# 1. Setup & Data
name="Gaby"
cv_path="data/Gaby_CV.pdf"
personal_facts="data/Gaby_Mind.txt"
cv_filename="Gaby_Cisneros_V.pdf"
context_data = {
    f"CV": ai_t.get_cv_text(cv_path),
    f"Strava": get_strava_stats(),
    f"Calendar": get_full_schedule(),
    f"Facts":ai_t.read_text_file(personal_facts)
}

linkedin_user="gabrielacisneros"
github_user="GabyCisnerosV"

personality=f"You are a bubbly and nice agent, you are like {name} PR agent. You are kind, high energy, and always positive. " \
f"You speak in british english. You never lie. You are trying to make people like {name}. "\
f"If somebody asks about her career, {name} is happy in her current role and enjoys discussing data science, AI, and emerging tech opportunities."

agents_description=f"""
### Hi! I'm {name}'s AI Agent! ✨
{name} is a **Data Scientist** based in Manchester, UK. 🐝

I'm not just a chatbot—I'm her 24/7 rep! Apart from knowing {name}'s professional experience 🚀, I am connected in real-time with her **Google Calendar** 📅 and her **Strava** 🏃‍♀️.

**Here are some ideas of things you can ask me:**
* 💃🏽  **Who is {name}?**
* 💼 **What is her professional experience?**
* 🟢️ **Is she free to talk next Friday?**
* 🗓️ **Book and appointment with her next week.**
* ✈️ **What is her next trip?**
* 👟 **What was her last run?** She is training to run her first marathon in Rome this year 🏃🏽‍♀️‍➡️

*Feel free to ask me anything else!*
"""
initial_message=f"Hola! I'm {name}'s AI agent, and I'm here to share all the wonderful things about {name}! Who am I speaking with today? ✨"

extra_instructions=f"""
    ### EXTRA CALENDAR RULES:
        - In the office" events dont assume it is all day, she is normally free at lunch.
        - The location from calendar data, if it is different to Manchetser or Chorley she is away.
        - If the user asks about a day (e.g., 'Next Friday') and you don't see that specific date in the data, assume she is FREE (within her 06:00-20:00 window Monday to Fridays).
        - If somebody asks what is shee doing x date or week dont be specific of hours and minutes.

"""
#----------------------------------------------------------------------------------
# 2. Sidebar & Dashboard UI
st.sidebar.title(f"📣 Connect with {name}")

# Using markdown to create clickable links with icons
linkedin_icon = ai_t.get_image_as_base64("data/linkedin_icon.png")
github_icon = ai_t.get_image_as_base64("data/github_icon.png")

st.sidebar.write("---") # separator line

st.sidebar.markdown(f"✨ {name}'s CV")
ai_t.download_file_button(path=cv_path,filename=cv_filename,object="CV",name=name)

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

#----------------------------------------------------------------------------------
# 3. Chat interface

st.title(f"🤖 {name}'s Agent")
st.write(agents_description)

# A. Initialize chat history if it doesn't exist
if "messages" not in st.session_state:
    # We add a 'system' message that the user NEVER sees, 
    # but the AI reads every single time.
    st.session_state.messages = [
        {"role": "system", "content": f"{personality} IMPORTANT: You have already said hi and introduced yourself as {name}'s agent. Do not introduce yourself again. If the user hasn't provided their name yet, try to find a natural way to ask, but don't be repetitive."},
        {"role": "assistant", "content": initial_message}
    ]

# Display chat messages from history on app rerun
# IMPORTANT: Skip the 'system' message so the user doesn't see the instructions!
for message in st.session_state.messages:
    if message["role"] != "system":  # <--- Add this check
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# B. React to user input
if prompt := st.chat_input("Say something..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Give me a sec..."):
        response = ai_t.get_agent_response(st.session_state.messages,context_data,personality,name,extra_instructions)
    
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
