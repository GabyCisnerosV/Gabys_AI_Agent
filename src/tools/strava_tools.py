import streamlit as st
from stravalib.client import Client
import logging
import datetime

# Keep the logs clean
logging.getLogger().setLevel(logging.ERROR)

@st.cache_data(ttl=600)
def get_strava_stats():
    """
    Connects to Strava and returns complete running data for the AI to search through.
    """
    client = Client()
    
    try:
        # 1. Refresh the connection
        response = client.refresh_access_token(
            client_id=int(st.secrets["strava"]["client_id"]),
            client_secret=st.secrets["strava"]["client_secret"],
            refresh_token=st.secrets["strava"]["refresh_token"]
        )
        client.access_token = response['access_token']
        
        # 2. Get activities from the last year
        one_year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
        activities = client.get_activities(after=one_year_ago)
        
        # 3. Collect all run data
        runs = []
        total_distance = 0
        total_time = 0
        
        for activity in activities:
            if activity.type == 'Run':
                distance_km = float(activity.distance) / 1000
                time_minutes = activity.moving_time.total_seconds() / 60 if activity.moving_time else 0
                pace_min_per_km = time_minutes / distance_km if distance_km > 0 else 0
                date_str = activity.start_date_local.strftime("%d %b %Y")
                
                runs.append({
                    'name': activity.name,
                    'date': date_str,
                    'distance_km': distance_km,
                    'time_minutes': time_minutes,
                    'pace': pace_min_per_km
                })
                
                total_distance += distance_km
                total_time += time_minutes
        
        if not runs:
            return "Gaby hasn't logged any runs in the last year."
        
        # 4. Sort by date (most recent first)
        runs.sort(key=lambda x: x['date'], reverse=True)
        
        # 5. Calculate summary stats
        avg_distance = total_distance / len(runs)
        avg_pace = total_time / total_distance if total_distance > 0 else 0
        longest_run = max(runs, key=lambda x: x['distance_km'])
        
        # 6. Build compact but complete output
        summary = (
            f"📊 RUNNING SUMMARY (Last 12 Months):\n"
            f"Total Runs: {len(runs)} | "
            f"Total Distance: {total_distance:.1f}km | "
            f"Total Time: {total_time/60:.1f}hrs | "
            f"Avg Distance: {avg_distance:.1f}km | "
            f"Avg Pace: {avg_pace:.1f}min/km | "
            f"Longest: {longest_run['distance_km']:.1f}km on {longest_run['date']}\n\n"
            f"COMPLETE RUN LOG (most recent first):\n"
        )
        
        # 7. Add ALL runs in compact format
        for run in runs:
            summary += (
                f"• {run['date']}: {run['name']} - "
                f"{run['distance_km']:.1f}km, {run['time_minutes']:.0f}min, "
                f"{run['pace']:.1f}min/km\n"
            )
        
        return summary

    except Exception as e:
        return f"I tried to check Gaby's Strava, but ran into an error: {e}"