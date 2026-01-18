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
        # 1. Refresh the connection
        response = client.refresh_access_token(
            client_id=int(st.secrets["strava"]["client_id"]),
            client_secret=st.secrets["strava"]["client_secret"],
            refresh_token=st.secrets["strava"]["refresh_token"]
        )
        client.access_token = response['access_token']
        
        # 2. Get activities from the last year
        # Strava API expects 'after' to be a datetime object or epoch
        one_year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
        activities = client.get_activities(after=one_year_ago)
        
        # 3. Collect data in a list FIRST
        runs = []
        
        # Iterating through the Strava results
        for activity in activities:
            # Check for 'Run' (Standard Strava type)
            if activity.type == 'Run':
                # Convert distance from meters to km safely
                dist_m = float(activity.distance) if activity.distance else 0
                distance_km = dist_m / 1000
                
                # Handle moving time (stravalib returns a timedelta-like object)
                if activity.moving_time:
                    # total_seconds() is the most reliable way to get time
                    time_minutes = activity.moving_time.total_seconds() / 60
                else:
                    time_minutes = 0
                
                pace_min_per_km = time_minutes / distance_km if distance_km > 0 else 0
                
                # We store the raw datetime object for sorting later, and the string for display
                runs.append({
                    'name': activity.name,
                    'raw_date': activity.start_date_local, 
                    'date_str': activity.start_date_local.strftime("%d %b %Y"),
                    'distance_km': distance_km,
                    'time_minutes': time_minutes,
                    'pace': pace_min_per_km
                })
        
        if not runs:
            return "Gaby hasn't logged any runs in the last year."
        
        # 4. Sort by raw datetime (most recent first)
        runs.sort(key=lambda x: x['raw_date'], reverse=True)
        
        # 5. Calculate summary stats
        total_distance = sum(r['distance_km'] for r in runs)
        total_time_mins = sum(r['time_minutes'] for r in runs)
        avg_distance = total_distance / len(runs)
        avg_pace = total_time_mins / total_distance if total_distance > 0 else 0
        longest_run = max(runs, key=lambda x: x['distance_km'])
        
        # 6. Build the summary output
        summary = (
            f"📊 **STRAVA RUNNING SUMMARY (Last 12 Months)**\n"
            f"• Total Runs: {len(runs)}\n"
            f"• Total Distance: {total_distance:.1f}km\n"
            f"• Total Time: {total_time_mins/60:.1f} hours\n"
            f"• Avg Distance: {avg_distance:.1f}km | Avg Pace: {avg_pace:.1f} min/km\n"
            f"• Longest Run: {longest_run['distance_km']:.1f}km on {longest_run['date_str']}\n\n"
            f"**RECENT RUN LOG:**\n"
        )
        
        # 7. Add runs (Limiting to top 50 to avoid hitting AI token limits if she runs a lot!)
        for run in runs[:50]:
            summary += (
                f"🏃 {run['date_str']}: {run['name']} — "
                f"{run['distance_km']:.1f}km, {run['time_minutes']:.0f}m, "
                f"({run['pace']:.1f} min/km)\n"
            )
            
        return summary

    except Exception as e:
        return f"Strava Error: {e}"