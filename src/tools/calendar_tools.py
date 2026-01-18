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

    now = datetime.datetime.now(datetime.timezone.utc)
    start_iso = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    end_iso = (now + datetime.timedelta(days=days)).isoformat()

    combined_events = []
    
    # Check all three calendars
    for cal_id in [CAL_MAIN, CAL_NORMAL_DAYS, CAL_AGENT]:
        try:
            result = service.events().list(
                calendarId=cal_id, 
                timeMin=start_iso, 
                timeMax=end_iso,
                singleEvents=True, 
                orderBy='startTime'
            ).execute()
            
            items = result.get('items', [])
            for event in items:
                start_raw = event['start'].get('dateTime', event['start'].get('date'))
                # Handle different date formats from Google API
                if 'T' in start_raw:
                    dt = datetime.datetime.fromisoformat(start_raw.replace('Z', '+00:00'))
                else:
                    dt = datetime.datetime.strptime(start_raw, '%Y-%m-%d')

                # Critical: Include Day, Date, Year, and Time
                friendly_date = dt.strftime("%A, %d %B %Y at %H:%M") 
                
                summary = "Private Appointment" if cal_id == CAL_AGENT else event.get('summary', 'Busy')
                combined_events.append(f"- {summary} ({friendly_date})")
        except Exception as e:
            # If one calendar fails, we continue to the next
            continue

    # Sort events by date so the AI sees them in chronological order
    combined_events.sort(key=lambda x: x.split('(')[-1])

    return "\n".join(combined_events) if combined_events else "Gaby has no scheduled events."

@st.cache_data(ttl=600)
def schedule_meeting(start_time_iso, duration_minutes, visitor_name, visitor_email, description):
    creds = get_calendar_credentials()
    if not creds: return "Calendar access denied."

    try:
        service = build('calendar', 'v3', credentials=creds)
        
        # Clean the ISO string
        if start_time_iso.endswith('Z'):
            start_dt = datetime.datetime.fromisoformat(start_time_iso.replace('Z', '+00:00'))
        else:
            start_dt = datetime.datetime.fromisoformat(start_time_iso)
            
        end_dt = start_dt + datetime.timedelta(minutes=int(duration_minutes))
        
        #ISO format
        start_iso = start_dt.isoformat()
        if not start_iso.endswith('Z') and '+' not in start_iso:
            start_iso += 'Z'
            
        end_iso = end_dt.isoformat()
        if not end_iso.endswith('Z') and '+' not in end_iso:
            end_iso += 'Z'

        # Conflict check across all calendars
        for cal_id in [CAL_MAIN, CAL_NORMAL_DAYS, CAL_AGENT]:
            check = service.events().list(
                calendarId=cal_id, 
                timeMin=start_iso, 
                timeMax=end_iso,
                singleEvents=True
            ).execute()
            
            if check.get('items'):
                return "Gaby is busy at that time. Try another slot!"

        # Create Event
        event_body = {
            'summary': f'Meeting with {visitor_name}',
            'description': f"{description}\n\nBooked with Gaby's AI Agent ✨.",
            'start': {'dateTime': start_iso, 'timeZone': 'Europe/London'},
            'end': {'dateTime': end_iso, 'timeZone': 'Europe/London'},
            'attendees': [{'email': visitor_email}],
        }
        
        service.events().insert(calendarId=CAL_AGENT, body=event_body, sendUpdates='all').execute()
        return f"All set! Invite sent to {visitor_email}."
    except Exception as e:
        return f"Booking error: {e}"