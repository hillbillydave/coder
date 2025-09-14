# workers/_fleetbridge_launcher.py
import threading, time, random, math, json, webview, requests, os, signal
from flask import Flask, request, jsonify, render_template
from pathlib import Path
from skyfield.api import load, EarthSatellite, Loader
from datetime import datetime, timedelta, timezone
from queue import Queue, Empty

class AIWorker:
    PLANET_DATA = [{"id":"mercury","size":2.0,"skyfield_name":"mercury"}, {"id":"venus","size":3.5,"skyfield_name":"venus"}, {"id":"earth","size":4.0,"skyfield_name":"earth"}, {"id":"mars","size":2.5,"skyfield_name":"mars"}, {"id":"jupiter","size":9.0,"skyfield_name":"jupiter barycenter"},{"id":"saturn","size":8.0,"skyfield_name":"saturn barycenter"},{"id":"uranus","size":6.0,"skyfield_name":"uranus barycenter"},{"id":"neptune","size":5.8,"skyfield_name":"neptune barycenter"}]
    SCENE_SCALE_AU = 150.0

    def __init__(self, config):
        self.config = config; self.lock = threading.Lock()
        
        self.active_satellites = [] 
        self.live_neo_data = []; self.asteroid_belt_data = []; self.plotted_path = {}
        
        self.shared_queue = self.config.get("shared_data_queue")
        self.api_keys = self.config.get("api_keys", {})
        self.studio_log_path = Path(__file__).parent / "_studio_log.jsonl"
        
        print("[AIWorker] Initializing astronomical data..."); 
        
        data_path = Path(__file__).parent.parent / "skyfield_cache"
        data_path.mkdir(exist_ok=True)
        self.loader = Loader(data_path)
        
        self.timescale = self.loader.timescale()
        self.eph = self.loader('de421.bsp')
        
        self.sun = self.eph['sun']; self.planets = {p['id']: self.eph[p['skyfield_name']] for p in self.PLANET_DATA}
        print("[AIWorker] Astronomical data loaded.")
        
        self._generate_asteroid_belt()
        # --- THIS IS THE FIX ---
        # We NO LONGER start the data fetch from here. This barista waits for instructions.
        # --- END OF FIX ---

    def initial_data_fetch(self):
        print("[AIWorker] Data fetch sequence initiated...")
        time.sleep(3)
        self._fetch_tle_data()
        print("[AIWorker] Pausing before next network request...")
        time.sleep(10)
        self._fetch_live_neos()

    def _fetch_tle_data(self):
        print("[AIWorker] Fetching real-time satellite catalog from CelesTrak...")
        try:
            url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"
            satellites_from_skyfield = self.loader.tle_file(url, reload=True)
            satellites = [{"name": sat.name, "obj": sat} for sat in satellites_from_skyfield]
            with self.lock: self.active_satellites = satellites[:200]
            print(f"[AIWorker] Successfully loaded {len(self.active_satellites)} active satellites.")
        except Exception as e:
            print(f"[AIWorker] WARNING: Could not fetch satellite data: {e}")

    def _generate_asteroid_belt(self):
        inner_au = 2.2; outer_au = 3.2
        for i in range(2000):
            oe={"semi_major_axis":random.uniform(inner_au,outer_au),"eccentricity":random.uniform(0,0.25),"inclination":math.radians(random.uniform(-5,5)),"mean_anomaly":random.uniform(0,2*math.pi)};oe["period"]=math.sqrt(oe["semi_major_axis"]**3)
            self.asteroid_belt_data.append({"id": f"asteroid_{i}", "type": "asteroid", "size": random.uniform(0.1, 0.4), "orbital_elements": oe})

    def _fetch_live_neos(self):
        print("[AIWorker] Fetching Near-Earth Object data from NASA...")
        
        api_keys_lower = {k.lower(): v for k, v in self.api_keys.items()}
        key_to_try_names = ["nasa_general_key", "nasa_neo_key"]
        
        for key_name in key_to_try_names:
            nasa_api_key = api_keys_lower.get(key_name)
            if not nasa_api_key: continue

            print(f"[AIWorker] Attempting to fetch NEOs with key '{key_name}'.")
            try:
                url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={datetime.now(timezone.utc).strftime('%Y-%m-%d')}&api_key={nasa_api_key}"
                r = requests.get(url, timeout=20); r.raise_for_status(); data = r.json()
                t = self.timescale.now(); earth_pos_au = self.eph['earth'].at(t).position.au
                new_neos=[]
                for date_obj in data.get('near_earth_objects',{}).values():
                    for neo in date_obj:
                        if not neo.get('close_approach_data'): continue
                        ca=neo['close_approach_data'][0]; dist_au=float(ca['miss_distance']['astronomical'])
                        vec=[random.uniform(-1,1) for _ in range(3)]; norm=math.sqrt(sum(v*v for v in vec)) if sum(v*v for v in vec) > 0 else 1; vec=[v/norm*dist_au for v in vec]
                        pos = {"x": (earth_pos_au[0] + vec[0]) * self.SCENE_SCALE_AU, "y": (earth_pos_au[2] + vec[1]) * self.SCENE_SCALE_AU, "z": -(earth_pos_au[1] + vec[2]) * self.SCENE_SCALE_AU}
                        new_neos.append({"id":f"NEO-{neo['id']}","name":neo['name'].replace('(','').replace(')',''),"type":"neo","size":max(0.5,min(3,neo['estimated_diameter']['meters']['estimated_diameter_max']/200)),"position":pos,"is_hazardous":neo['is_potentially_hazardous_asteroid'],"velocity_kps":float(ca['relative_velocity']['kilometers_per_second']),"miss_distance_km":f"{float(ca['miss_distance']['kilometers']):,.0f} km"})
                
                with self.lock: self.live_neo_data = new_neos
                print(f"[AIWorker] Successfully loaded {len(self.live_neo_data)} near-earth objects using key '{key_name}'.")
                return
            except Exception as e:
                print(f"[AIWorker] Key '{key_name}' failed. Reason: {e}")
        
        print(f"[AIWorker] All personal keys failed. Please check your network or API keys.")
    
    def _check_shared_queue(self):
        if not self.shared_queue: return
        try:
            msg = self.shared_queue.get_nowait()
            with self.lock:
                if msg.get("type") == "PATH_DATA_UPDATE":
                    self.plotted_path = msg.get("payload", {})
                elif msg.get("type") == "STATUS_UPDATE":
                    self.plotted_path = msg.get("payload", {})
        except Empty: pass

    def run_mission_loop(self):
        while True:
            self._check_shared_queue(); time.sleep(1) 
            
    def get_orbital_overlay(self, hours_in_future=0):
        with self.lock:
            future_offset=timedelta(hours=hours_in_future); t=self.timescale.now()+future_offset
            orbital_data=[{"id":"sun","type":"star","size":20,"position":{"x":0,"y":0,"z":0}}]
            earth_pos_au_tuple = (0,0,0)
            for p_info in self.PLANET_DATA:
                p_id=p_info['id'];p_obj=self.planets[p_id];astro=self.sun.at(t).observe(p_obj);x,y,z=astro.ecliptic_xyz().au
                pos={"x":x*self.SCENE_SCALE_AU,"y":z*self.SCENE_SCALE_AU,"z":-y*self.SCENE_SCALE_AU}
                orbital_data.append({"id":p_id,"type":"planet","size":p_info['size'],"position":pos})
                if p_id=='earth': earth_pos_au_tuple = (x, y, z)
            for sat in self.active_satellites:
                geocentric_pos = sat['obj'].at(t)
                x, y, z = geocentric_pos.position.au
                sat_pos = {"x": (earth_pos_au_tuple[0] + x) * self.SCENE_SCALE_AU,"y": (earth_pos_au_tuple[2] + z) * self.SCENE_SCALE_AU,"z": -(earth_pos_au_tuple[1] + y) * self.SCENE_SCALE_AU}
                orbital_data.append({"id":sat['name'],"type":"satellite","size":0.5,"position":sat_pos,"status":"Nominal"})
            for asteroid in self.asteroid_belt_data:
                orbital_data.append({"id": asteroid['id'], "type": "asteroid", "size": asteroid['size'], "orbital_elements": asteroid["orbital_elements"]})
            if hours_in_future == 0: orbital_data.extend(self.live_neo_data)
            return orbital_data

    def get_telemetry(self):
        with self.lock:
            return {"fleet_status": {"ai_status": "Online","active_satellites": len(self.active_satellites),"tracking_neos": len(self.live_neo_data)}, "satellites": [{"id": sat['name'], "status": "Nominal"} for sat in self.active_satellites]}

    def get_plotted_path(self):
        with self.lock: return self.plotted_path
        
    def get_studio_log(self):
        if not self.studio_log_path.exists(): return []
        try:
            with open(self.studio_log_path, 'r', encoding='utf-8') as f: lines = f.readlines()
            return [json.loads(line) for line in lines[-10:]]
        except Exception: return []

