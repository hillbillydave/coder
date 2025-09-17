# workers/worker_base.py
import json
import time
from pathlib import Path

class WorkerBase:
    def __init__(self, config):
        self.config = config
        self.speak(f"{self.__class__.__name__} initialized.", style="info")

    def get_api_key(self, key_name):
        """Retrieve API key case-insensitively from config."""
        api_keys = self.config.get("api_keys", {})
        for key in api_keys:
            if key.lower() == key_name.lower():
                return api_keys[key]
        return ""

    def speak(self, message, style="info"):
        prefix = f"[Worker]" if style == "info" else f"[Worker][{style.upper()}]"
        print(f"{prefix} {message}")
        log_file = Path(__file__).parent / '_studio_log.jsonl'
        with open(log_file, 'a', encoding='utf-8') as f:
            json.dump({"timestamp": time.strftime('%Y-%m-%d %H:%M:%S'), "message": message, "style": style}, f)
            f.write('\n')

    def send_update_to_fleetbridge(self, data):
        queue = self.config.get('shared_data_queue')
        if queue:
            queue.put({"type": "SEPFORECAST_UPDATE", "payload": data})
        else:
            self.speak(f"No shared queue for FleetBridge update: {data}", style="error")

    def execute_task(self, args, stop_event):
        raise NotImplementedError("Subclasses must implement execute_task")
