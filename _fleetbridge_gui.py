import threading, time, random, math, json, webview, requests, os, signal
from flask import Flask, request, jsonify, render_template
from pathlib import Path
from skyfield.api import load, EarthSatellite, Loader, Topos
from datetime import datetime, timedelta, timezone
from queue import Queue, Empty
from waitress import serve
import numpy as np
import socket

class TrajectoryAnalyst:
    def __init__(self, config, result_queue):
        self.name = "Internal Trajectory Analyst"
        self.result_queue = result_queue
        self.request_queue = Queue()
        self.config = config
        try:
            data_path = Path(__file__).parent.parent / "skyfield_cache"
            self.loader = Loader(data_path)
            self.ts = self.loader.timescale()
            self.eph = self.loader('de421.bsp')
            self.sun = self.eph['sun']
            import skyfield
            print(f"[{self.name}] Initialized with Skyfield version {skyfield.__version__}.")
        except Exception as e:
            print(f"[{self.name}] ERROR: Could not initialize. {e}")
            self.eph = None
    
    def _send_update(self, update_type, payload):
        if self.result_queue:
            print(f"[{self.name}] Sending update: type={update_type}, payload={payload}")
            self.result_queue.put({"type": update_type, "payload": payload})

    def _kepler_propagate(self, elements, time_offset_days, total_days):
        """Propagate orbit using Keplerian elements for a given number of days."""
        mu = 1.32712440018e11  # Solar gravitational parameter (km^3/s^2)
        mu_au = mu / (149597870.7**3) * (86400**2)  # Convert to AU^3/day^2

        a = elements['a']  # Semi-major axis in AU
        e = elements['e']  # Eccentricity
        i = math.radians(elements['i'])  # Inclination in radians
        omega = math.radians(elements['om'])  # Longitude of ascending node
        w = math.radians(elements['w'])  # Argument of perihelion
        M0 = math.radians(elements['ma'])  # Mean anomaly at epoch
        n = math.sqrt(mu_au / a**3)  # Mean motion (radians/day)

        path_points = []
        for day in range(total_days):
            t = time_offset_days + day  # Total days since epoch
            M = M0 + n * t  # Mean anomaly at time t
            E = M  # Initial guess for eccentric anomaly
            for _ in range(10):  # Increased iterations for accuracy
                dE = (M - E + e * math.sin(E)) / (1 - e * math.cos(E))  # Newton-Raphson
                E += dE
                if abs(dE) < 1e-8:
                    break
            cos_nu = (math.cos(E) - e) / (1 - e * math.cos(E))
            sin_nu = math.sqrt(1 - e**2) * math.sin(E) / (1 - e * math.cos(E))
            nu = math.atan2(sin_nu, cos_nu)  # True anomaly

            # Position in orbital plane (AU)
            r = a * (1 - e * math.cos(E))
            x_orb = r * math.cos(nu)
            y_orb = r * math.sin(nu)

            # Rotate to ecliptic coordinates
            cos_i = math.cos(i)
            sin_i = math.sin(i)
            cos_omega = math.cos(omega)
            sin_omega = math.sin(omega)
            cos_w = math.cos(w)
            sin_w = math.sin(w)

            x = (cos_omega * cos_w - sin_omega * sin_w * cos_i) * x_orb - (cos_omega * sin_w + sin_omega * cos_w * cos_i) * y_orb
            y = (sin_omega * cos_w + cos_omega * sin_w * cos_i) * x_orb + (cos_omega * cos_w - sin_omega * sin_w * cos_i) * y_orb
            z = sin_w * sin_i * x_orb + cos_w * sin_i * y_orb

            path_points.append({"x": x * 150.0, "y": z * 150.0, "z": -y * 150.0})

        return path_points

    def plot_path(self, object_id: str):
        try:
            # Clean input by stripping quotes, whitespace, and splitting
            object_id = object_id.strip().strip('"').strip("'").replace(" ", "")
            print(f"[{self.name}] Processing plot request for '{object_id}'")
            self._send_update("STATUS_UPDATE", {"message": f"Request received for '{object_id}'..."})
            # Validate and extract SPK-ID (handle names like "2005 EJ225" or "385605")
            spk_id = object_id if object_id.isdigit() and len(object_id) == 6 else self._lookup_neo_spk_id(object_id)
            if not spk_id:
                # Try splitting and checking again (e.g., "385605 2005 EJ225")
                parts = object_id.split()
                if len(parts) > 1 and parts[0].isdigit() and len(parts[0]) == 6:
                    spk_id = parts[0]
                elif len(parts) > 1:
                    spk_id = self._lookup_neo_spk_id(" ".join(parts[1:]))
                if not spk_id:
                    self._send_update("STATUS_UPDATE", {"message": f"Error: '{object_id}' is not a valid 6/7-digit SPK-ID or recognized NEO name."})
                    return
            # Try NASA NeoWs API first
            api_key = self.config.get("api_keys", {}).get("nasa_neo_key", "DEMO_KEY")
            url = f"https://api.nasa.gov/neo/rest/v1/neo/{spk_id}?api_key={api_key}"
            print(f"[{self.name}] Fetching data from NeoWs API: {url}")
            try:
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                data = response.json()
                print(f"[{self.name}] NeoWs API response: {json.dumps(data, indent=2)}")
            except requests.exceptions.HTTPError as e:
                print(f"[{self.name}] NeoWs API failed: {e}. Trying JPL SBDB API...")
                # Fallback to JPL SBDB API
                url = f"https://ssd-api.jpl.nasa.gov/sbdb.api?sstr={spk_id}"
                print(f"[{self.name}] Fetching data from JPL SBDB API: {url}")
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                data = response.json()
                print(f"[{self.name}] JPL SBDB API response: {json.dumps(data, indent=2)}")
                if "orbit" not in data or "elements" not in data["orbit"]:
                    self._send_update("STATUS_UPDATE", {"message": f"Error: No orbital data for '{spk_id}' in JPL SBDB API."})
                    return
                fullname = data.get('object', {}).get('fullname', spk_id)
                self._send_update("STATUS_UPDATE", {"message": f"Data for {fullname} received from JPL SBDB. Calculating..."})
                elements_list = data['orbit']['elements']
                elements = {elem['name']: float(elem['value']) for elem in elements_list}
                epoch_jd = elements.get('epoch', 2451545.0)  # Default to J2000 if missing
            else:
                # NeoWs API succeeded
                if "orbital_data" not in data or not data["orbital_data"]:
                    self._send_update("STATUS_UPDATE", {"message": f"Error: No orbital data for '{spk_id}' in NeoWs API."})
                    return
                fullname = data.get('name', spk_id)
                self._send_update("STATUS_UPDATE", {"message": f"Data for {fullname} received from NeoWs. Calculating..."})
                orbit_data = data['orbital_data']
                elements = {
                    'e': float(orbit_data.get('eccentricity', 0.0)),
                    'a': float(orbit_data.get('semi_major_axis', 0.0)),
                    'i': float(orbit_data.get('inclination', 0.0)),
                    'om': float(orbit_data.get('ascending_node_longitude', 0.0)),
                    'w': float(orbit_data.get('perihelion_argument', 0.0)),
                    'ma': float(orbit_data.get('mean_anomaly', 0.0)),
                    'epoch': float(orbit_data.get('epoch_osculation', 2460800.5))  # JD
                }

            # Convert epoch to MJD and get start time in MJD
            epoch_mjd = elements['epoch'] - 2400000.5  # Convert JD to MJD
            today = time.gmtime()
            start_time = self.ts.utc(today.tm_year, today.tm_mon, today.tm_mday)
            print(f"Debug: start_time type = {type(start_time)}, TT = {start_time.tt}, MJD = {start_time.tt + 2400000.5 - 2451545.0}")
            start_mjd = start_time.tt + 2400000.5 - 2451545.0  # Convert TT to MJD (J2000 epoch adjustment)
            days_ahead = 400 * 365.25  # Approximately 400 years in days

            # Use Kepler propagation for 400 years
            path_points = self._kepler_propagate(elements, start_mjd - epoch_mjd, int(days_ahead))

            self._send_update("STATUS_UPDATE", {"message": f"Calculation complete for {fullname}."})
            path_data = {"id": fullname, "path": path_points}
            self._send_update("PATH_DATA_UPDATE", path_data)
            print(f"[{self.name}] Sent PATH_DATA_UPDATE for {fullname}")
        except Exception as e:
            print(f"[{self.name}] ERROR in plot_path: {e}")
            self._send_update("STATUS_UPDATE", {"message": f"Calculation error: {e}"})

    def track_starship(self, object_id: str):
        try:
            self._send_update("STATUS_UPDATE", {"message": f"Tracking {object_id} to Mars..."})
            # Fetch latest TLE for Starship from Celestrak (using ISS as placeholder)
            headers = {'User-Agent': 'Mozilla/5.0'}
            url = "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE"  # ISS; replace with Starship CATNR when available
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            tle_lines = response.text.strip().split('\n')
            if len(tle_lines) < 2:
                self._send_update("STATUS_UPDATE", {"message": "Error: Could not fetch TLE data."})
                return

            # Load TLE into Skyfield
            tle_path = Path(__file__).parent.parent / "skyfield_cache" / "starship.tle"
            with open(tle_path, "w") as f:
                f.write(tle_lines[1] + '\n' + tle_lines[2])
            sat = self.loader.tle_file(str(tle_path))[0]

            # Generate future positions to Mars (e.g., 6 months)
            path_points = []
            today = self.ts.now()
            for day_offset in range(0, 180, 1):  # 180 days
                future_time = today + day_offset / 365.25  # Convert to years
                pos = sat.at(future_time).position.au
                x, y, z = pos
                path_points.append({"x": x * 150.0, "y": z * 150.0, "z": -y * 150.0})

            self._send_update("STATUS_UPDATE", {"message": f"Starship trajectory to Mars calculated."})
            path_data = {"id": "Starship to Mars", "path": path_points}
            self._send_update("PATH_DATA_UPDATE", path_data)
            print(f"[{self.name}] Sent PATH_DATA_UPDATE for {object_id}")  # Fixed typo here
        except Exception as e:
            print(f"[{self.name}] ERROR in track_starship: {e}")
            self._send_update("STATUS_UPDATE", {"message": f"Tracking error: {e}"})

    def listen_for_requests(self, stop_event):
        if not self.eph:
            print(f"[{self.name}] Cannot listen: ephemeris not loaded.")
            return
        print(f"[{self.name}] Starting to listen for requests...")
        while not stop_event.is_set():
            try:
                msg = self.request_queue.get(timeout=1.0)
                print(f"[{self.name}] Received message: {msg}")
                if msg.get("type") == "PLOT_REQUEST":
                    self.plot_path(msg.get("payload", {}).get("object_id", ""))
                elif msg.get("type") == "TRACK_STARSHIP":
                    self.track_starship(msg.get("payload", {}).get("object_id", "STARSHIP"))
            except Empty:
                pass
            except Exception as e:
                print(f"[{self.name}] ERROR in listen_for_requests: {e}")
                break

    def _lookup_neo_spk_id(self, neo_name: str) -> str:
        """Lookup SPK-ID from NEO name using JPL API."""
        try:
            url = f"https://ssd-api.jpl.nasa.gov/sbdb.api?sstr={neo_name.replace(' ', '%20')}"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            if "object" in data and "id" in data["object"]:
                return data["object"]["id"]
        except Exception as e:
            print(f"[{self.name}] NEO lookup failed: {e}")
        return None