script_dir=Path(__file__).parent;root_dir=script_dir.parent
server=Flask("FleetBridgeGUI",template_folder=root_dir/'templates',static_folder=root_dir/'static')
worker_instance=AIWorker(config={})
@server.route('/')
def main_page():return render_template('dashboard.html')
@server.route('/orbitaldata')
def orbital_data():return jsonify(worker_instance.get_orbital_overlay())
@server.route('/telemetry')
def telemetry():return jsonify(worker_instance.get_telemetry())
@server.route('/get_plotted_path')
def get_plotted_path_route(): return jsonify(worker_instance.get_plotted_path())
@server.route('/plot_object', methods=['POST'])
def plot_object_route():
    data = request.get_json()
    object_id = data.get('id')
    if object_id and worker_instance.shared_queue:
        worker_instance.shared_queue.put({"type": "PLOT_REQUEST","payload": {"object_id": object_id}})
        return jsonify({"status": "ok", "message": f"Plot request for '{object_id}' sent."})
    return jsonify({"status": "error", "message": "Invalid ID."}), 400
@server.route('/get_studio_log')
def get_studio_log_route(): return jsonify(worker_instance.get_studio_log())
@server.route('/get_texture_info')
def get_texture_info():
    textures_dir = root_dir/'static'/'textures';files={}
    if (textures_dir/"starfield.jpg").exists():files['starfield']="/static/textures/starfield.jpg"
    if (textures_dir/"earth.jpg").exists():files['earth']="/static/textures/earth.jpg"
    return jsonify(files)

