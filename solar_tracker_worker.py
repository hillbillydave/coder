# workers/solar_tracker_worker.py
import time
import requests
import json
from datetime import datetime

FLEETBRIDGE_ENDPOINT = "http://127.0.0.1:5555/update"
CONFIG_PATH = "config/solar_apis.json"
ALERT_PATH = "config/solar_alerts.json"

# Default alert thresholds
DEFAULT_ALERTS = {
    "flux": { "warn": 150, "critical": 200 },
    "sunspots": { "warn": 80, "critical": 120 },
    "solarWind": {
        "speed": { "warn": 500, "critical": 700 },
        "density": { "warn": 6, "critical": 10 }
    },
    "geomagneticIndex": { "warn": 5, "critical": 7 }
}

POLL_INTERVAL = 60  # seconds

def load_api_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
            return config.get("apis", [])
    except Exception as e:
        print(f"[SolarTracker] Failed to load API config: {e}")
        return []

def load_alert_config():
    try:
        with open(ALERT_PATH, "r") as f:
            user_config = json.load(f)
            return { **DEFAULT_ALERTS, **user_config }
    except Exception:
        return DEFAULT_ALERTS

def fetch_from_api(api):
    try:
        response = requests.get(api["url"], params=api.get("params", {}), timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[SolarTracker] API {api['name']} returned {response.status_code}")
    except Exception as e:
        print(f"[SolarTracker] Error fetching from {api['name']}: {e}")
    return {}

def evaluate_alerts(data, config):
    alerts = []

    def check(metric, value, thresholds):
        if value >= thresholds.get("critical", float("inf")):
            alerts.append(f"{metric} CRITICAL: {value}")
        elif value >= thresholds.get("warn", float("inf")):
            alerts.append(f"{metric} WARNING: {value}")

    check("flux", data.get("flux", 0), config.get("flux", {}))
    check("sunspots", data.get("sunspots", 0), config.get("sunspots", {}))

    sw = data.get("solarWind", {})
    check("solarWind.speed", sw.get("speed", 0), config.get("solarWind", {}).get("speed", {}))
    check("solarWind.density", sw.get("density", 0), config.get("solarWind", {}).get("density", {}))

    if "geomagneticIndex" in data:
        check("geomagneticIndex", data["geomagneticIndex"], config.get("geomagneticIndex", {}))

    return alerts

def format_payload(raw_data, source_name, alert_config):
    alerts = evaluate_alerts(raw_data, alert_config)
    return {
        "source": "SolarTracker",
        "payload": {
            "sourceName": source_name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": raw_data,
            "alerts": alerts
        },
        "is_alert": bool(alerts)
    }

def send_to_gui(payload):
    try:
        requests.post(FLEETBRIDGE_ENDPOINT, json=payload)
        print(f"[SolarTracker] Sent update from {payload['payload']['sourceName']}")
    except Exception as e:
        print(f"[SolarTracker] Failed to send update: {e}")

def run_tracker():
    print("[SolarTracker] Worker online. Smart polling active.")
    apis = load_api_config()

    while True:
        alert_config = load_alert_config()
        for api in apis:
            raw = fetch_from_api(api)
            if raw:
                payload = format_payload(raw, api["name"], alert_config)
                send_to_gui(payload)
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    run_tracker()

