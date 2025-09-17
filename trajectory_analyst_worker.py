# workers/trajectory_analyst_worker.py
import threading
import time
import requests
from queue import Empty
from pathlib import Path

# Use an absolute import for robustness
from workers.worker_base import WorkerBase

try:
    from skyfield.api import load, Loader, ecliptic_frame
    SKYFIELD_AVAILABLE = True
except ImportError:
    SKYFIELD_AVAILABLE = False

class TrajectoryAnalystWorker(WorkerBase):
    """
    A headless analytics worker. It listens for PLOT_REQUEST messages on the
    shared queue, fetches real orbital data from JPL, calculates a 365-day
    trajectory, and sends the results back to the queue for visualization.
    """
    def __init__(self, config: dict):
        super().__init__(config)
        self.shared_queue = config.get("shared_queue")
        
        if not SKYFIELD_AVAILABLE:
            self.eph = None
            self.speak("CRITICAL ERROR: skyfield library not found. I am offline.")
            return
            
        try:
            # Use a dedicated cache for skyfield data
            data_path = Path(__file__).parent.parent / "skyfield_cache"
            data_path.mkdir(exist_ok=True)
            self.loader = Loader(data_path)
            self.ts = self.loader.timescale()
            self.eph = self.loader('de421.bsp') # Ephemeris for planets
            self.sun = self.eph['sun']
            self.speak("Calculator engine initialized. Standing by for trajectory analysis requests.")
        except Exception as e:
            self.speak(f"CRITICAL ERROR: Could not initialize calculator engine. {e}")
            self.eph = None

    def _send_update(self, msg_type: str, payload: dict):
        """Sends a structured message back to the shared queue for the GUI."""
        if self.shared_queue:
            self.shared_queue.put({"type": msg_type, "payload": payload})
            time.sleep(0.1) # Small delay to ensure message order

def _plot_neo_path(self, object_id: str):
    """The core logic for fetching and calculating a NEO's path."""
    try:
        self._send_update("STATUS_UPDATE", {"message": f"Request received. Contacting JPL for '{object_id}'..."})
        
        # First, get the full orbital elements from the Small-Body Database (SBDB)
        sbdb_url = f"https://ssd-api.jpl.nasa.gov/sbdb.api?sstr={object_id.replace(' ', '%20')}&orb=1"
        sbdb_response = requests.get(sbdb_url, timeout=15)
        sbdb_response.raise_for_status()
        sbdb_data = sbdb_response.json()
        
        if "orb" not in sbdb_data or "elements" not in sbdb_data['orb']:
            self._send_update("STATUS_UPDATE", {"message": f"Error: Could not retrieve orbital elements for '{object_id}'."})
            return
        
        fullname = sbdb_data['object']['fullname'].strip()
        self._send_update("STATUS_UPDATE", {"message": f"Data received for {fullname}. Calculating trajectory..."})
        
        # Extract orbital elements from SBDB data
        elements = {el['name']: float(el['value']) for el in sbdb_data['orb']['elements']}
        epoch_jd = elements.get('epoch', self.ts.J(2451545.0))  # Default to J2000 if missing
        
        # Create a Skyfield orbit using from_elements
        from skyfield import framelib
        frame = framelib.ecliptic_frame
        t0 = self.ts.J(epoch_jd)
        orbit = self.sun.at(t0).observe_solar_system(self.eph).from_elements(
            e=elements.get('e', 0.0),
            a_au=elements.get('a', 1.0),
            inc_degrees=elements.get('i', 0.0),
            node_degrees=elements.get('om', 0.0),
            argp_degrees=elements.get('w', 0.0),
            M_degrees=elements.get('ma', 0.0),
            epoch=t0
        )

        # Generate future positions
        path_points = []
        SCENE_SCALE_FACTOR = 150.0  # Scales AU to a nice size for the 3D scene
        today = self.ts.now()
        for day_offset in range(0, 366, 1):  # 1-day steps for smoothness
            future_time = self.ts.utc(today.utc_datetime().year, today.utc_datetime().month, today.utc_datetime().day + day_offset)
            pos = orbit.at(future_time).position.au
            x, y, z = pos
            path_points.append({"x": x * SCENE_SCALE_FACTOR, "y": z * SCENE_SCALE_FACTOR, "z": -y * SCENE_SCALE_FACTOR})
        
        self._send_update("STATUS_UPDATE", {"message": f"Calculation complete. Rendering path for {fullname}..."})
        path_data = {"id": fullname, "path": path_points}
        self._send_update("PATH_DATA_UPDATE", path_data)

    except requests.exceptions.HTTPError as http_err:
        self._send_update("STATUS_UPDATE", {"message": f"JPL API returned an error: {http_err}"})
    except Exception as e:
        import traceback
        print(f"[{self.name}] CRITICAL ERROR during plot: {e}")
        traceback.print_exc()
        self._send_update("STATUS_UPDATE", {"message": f"A critical calculation error occurred."})

    def execute_task(self, args: list, stop_event: threading.Event):
        """Main loop. Listens for PLOT_REQUEST messages on the queue."""
        if not self.eph:
            self.speak("Analytics engine is offline. Cannot process requests.")
            return

        while not stop_event.is_set():
            try:
                # Wait for a message. The timeout allows this loop to check the stop_event.
                msg = self.shared_queue.get(timeout=1.0)
                if msg.get("type") == "PLOT_REQUEST":
                    object_id = msg.get("payload", {}).get("object_id")
                    if object_id:
                        # Run the heavy calculation in a new thread to keep the listener responsive
                        threading.Thread(target=self._plot_neo_path, args=(object_id,), daemon=True).start()
            except Empty:
                continue # This is normal, just means no messages
            except (KeyboardInterrupt, SystemExit):
                break
        self.speak("Shutting down.")

def create_worker(config: dict) -> TrajectoryAnalystWorker:
    return TrajectoryAnalystWorker(config)
