import time
import requests
import threading

API_URL = "https://api.astronomyapi.com/api/v2/stars"
API_HEADERS = {
    "Authorization": "Bearer YOUR_API_TOKEN",  # Replace with your AstronomyAPI token
    "Content-Type": "application/json"
}

def fetch_star_data():
    # Example payload for AstronomyAPI — adjust based on your subscription level
    payload = {
        "observer": {
            "latitude": 39.0438,
            "longitude": -77.4874,
            "date": time.strftime("%Y-%m-%d"),
            "time": time.strftime("%H:%M:%S")
        },
        "view": {
            "type": "constellation",
            "parameters": {
                "constellation": "Orion"
            }
        }
    }

    try:
        response = requests.post(API_URL, headers=API_HEADERS, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[StarTracker] API error: {response.status_code}")
    except Exception as e:
        print(f"[StarTracker] Request failed: {e}")
    return None

def format_for_gui(raw_data):
    stars = []
    for obj in raw_data.get("data", {}).get("stars", []):
        stars.append({
            "name": obj.get("name"),
            "ra": obj.get("rightAscension"),
            "dec": obj.get("declination"),
            "mag": obj.get("magnitude")
        })
    return {
        "source": "StarTracker",
        "payload": {
            "stars": stars,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        },
        "is_alert": False
    }

def send_to_gui(data):
    try:
        requests.post("http://127.0.0.1:5555/update", json=data)
        print("[StarTracker] Update sent to GUI.")
    except Exception as e:
        print(f"[StarTracker] Failed to send update: {e}")

def run_star_tracker():
    while True:
        raw = fetch_star_data()
        if raw:
            formatted = format_for_gui(raw)
            send_to_gui(formatted)
        time.sleep(300)  # Poll every 5 minutes

if __name__ == "__main__":
    print("[StarTracker] Starting worker...")
    threading.Thread(target=run_star_tracker, daemon=True).start()

