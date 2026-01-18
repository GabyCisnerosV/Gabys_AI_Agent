import streamlit as st
from stravalib.client import Client
import logging

# Keep the logs clean
logging.getLogger().setLevel(logging.ERROR)

def get_strava_stats():
    """
    Connects to Strava and returns a string summarizing Gaby's latest activity.
    """
    client = Client()
    
    try:
        # 1. Refresh the connection using secrets
        response = client.refresh_access_token(
            client_id=int(st.secrets["strava"]["client_id"]),
            client_secret=st.secrets["strava"]["client_secret"],
            refresh_token=st.secrets["strava"]["refresh_token"]
        )
        client.access_token = response['access_token']
        
        # 2. Get the last activity
        activities = client.get_activities(limit=1)
        
        # List to handle the generator safely
        act_list = list(activities)
        if not act_list:
            return "Gaby hasn't logged any runs lately. Time to lace up!"
            
        last_act = act_list[0]
        distance_km = float(last_act.distance) / 1000
        
        return f"Gaby's latest activity was '{last_act.name}': a {distance_km:.2f}km run!"

    except Exception as e:
        return f"I tried to check Gaby's Strava, but ran into an error: {e}"