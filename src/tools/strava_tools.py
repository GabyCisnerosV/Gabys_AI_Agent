import streamlit as st
from stravalib.client import Client
import logging
import datetime

# Keep the logs clean
logging.getLogger().setLevel(logging.ERROR)

@st.cache_data(ttl=600)
def get_strava_stats():
    client = Client()
    try:
        response = client.refresh_access_token(
            client_id=int(st.secrets["strava"]["client_id"]),
            client_secret=st.secrets["strava"]["client_secret"],
            refresh_token=st.secrets["strava"]["refresh_token"]
        )
        client.access_token = response['access_token']
        
        one_year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
        activities = client.get_activities(after=one_year_ago)
        
        runs = []
        for activity in activities:
            if activity.type == 'Run':
                dist_km = float(activity.distance) / 1000 if activity.distance else 0
                
                # --- THE DURATION FIX ---
                m_time = activity.moving_time
                if m_time is not None:
                    if hasattr(m_time, 'total_seconds'):
                        time_minutes = m_time.total_seconds() / 60
                    else:
                        try:
                            time_minutes = float(m_time) / 60
                        except:
                            time_minutes = getattr(m_time, 'seconds', 0) / 60
                else:
                    time_minutes = 0
                # -----------------------

                pace = time_minutes / dist_km if dist_km > 0 else 0
                runs.append({
                    'name': activity.name,
                    'date': activity.start_date_local.strftime("%d %b %Y"),
                    'km': dist_km,
                    'mins': time_minutes,
                    'pace': pace,
                    'raw_date': activity.start_date_local
                })

        if not runs: 
            return "Gaby hasn't logged any runs in the last year."
        
        # Sort so the newest runs are at the top
        runs.sort(key=lambda x: x['raw_date'], reverse=True)

        # 1. CALCULATE TOTALS
        total_km = sum(r['km'] for r in runs)
        total_runs = len(runs)
        longest_run = max(runs, key=lambda x: x['km'])
        total_hours = sum(r['mins'] for r in runs) / 60

        # 2. BUILD THE OUTPUT TEXT
        # We start with the summary headers
        output = (
            f"📊 GABY'S RUNNING DATA (LAST 12 MONTHS):\n"
            f"- Total Distance: {total_km:.1f} km\n"
            f"- Total Runs: {total_runs}\n"
            f"- Total Time: {total_hours:.1f} hours\n"
            f"- Longest Run: {longest_run['km']:.1f} km on {longest_run['date']}\n\n"
            f"DETAILED RUN LOG:\n"
        )

        # 3. ADD EVERY RUN (Limiting to top 100 to keep AI tokens safe)
        for r in runs[:100]:
            output += f"• {r['date']}: {r['name']} | {r['km']:.2f}km | Pace: {r['pace']:.2f} min/km\n"
        
        return output

    except Exception as e:
        return f"Strava logic error: {str(e)}"