def run_server():
    import logging
    log=logging.getLogger('werkzeug');log.setLevel(logging.ERROR)
    server.run(host='127.0.0.1',port=5001)

class Api:
    def __init__(self): self._window=None
    def shutdown(self):
        if self._window: self._window.destroy()

# --- THIS IS THE NEW, CORRECT STARTUP SEQUENCE ---
if __name__ == '__main__':
    # 1. Load the configuration from the temporary file.
    config={};config_path=root_dir/'workers'/'_temp_gui_config.json'
    if config_path.exists():
        with open(config_path,'r') as f:config=json.load(f)
    
    # 2. Create the shared queue and add it to the config.
    shared_queue_main = Queue()
    config['shared_data_queue'] = shared_queue_main
    
    # 3. Create the AIWorker instance, passing the full, correct config.
    # This barista now has the keys to the register.
    worker_instance = AIWorker(config)
    
    # 4. NOW, after the worker is fully initialized, we ask it to start fetching data.
    threading.Thread(target=worker_instance.initial_data_fetch, daemon=True).start()
    
    # Start the other necessary background tasks
    try: from trajectory_worker import TrajectoryWorker
    except ImportError: TrajectoryWorker = None
    if TrajectoryWorker:
        trajectory_worker = TrajectoryWorker(config)
        traj_thread = threading.Thread(target=trajectory_worker.execute_task, args=([], threading.Event()), daemon=True)
        traj_thread.start()
    threading.Thread(target=worker_instance.run_mission_loop,daemon=True).start()
    server_thread=threading.Thread(target=run_server,daemon=True);server_thread.start()
    
    api=Api()
    
    def on_closing():
        print("[FleetBridge GUI] Window close requested. Shutting down.")
        api.shutdown()

    window=webview.create_window('🛰️ FleetBridge', 'http://127.0.0.1:5001/',js_api=api,width=1600,height=900)
    window.events.closing += on_closing
    
    signal.signal(signal.SIGINT, signal.default_int_handler)
    try:
        webview.start(debug=False)
    except KeyboardInterrupt:
        print("[FleetBridge GUI] Keyboard interrupt received. Closing.")
        api.shutdown()