class FleetBridgeApp:
    PLANET_DATA = [
        {"id": "mercury", "size": 2.0, "skyfield_name": "mercury"},
        {"id": "venus", "size": 3.5, "skyfield_name": "venus"},
        {"id": "earth", "size": 4.0, "skyfield_name": "earth"},
        {"id": "mars", "size": 2.5, "skyfield_name": "mars"},
        {"id": "jupiter", "size": 9.0, "skyfield_name": "jupiter barycenter"},
        {"id": "saturn", "size": 8.0, "skyfield_name": "saturn barycenter"},
        {"id": "uranus", "size": 6.0, "skyfield_name": "uranus barycenter"},
        {"id": "neptune", "size": 5.8, "skyfield_name": "neptune barycenter"}
    ]
    SCENE_SCALE_AU = 150.0

    def __init__(self, config):
        self.config = config
        self.lock = threading.Lock()
        self.active_satellites = []
        self.live_neo_data = []
        self.asteroid_belt_data = []
        self.plotted_path = {}
        self.result_queue = Queue()
        self.api_keys = self.config.get("api_keys", {})
        self.studio_log_path = Path(__file__).parent.parent / "workers" / "_studio_log.jsonl"
        data_path = Path(__file__).parent.parent / "skyfield_cache"
        self.loader = Loader(data_path)
        self.timescale = self.loader.timescale()
        self.eph = self.loader('de421.bsp')
        self.sun = self.eph['sun']
        self.planets = {p['id']: self.eph[p['skyfield_name']] for p in self.PLANET_DATA}
        self._generate_asteroid_belt()
        self.trajectory_analyst = TrajectoryAnalyst(self.config, self.result_queue)
        self.stop_event = threading.Event()
        threading.Thread(target=self.trajectory_analyst.listen_for_requests, args=(self.stop_event,), daemon=True).start()
        threading.Thread(target=self.initial_data_fetch, daemon=True).start()
        # Initialize Flask server with explicit paths
        self.server = Flask("FleetBridgeGUI", 
                           template_folder=Path('/home/ashley/Desktop/coder/templates'), 
                           static_folder=Path('/home/ashley/Desktop/coder/static'))

    def initial_data_fetch(self):
        time.sleep(1)
        self._fetch_tle_data()
        time.sleep(1)
        self._fetch_live_neos()

    def _fetch_tle_data(self):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            tle_path = Path(__file__).parent.parent / "skyfield_cache" / "active.tle"
            with open(tle_path, "w") as f:
                f.write(response.text)
            sats = self.loader.tle_file(str(tle_path))
            with self.lock:
                self.active_satellites = [{"name": sat.name, "obj": sat} for sat in sats]
        except Exception as e:
            print(f"[FleetBridge] WARNING: Satellite data fetch failed: {e}")

    def _generate_asteroid_belt(self):
        inner_au = 2.2
        outer_au = 3.2
        for i in range(500):  # Reduced from 2000 for performance
            oe = {
                "semi_major_axis": random.uniform(inner_au, outer_au),
                "eccentricity": random.uniform(0, 0.25),
                "inclination": math.radians(random.uniform(-5, 5)),
                "mean_anomaly": random.uniform(0, 2 * math.pi)
            }
            oe["period"] = math.sqrt(oe["semi_major_axis"] ** 3)
            self.asteroid_belt_data.append({
                "id": f"asteroid_{i}",
                "type": "asteroid",
                "size": random.uniform(0.1, 0.4),
                "orbital_elements": oe
            })

    def _fetch_live_neos(self):
        api_keys_lower = {k.lower(): v for k, v in self.api_keys.items()}
        key_names = ["nasa_general_key", "nasa_neo_key"]
        for key_name in key_names:
            api_key = api_keys_lower.get(key_name)
            if not api_key:
                continue
            try:
                url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={datetime.now(timezone.utc).strftime('%Y-%m-%d')}&api_key={api_key}"
                r = requests.get(url, timeout=20)
                r.raise_for_status()
                data = r.json()
                t = self.timescale.now()
                earth_pos_au = self.eph['earth'].at(t).position.au
                new_neos = []
                for date_obj in data.get('near_earth_objects', {}).values():
                    for neo in date_obj:
                        if not neo.get('close_approach_data'):
                            continue
                        ca = neo['close_approach_data'][0]
                        dist_au = float(ca['miss_distance']['astronomical'])
                        vec = [random.uniform(-1, 1) for _ in range(3)]
                        norm = math.sqrt(sum(v * v for v in vec)) if sum(v * v for v in vec) > 0 else 1
                        vec = [v / norm * dist_au for v in vec]
                        pos = {
                            "x": (earth_pos_au[0] + vec[0]) * 150.0,
                            "y": (earth_pos_au[2] + vec[1]) * 150.0,
                            "z": -(earth_pos_au[1] + vec[2]) * 150.0
                        }
                        new_neos.append({
                            "id": f"NEO-{neo['id']}",
                            "name": neo['name'].replace('(', '').replace(')', ''),
                            "type": "neo",
                            "size": max(0.5, min(3, neo['estimated_diameter']['meters']['estimated_diameter_max'] / 200)),
                            "position": pos,
                            "is_hazardous": neo['is_potentially_hazardous_asteroid'],
                            "velocity_kps": float(ca['relative_velocity']['kilometers_per_second']),
                            "miss_distance_km": f"{float(ca['miss_distance']['kilometers']):,.0f} km"
                        })
                with self.lock:
                    self.live_neo_data = new_neos
                return
            except Exception as e:
                print(f"[FleetBridge] Key '{key_name}' failed: {e}")

    def get_orbital_overlay(self, hours_in_future=0):
        with self.lock:
            future_offset = timedelta(hours=hours_in_future)
            t = self.timescale.now() + future_offset
            orbital_data = [{"id": "sun", "type": "star", "size": 20, "position": {"x": 0, "y": 0, "z": 0}}]
            earth_pos_au_tuple = (0, 0, 0)
            for p_info in self.PLANET_DATA:
                p_id = p_info['id']
                p_obj = self.planets[p_id]
                astro = self.sun.at(t).observe(p_obj)
                x, y, z = astro.ecliptic_xyz().au
                pos = {"x": x * 150.0, "y": z * 150.0, "z": -y * 150.0}
                orbital_data.append({"id": p_id, "type": "planet", "size": p_info['size'], "position": pos})
                if p_id == 'earth':
                    earth_pos_au_tuple = (x, y, z)
            for sat in self.active_satellites:
                geocentric_pos = sat['obj'].at(t)
                x, y, z = geocentric_pos.position.au
                sat_pos = {
                    "x": (earth_pos_au_tuple[0] + x) * 150.0,
                    "y": (earth_pos_au_tuple[2] + z) * 150.0,
                    "z": -(earth_pos_au_tuple[1] + y) * 150.0
                }
                orbital_data.append({"id": sat['name'], "type": "satellite", "size": 0.5, "position": sat_pos, "status": "Nominal"})
            for asteroid in self.asteroid_belt_data:
                orbital_data.append(asteroid)
            if hours_in_future == 0:
                orbital_data.extend(self.live_neo_data)
            return orbital_data

    def get_telemetry(self):
        with self.lock:
            return {
                "fleet_status": {
                    "ai_status": "Online",
                    "active_satellites": len(self.active_satellites),
                    "tracking_neos": len(self.live_neo_data)
                }
            }

    def get_object_list(self):
        with self.lock:
            objects = {
                "planets": [{"id": p["id"], "type": "planet"} for p in self.PLANET_DATA],
                "satellites": [{"id": sat["name"], "type": "satellite"} for sat in self.active_satellites[:50]],  # Top 50
                "neos": [{"id": neo["name"], "type": "neo"} for neo in self.live_neo_data[:50]],  # Top 50
                "starship": [{"id": "Starship to Mars", "type": "starship"}]
            }
            return objects

    def get_results(self):
        results = []
        try:
            while True:
                msg = self.result_queue.get_nowait()
                results.append(msg)
        except Empty:
            pass
        return jsonify(results if results else {})

    def setup_routes(self):
        @self.server.route('/')
        def main_page():
            return render_template('dashboard.html')
        @self.server.route('/orbitaldata')
        def orbital_data():
            return jsonify(self.get_orbital_overlay())
        @self.server.route('/telemetry')
        def telemetry():
            return jsonify(self.get_telemetry())
        @self.server.route('/get_results')
        def get_results_route():
            return self.get_results()
        @self.server.route('/plot_object', methods=['POST'])
        def plot_object_route():
            object_id = request.json.get('id')
            if object_id:
                self.trajectory_analyst.request_queue.put({"type": "PLOT_REQUEST", "payload": {"object_id": object_id}})
                return jsonify({"status": "ok"})
            return jsonify({"status": "error"}), 400
        @self.server.route('/track_starship', methods=['POST'])
        def track_starship_route():
            self.trajectory_analyst.request_queue.put({"type": "TRACK_STARSHIP", "payload": {"object_id": "STARSHIP"}})
            return jsonify({"status": "ok"})
        @self.server.route('/get_object_list')
        def get_object_list_route():
            return jsonify(self.get_object_list())
        @self.server.route('/get_studio_log')
        def get_studio_log_route():
            studio_log_path = Path(__file__).parent.parent / "workers" / "_studio_log.jsonl"
            if not studio_log_path.exists():
                return jsonify([])
            try:
                with open(studio_log_path, 'r') as f:
                    lines = f.readlines()
                return jsonify([json.loads(line) for line in lines[-10:]])
            except:
                return jsonify([])

