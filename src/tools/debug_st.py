from stravalib.client import Client
import datetime

# PASTE YOUR SECRETS HERE MANUALLY FOR THIS TEST
CLIENT_ID = "196458"
CLIENT_SECRET = "a45f86d15eb9ba71f2ebe21ea79bde98b4427610"
REFRESH_TOKEN="ec395ac737c0870e811dd8b9fe4c1d3a2e7f34f6"

def test_strava_objects():
    client = Client()
    print("--- 🔍 STRAVA RAW DATA DEBUG ---")
    
    try:
        # 1. Auth
        response = client.refresh_access_token(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            refresh_token=REFRESH_TOKEN
        )
        client.access_token = response['access_token']
        print("✅ Auth Successful!")

        # 2. Get 1 activity
        activities = client.get_activities(limit=1)
        activity_list = list(activities)
        
        if not activity_list:
            print("❌ No activities found in account.")
            return

        activity = activity_list[0]
        m_time = activity.moving_time

        print(f"\n--- ACTIVITY: {activity.name} ---")
        print(f"Object Type: {type(m_time)}")
        print(f"Raw Representation: {repr(m_time)}")
        
        # 3. Test extraction
        print("\n--- TEST RESULTS ---")
        
        # Test 1: Float conversion
        try:
            val = float(m_time)
            print(f"Casting to float: {val} (This is usually total seconds)")
        except Exception as e:
            print(f"Casting to float FAILED: {e}")

        # Test 2: total_seconds()
        try:
            val = m_time.total_seconds()
            print(f"total_seconds(): {val}")
        except Exception as e:
            print(f"total_seconds() FAILED: {e}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_strava_objects()