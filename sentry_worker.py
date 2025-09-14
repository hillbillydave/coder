# workers/sentry_worker.py
import threading
import requests
import json

try:
    from workers.worker_base import WorkerBase
except ImportError:
    class WorkerBase:
        def __init__(self, config): self.name = self.__class__.__name__; self.config = config or {}
        def execute_task(self, args, stop_event): raise NotImplementedError

class SentryWorker(WorkerBase):
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "Sentry Risk Analyst"

    def execute_task(self, args: list, stop_event: threading.Event):
        print(f"\n[{self.name}] Accessing JPL Sentry System...")
        try:
            # This is the direct API endpoint for the Sentry data
            url = "https://ssd-api.jpl.nasa.gov/sentry.api"
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            data = response.json()

            if stop_event.is_set(): return
            
            print("\n--- Sentry System: Top 5 Potential Earth Impact Risks ---")
            # The 'data' field contains the list of asteroids
            for asteroid in data.get('data', [])[:5]:
                print(f"\n  Object: {asteroid.get('fullname', 'N/A')}")
                print(f"    Estimated Diameter: {asteroid.get('diameter', 'N/A')} km")
                print(f"    Impact Probability (Cumulative): {asteroid.get('ip', 'N/A')}")
                print(f"    Number of Potential Impacts: {asteroid.get('n_imp', 'N/A')}")
                print(f"    Year Range of Impacts: {asteroid.get('range', 'N/A')}")
            print("\n---------------------------------------------------------")
            print(f"[{self.name}] Analysis complete. Full data is available at https://cneos.jpl.nasa.gov/sentry/")

        except Exception as e:
            print(f"[{self.name}] Drat. I couldn't connect to the Sentry System: {e}")

def create_worker(config: dict):
    return SentryWorker(config)
