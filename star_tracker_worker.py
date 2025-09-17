# workers/star_tracker_worker.py
from workers.worker_base import WorkerBase
import threading
import time
import requests
import random
try:
    from skyfield.api import load
except ImportError as e:
    load = None
    print(f"[StarTracker] Import error: {e}")

class StarTrackerWorker(WorkerBase):
    def __init__(self, config):
        super().__init__(config)
        self.nasa_key = self.get_api_key("nasa_neo_key")
        if not load:
            self.speak("WARNING: skyfield library not found. Install with 'pip install skyfield'.", style="error")
        if not self.nasa_key or "your-actual" in self.nasa_key:
            self.speak("WARNING: Missing or invalid NASA_NEO_KEY. Using simulated data.", style="warning")

    def execute_task(self, args, stop_event):
        if not load or not self.nasa_key or "your-actual" in self.nasa_key:
            self.speak("Using simulated star data due to missing skyfield or NASA API key.", style="warning")
            while not stop_event.is_set():
                self.speak("Simulating star tracking...", style="dim")
                data = {
                    "source": "StarTracker",
                    "payload": {
                        "stars": [{"name": f"Star-{i}", "ra": random.uniform(0, 360), "dec": random.uniform(-90, 90), "mag": random.uniform(1, 10)} for i in range(10)],
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
                    },
                    "is_alert": False
                }
                self.send_to_gui(data)
                stop_event.wait(300)
            return
        self.speak("Tracking stars with NASA API...")
        while not stop_event.is_set():
            try:
                url = f"https://api.nasa.gov/neo/rest/v1/feed?api_key={self.nasa_key}"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                raw_data = response.json()
                stars = [
                    {"name": neo.get("name"), "ra": random.uniform(0, 360), "dec": random.uniform(-90, 90), "mag": neo.get("absolute_magnitude_h", 10)}
                    for neo in raw_data.get("near_earth_objects", {}).get(time.strftime("%Y-%m-%d"), [])
                ]
                data = {
                    "source": "StarTracker",
                    "payload": {"stars": stars, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")},
                    "is_alert": False
                }
                self.send_to_gui(data)
                self.speak("Fetching star data...", style="dim")
            except requests.exceptions.RequestException as e:
                self.speak(f"Error fetching star data: {e}", style="error")
            stop_event.wait(300)

    def send_to_gui(self, data):
        try:
            requests.post("http://127.0.0.1:5001/update", json=data, timeout=2)
            self.speak("Star chart update sent to FleetBridge.")
        except requests.exceptions.RequestException:
            pass  # GUI probably isn't open

def create_worker(config):
    return StarTrackerWorker(config)