class FleetbridgeWorker:
    def __init__(self, config):
        self.config = config
        self.stop_event = threading.Event()
        self._server_running = False
        self.app = FleetBridgeApp(config)
        self.app.setup_routes()  # Call to set up Flask routes

    def run(self):
        print("[Worker] FleetbridgeWorker initialized.")
        print("[DIAG] Worker created: Fleetbridge Worker")
        print("[DIAG] FleetbridgeWorker.execute_task STARTED with args: []")
        print("[Fleetbridge Worker] Launching the Solar Command Interface (non-blocking)...")
        print(f"[DIAG] FleetbridgeWorker.launch_gui thread STARTED.")

        def run_server():
            print("[FleetBridge] Starting web server...")
            if not hasattr(self, '_server_running') or not self._server_running:
                self._server_running = True
                serve(self.app.server, host='127.0.0.1', port=5001, _quiet=True)

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        # Wait for server to be ready
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('127.0.0.1', 5001))
                    if result == 0:
                        print("[FleetBridge] Server is ready on port 5001.")
                        break
                time.sleep(1)
            except Exception as e:
                print(f"[FleetBridge] Waiting for server... Attempt {attempt + 1}/{max_attempts}, Error: {e}")
                if attempt == max_attempts - 1:
                    print("[FleetBridge] Server failed to start. Aborting.")
                    return
        try:
            window = webview.create_window('🛰️ FleetBridge', 'http://127.0.0.1:5001/', width=1600, height=900)
            def on_closing():
                self.stop_event.set()
            window.events.closing += on_closing
            signal.signal(signal.SIGINT, signal.default_int_handler)
            webview.start(debug=True)  # Enable debug mode to catch errors
        except Exception as e:
            print(f"[FleetBridge] GUI Error: {e}")
        print("[FleetBridge] Window closed. Signalling shutdown.")
        self.stop_event.set()
        print("[DIAG] FleetbridgeWorker.execute_task FINISHED (thread launched, returning control).")

if __name__ == '__main__':
    root_dir = Path(__file__).parent.parent
    config = {}
    config_path = root_dir / 'workers' / '_temp_gui_config.json'
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    worker = FleetbridgeWorker(config)
    worker.run()
