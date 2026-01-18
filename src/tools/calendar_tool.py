import datetime
import os.path
import json
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Permission to READ and MODIFY the calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

# CALENDAR IDS:
CAL_MAIN = "7d514ef304466f0907f53d25c605bf460a375d675c6ca73614920da88bf7ee43@group.calendar.google.com"
CAL_NORMAL_DAYS = "3ca4b2f4b87529b7e45964f6a5524c13f3d0dd6529d40c16f4fb383deb10a40e@group.calendar.google.com"
CAL_AGENT = "bad930e80b21a4aa66511e5f5c19f5af2068363ca3a0db474efdf95a1051ca4d@group.calendar.google.com"


def get_calendar_credentials():
    """Handles authentication and returns valid credentials."""
    creds = None
    
    # 1. Try loading from Streamlit Secrets (Cloud)
    if "google_calendar" in st.secrets:
        token_data = st.secrets["google_calendar"]["token"]
        token_info = json.loads(token_data) if isinstance(token_data, str) else token_data
        creds = Credentials.from_authorized_user_info(token_info, SCOPES)
        
    # 2. Try loading from Local File (Keys folder)
    elif os.path.exists('keys/google_calendar_token.json'):
        creds = Credentials.from_authorized_user_file('keys/google_calendar_token.json', SCOPES)

    # 3. Refresh or Login if necessary
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Only run local server if we aren't in the cloud
            if "google_calendar" not in st.secrets:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'keys/google_calendar_credentials.json', SCOPES)
                creds = flow.run_local_server(port=8080)
                
                if os.path.exists('keys'):
                    with open('keys/google_calendar_token.json', 'w') as token:
                        token.write(creds.to_json())
            else:
                return None
    return creds

def get_next_events():
    """Fetches a summary of upcoming events from the main calendars."""
    creds = get_calendar_credentials()
    if not creds:
        return "Authentication failed: Check Secrets/Keys."

    try:
        service = build('calendar', 'v3', credentials=creds)
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        
        # We check both your personal and work calendars to show availability
        event_summaries = []
        for cal_id in [CAL_MAIN, CAL_NORMAL_DAYS, CAL_AGENT]:
            result = service.events().list(
                calendarId=cal_id, timeMin=now,
                maxResults=2, singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = result.get('items', [])
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                event_summaries.append(f"- {event['summary']} (Starts: {start})")

        if not event_summaries:
            return "Gaby's schedule looks clear for now!"

        return "Current Schedule:\n" + "\n".join(event_summaries)

    except Exception as e:
        return f"Error fetching events: {e}"