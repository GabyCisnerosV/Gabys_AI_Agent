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
    
    # --- STEP 1: LOAD CREDENTIALS ---
    # Check if we are running on Streamlit Cloud (using Secrets)
    if "google_calendar" in st.secrets:
        # We store the google_calendar_token.json content inside a secret called 'token'
        token_info = json.loads(st.secrets["google_calendar"]["token"])
        creds = Credentials.from_authorized_user_info(token_info, SCOPES)
        
    # If not on Cloud, check for local google_calendar_token.json file
    elif os.path.exists('keys/google_calendar_token.json'):
        creds = Credentials.from_authorized_user_file('keys/google_calendar_token.json', SCOPES)

    # --- STEP 2: REFRESH OR LOGIN ---
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # THIS ONLY WORKS LOCALLY
            # Ensure your .streamlit/google_calendar_credentials.json is correct
            flow = InstalledAppFlow.from_client_secrets_file(
                'keys/google_calendar_credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        
        # Save the token locally (helps for the very first time you run it)
        with open('keys/google_calendar_token.json', 'w') as token:
            token.write(creds.to_json())

    # --- STEP 3: FETCH EVENTS ---
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