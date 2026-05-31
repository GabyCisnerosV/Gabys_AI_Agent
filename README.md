# 🤖 Gaby’s AI Agent

This is my personal AI rep. My agent is available 24/7 and, apart from knowing about my professional experience, it keeps an eye on my Strava runs, checks my calendar, and can even book meetings for me.

## ✨ What does it do?
- Answers questions about my background, projects, and work experience.
- Knows exactly how my marathon training is going (slow, but consistent! 💪).
- Checks my real-time availability and books meetings directly into my calendar.
- **Continuous Learning:** I'm looking to add more capabilities over time!



## 🛠️ How was it built?
Built with **Streamlit** and **GPT-4o**. It connects to **Strava** for running stats and **Google Calendar** for scheduling. The agent utilizes OpenAI's **Function Calling** to execute real actions rather than just simulating them.

### Try asking it:
* 🏃‍♀️ *"What's Gaby been up to lately?"*
* 👟 *"How far did she run last week?"*
* 📅 *"Is she free Thursday afternoon?"*
* ☕ *"Book a 30min chat next Tuesday at 2pm"*

The agent will remember your name, check for calendar conflicts (including travel and office days), and ensure I'm never double-booked.



## 🚀 Making your own
1. Clone the repo and swap out the details in `config.py` — that's where the name, social links, personality, and prompts all live.
2. Replace the data files in `/data` with your own CV and personal facts file.
3. You'll need API keys for OpenAI, Strava, and Google Calendar.

### Configuration
Place your credentials in `.streamlit/secrets.toml`:

```toml
OPENAI_API_KEY = "your-key-here"

[strava]
client_id = "your-strava-id"
client_secret = "your-strava-secret"
refresh_token = "your-refresh-token"

[calendar_selection]
cal_main = "your-main-calendar"
cal_normal_days = "your-normal-days-calendar"
cal_agent = "your-agent-calendar"

[google_calendar]
token = '''your-google-token-json'''
