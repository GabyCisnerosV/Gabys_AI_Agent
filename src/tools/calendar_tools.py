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

# Pulling IDs from Secrets
CAL_MAIN = st.secrets["calendar_selection"]["cal_main"]
CAL_NORMAL_DAYS = st.secrets["calendar_selection"]["cal_normal_days"]
CAL_AGENT = st.secrets["calendar_selection"]["cal_agent"]

@st.cache_data(ttl=600)
def get_calendar_credentials():
    """Handles authentication and returns valid credentials."""
    creds = None
    if "google_calendar" in st.secrets:
        token_data = st.secrets["google_calendar"]["token"]
        token_info = json.loads(token_data) if isinstance(token_data, str) else token_data
        creds = Credentials.from_authorized_user_info(token_info, SCOPES)
    elif os.path.exists('keys/google_calendar_token.json'):
        creds = Credentials.from_authorized_user_file('keys/google_calendar_token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
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


@st.cache_data(ttl=600)
def get_full_schedule(days=90):
    creds = get_calendar_credentials()
    if not creds: return "Calendar access unavailable."
    
    service = build('calendar', 'v3', credentials=creds)
    now = datetime.datetime.utcnow()
    # Start from the beginning of today
    start_iso = now.replace(hour=0, minute=0, second=0).isoformat() + 'Z'
    end_iso = (now + datetime.timedelta(days=days)).isoformat() + 'Z'

    combined_events = []
    for cal_id in [CAL_MAIN, CAL_NORMAL_DAYS, CAL_AGENT]:
        result = service.events().list(
            calendarId=cal_id, timeMin=start_iso, timeMax=end_iso,
            singleEvents=True, orderBy='startTime'
        ).execute()
        
        for event in result.get('items', []):
            start_raw = event['start'].get('dateTime', event['start'].get('date'))
            dt = datetime.datetime.fromisoformat(start_raw.replace('Z', ''))

            friendly_date = dt.strftime("%A, %b %d at %H:%M")
            summary = "Private Appointment" if cal_id == CAL_AGENT else event.get('summary', 'Busy')
            
            combined_events.append(f"- {summary} ({friendly_date})")

    return "\n".join(combined_events) if combined_events else "No scheduled events."

@st.cache_data(ttl=600)
def schedule_meeting(start_time_iso, duration_minutes, visitor_name, visitor_email, description):
    """Books an appointment after checking all calendars for conflicts."""
    creds = get_calendar_credentials()
    if not creds: return "Calendar access denied."

    try:
        service = build('calendar', 'v3', credentials=creds)
        start_dt = datetime.datetime.fromisoformat(start_time_iso.replace('Z', ''))
        # Using timedelta correctly
        end_dt = start_dt + datetime.timedelta(minutes=int(duration_minutes))
        end_time_iso = end_dt.isoformat() + 'Z'

        # Conflict check
        for cal_id in [CAL_MAIN, CAL_NORMAL_DAYS, CAL_AGENT]:
            check = service.events().list(calendarId=cal_id, timeMin=start_time_iso, timeMax=end_time_iso).execute()
            if check.get('items'):
                return "Gaby is busy at that time. Try another slot!"

        # Create Event
        event_body = {
            'summary': f'Meeting with {visitor_name}',
            'description': f"{description}\n\nBooked via AI Agent.",
            'start': {'dateTime': start_time_iso, 'timeZone': 'Europe/London'},
            'end': {'dateTime': end_time_iso, 'timeZone': 'Europe/London'},
            'attendees': [{'email': visitor_email}],
        }
        
        service.events().insert(calendarId=CAL_AGENT, body=event_body, sendUpdates='all').execute()
        return f"All set! Invite sent to {visitor_email}."
    except Exception as e:
        return f"Booking error: {e}"