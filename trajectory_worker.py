# workers/trajectory_worker.py
import threading
import time
import requests
import math
from queue import Empty
from pathlib import Path
from skyfield.api import load, Loader
from skyfield.framelib import ecliptic_frame

try:
    from workers.worker_base import WorkerBase
except ImportError:
    class WorkerBase:
        def __init__(self, config): self.name = self.__class__.__name__; self.config = config or {}
        def execute_task(self, args, stop_event): raise NotImplementedError

class TrajectoryWorker(WorkerBase):
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "Trajectory Analyst"
        self.shared_queue = self.config.get("shared_data_queue")
        
        try:
            data_path = Path(__file__).parent.parent / "skyfield_cache"
            self.loader = Loader(data_path)
            self.ts = self.loader.timescale()
            self.eph = self.loader('de421.bsp')
            self.sun = self.eph['sun']
            print(f"[{self.name}] Initialized and ready for plotting requests.")
        except Exception as e:
            print(f"[{self.name}] ERROR: Could not initialize calculator engine. {e}")
            self.eph = None

    def _send_status_update(self, message: str):
        if self.shared_queue:
            self.shared_queue.put({"type": "STATUS_UPDATE", "payload": {"message": message}})
            time.sleep(0.1)

    # --- THIS IS THE FINAL, CORRECTED PLOTTING FUNCTION ---
    def _plot_neo_path(self, object_id: str):
        try:
            self._send_status_update(f"Request received. Contacting JPL Sentry for '{object_id}'...")
            
            # Use the correct Sentry API endpoint that you discovered
            url = f"https://ssd-api.jpl.nasa.gov/sentry.api?des={object_id.replace(' ', '%20')}"
            
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()

            # The Sentry API has a different structure
            if "summary" not in data:
                error_msg = data.get("error", f"No data found for '{object_id}'.")
                self._send_status_update(f"Error: {error_msg}")
                return

            summary = data["summary"]
            fullname = summary.get("fullname", object_id)
            self._send_status_update(f"Data received for {fullname}. Calculating trajectory...")
            
            # We need to fetch the full orbital elements from the main sbdb api now
            sbdb_url = f"https://ssd-api.jpl.nasa.gov/sbdb.api?sstr={object_id.replace(' ', '%20')}&orb=1"
            sbdb_response = requests.get(sbdb_url, timeout=15)
            sbdb_response.raise_for_status()
            sbdb_data = sbdb_response.json()
            
            if "orb" not in sbdb_data or "elements" not in sbdb_data['orb']:
                 self._send_status_update(f"Error: Could not retrieve orbital elements for '{fullname}'.")
                 return
            
            elements = sbdb_data['orb']['elements']
            orbit = self.eph.orbit(
                self.ts.J(float(elements['epoch']['value'])),
                frame=ecliptic_frame,
                e=float(elements['e']['value']),
                a_au=float(elements['a']['value']),
                inc_degrees=float(elements['i']['value']),
                node_degrees=float(elements['om']['value']),
                argp_degrees=float(elements['w']['value']),
                ma_degrees=float(elements['ma']['value'])
            )

            path_points = []
            SCENE_SCALE_AU = 150.0 
            today = time.gmtime()
            
            for day_offset in range(0, 366, 5):
                future_time = self.ts.utc(today.tm_year, today.tm_mon, today.tm_mday + day_offset)
                x, y, z = orbit.at(future_time).ecliptic_xyz().au
                path_points.append({"x": x * SCENE_SCALE_AU, "y": z * SCENE_SCALE_AU, "z": -y * SCENE_SCALE_AU})
            
            self._send_status_update(f"Calculation complete. Rendering path for {fullname}...")
            path_data = { "id": fullname, "path": path_points }
            if self.shared_queue:
                self.shared_queue.put({"type": "PATH_DATA_UPDATE", "payload": path_data})

        except requests.exceptions.HTTPError as http_err:
            error_message = f"JPL API returned an error: {http_err}"
            self._send_status_update(error_message)
            print(f"[{self.name}] CRITICAL ERROR during plot: {http_err}")
        except Exception as e:
            error_message = f"A calculation error occurred. See console for details."
            self._send_status_update(error_message)
            import traceback
            print(f"[{self.name}] CRITICAL ERROR during plot: {e}")
            traceback.print_exc()

    def execute_task(self, args: list, stop_event: threading.Event):
        if not self.eph: return
        print(f"[{self.name}] Now listening for plot requests...")
        while not stop_event.is_set():
            try:
                msg = self.shared_queue.get(timeout=1.0)
                if msg.get("type") == "PLOT_REQUEST":
                    object_id = msg.get("payload", {}).get("object_id")
                    if object_id:
                        self._plot_neo_path(object_id)
            except Empty:
                continue
            except (KeyboardInterrupt, SystemExit):
                break
        print(f"[{self.name}] Shutting down.")

def create_worker(config: dict):
    return TrajectoryWorker(config)
