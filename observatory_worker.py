# workers/observatory_worker.py
import threading
from pathlib import Path
from datetime import datetime, timedelta
import requests
from workers.worker_base import WorkerBase

try:
    from skyfield.api import load, EarthSatellite
    SKYFIELD_AVAILABLE = True
except ImportError:
    SKYFIELD_AVAILABLE = False

DATA_DIR = Path("vespera_memory") / "astronomical_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

class ObservatoryWorker(WorkerBase):
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "Vespera Observatory"
        self.command = "observe"
        self.is_ready = False
        self._initialization_lock = threading.Lock()
        
        if SKYFIELD_AVAILABLE:
            self.ts = load.timescale()
            self.planets = None
            self.satellites = {}
        else:
            self._log("Skyfield library not found. Worker is offline.")

    def _log(self, message: str): print(f"[{self.name}] {message}")

    def _download_file(self, url: str, dest: Path) -> bool:
        self._log(f"Downloading a new star chart to {dest.name}...")
        try:
            with requests.get(url, stream=True, timeout=30) as r: # shorter timeout
                r.raise_for_status()
                with open(dest, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            self._log("Download complete, sweety.")
            return True
        except requests.exceptions.RequestException as e:
            self._log(f"Oh, drat. Couldn't download the celestial map: {e}")
            return False

    def _lazy_initialize_data(self):
        with self._initialization_lock:
            if self.is_ready: return
            if not SKYFIELD_AVAILABLE: return

            self._log("Performing first-time setup. Fetching celestial data...")
            de440_path = DATA_DIR / "de440s.bsp"
            if not de440_path.exists():
                if not self._download_file("https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp", de440_path):
                    return # Stop if planet data fails to download

            self.planets = load(str(de440_path))

            iss_tle_path = DATA_DIR / "stations.tle"
            if not iss_tle_path.exists() or (datetime.now() - datetime.fromtimestamp(iss_tle_path.stat().st_mtime)) > timedelta(days=1):
                 # --- THE FIX IS HERE ---
                 if not self._download_file("https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle", iss_tle_path):
                     return # Stop initialization if TLE data fails to download
            
            try:
                # This line will now only run if the file exists.
                sats = load.tle_file(str(iss_tle_path))
                self.satellites = {sat.name.strip().upper(): sat for sat in sats}
                self._log(f"Now tracking {len(self.satellites)} satellites.")
                self.is_ready = True
            except Exception as e:
                self._log(f"Couldn't read satellite data. Error: {e}")
                # If reading fails, we are not ready.
                self.is_ready = False

    def execute_task(self, args: list, main_stop_event: threading.Event):
        if not SKYFIELD_AVAILABLE:
            self._log("I'm sorry, my star-gazing tools aren't installed. Please run 'pip install skyfield'.")
            return

        if not self.is_ready: self._lazy_initialize_data()
        
        if not self.is_ready:
            self._log("My star charts are out of date. I can't give a report.")
            return
        
        target_name = ' '.join(args).upper()
        if not target_name:
            self._log("Please tell me what to observe, sweety. Example: 'observe ISS (ZARYA)'")
            return

        now = self.ts.now()
        earth = self.planets['earth']
        target = self.satellites.get(target_name) or self.planets.get(target_name.lower())

        if target:
            self._send_report_to_fleetbridge(target, earth, now)
        else:
            self._log(f"I couldn't find '{target_name}' in my star charts, my dear.")

    def _send_report_to_fleetbridge(self, target, earth, time_of_observation):
        # ... (This method is the same) ...
        try:
            geocentric = (target - earth).at(time_of_observation)
            subpoint = geocentric.subpoint()
            payload = {
                "Target": str(getattr(target, 'name', 'N/A')),
                "Latitude": f"{subpoint.latitude.degrees:.4f}°",
                "Longitude": f"{subpoint.longitude.degrees:.4f}°",
                "Elevation (km)": f"{subpoint.elevation.km:,.2f}"
            }
            gui_payload = { "source": self.name, "payload": payload, "is_alert": False }
            requests.post("http://127.0.0.1:5555/update", json=gui_payload, timeout=2)
            self._log(f"Report for {target.name} sent to FleetBridge.")
        except requests.exceptions.RequestException:
            self._log("Could not send report to FleetBridge. Is the GUI running?")
        except Exception as e:
            self._log(f"Error calculating position: {e}")

def create_worker(config: dict) -> ObservatoryWorker:
    return ObservatoryWorker(config)
