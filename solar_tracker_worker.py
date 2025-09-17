# workers/star_tracker_worker.py
import threading
import time
import requests
from typing import List

# Import the base class to be a valid worker
from workers.worker_base import WorkerBase

# It's good practice to get the API key from the main config
API_URL = "https://api.astronomyapi.com/api/v2/stars"

class StarTrackerWorker(WorkerBase):
    """
    A worker that fetches live star data for a specific constellation
    from the AstronomyAPI and sends it to the FleetBridge GUI.
    """
    def __init__(self, config: dict):
        super().__init__(config)
        self.api_id = self.global_config.get("api_keys", {}).get("ASTRONOMY_API_ID", "")
        self.api_secret = self.global_config.get("api_keys", {}).get("ASTRONOMY_API_SECRET", "")
        self.auth_token = self._get_auth_token()

    def _get_auth_token(self):
        """Generates the authorization token for AstronomyAPI."""
        if not self.api_id or not self.api_secret:
            self.speak("API ID or Secret is missing. I cannot contact the star database.")
            return None
        try:
            # Note: AstronomyAPI uses Basic Auth with the ID and Secret for this endpoint
            response = requests.post(
                "https://api.astronomyapi.com/api/v2/token",
                auth=(self.api_id, self.api_secret)
            )
            response.raise_for_status()
            return response.json().get("access_token")
        except Exception as e:
            self.speak(f"Could not get authorization token from AstronomyAPI. Error: {e}")
            return None

    def fetch_star_data(self):
        """Fetches the star data using the stored auth token."""
        if not self.auth_token:
            return None
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        payload = {
            "observer": {"latitude": 39.0438, "longitude": -77.4874, "date": time.strftime("%Y-%m-%d")},
            "view": {"type": "constellation", "parameters": {"constellation": "ori"}} # Orion
        }
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.speak(f"API request failed: {e}")
            return None

    def format_for_gui(self, raw_data):
        stars = [{"name": s.get("name"), "ra": s.get("ra"), "dec": s.get("dec"), "mag": s.get("magnitude")} for s in raw_data.get("data", {}).get("table", {}).get("rows", [])]
        return {"source": self.name, "payload": {"stars": stars, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")}, "is_alert": False}

    def send_to_gui(self, data):
        try:
            requests.post("http://127.0.0.1:5555/update", json=data, timeout=2)
            self.speak("Star chart update sent to FleetBridge.")
        except requests.exceptions.RequestException:
            pass # GUI probably isn't open

    def execute_task(self, args: List[str], stop_event: threading.Event):
        """Main loop for the worker."""
        self.speak("Beginning star tracking sequence. I will send updates every 5 minutes.")
        while not stop_event.is_set():
            raw = self.fetch_star_data()
            if raw:
                formatted = self.format_for_gui(raw)
                self.send_to_gui(formatted)
            # Wait for 5 minutes or until a stop signal is received
            stop_event.wait(300)
        self.speak("Star tracking sequence complete.")


# --- THIS IS THE FIX ---
# Replace 'YourWorkerClassName' with the actual class name from this file.
def create_worker(config: dict) -> StarTrackerWorker:
    """Standard entry point for the AI to 'hire' this worker."""
    return StarTrackerWorker(config)
