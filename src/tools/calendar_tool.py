import datetime
import os.path
import json
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Permission to READ the calendar
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_next_events():
    creds = None
    
    # 1. Try loading from Secrets (Cloud)
    if "google_calendar" in st.secrets:
        token_data = st.secrets["google_calendar"]["token"]
        # Handle case where it might already be a dict or still a string
        token_info = json.loads(token_data) if isinstance(token_data, str) else token_data
        creds = Credentials.from_authorized_user_info(token_info, SCOPES)
        
    # 2. Try loading from Local File (Only if not on Cloud)
    elif os.path.exists('keys/google_calendar_token.json'):
        creds = Credentials.from_authorized_user_file('keys/google_calendar_token.json', SCOPES)

    # 3. Refresh or Login logic
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # ONLY attempt local login if we are NOT on Streamlit Cloud
            if "google_calendar" not in st.secrets:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'keys/google_calendar_credentials.json', SCOPES)
                creds = flow.run_local_server(port=8080)
                
                # Only try to save the file locally if the folder exists
                if os.path.exists('keys'):
                    with open('keys/google_calendar_token.json', 'w') as token:
                        token.write(creds.to_json())
            else:
                return "Authentication failed: Please check Streamlit Secrets."

    # 4. Fetch the events
    try:
        service = build('calendar', 'v3', credentials=creds)
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=3, singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])

        if not events:
            return "Calendar looks clear for now!"

        event_summaries = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            event_summaries.append(f"- {event['summary']} (Starts: {start})")

        return "Here is what's on the schedule:\n" + "\n".join(event_summaries)

    except Exception as e:
        return f"Error connecting to Google Calendar: {e}"

if __name__ == "__main__":
    # If running locally for testing
    print(get_next_events())