# workers/mission_control_worker.py

import threading
import time
import random
import math
import webbrowser
from flask import Flask, render_template, jsonify, request

# ===================================================================
# Part 1: The AI Worker Logic (from ai_worker.py)
# ===================================================================
class AIWorker:
    # This class is exactly the same as the one we perfected before.
    # All of its methods are here.
    def __init__(self, config):
        self.fleet_data = {"satellites": []}; self.mission_log = []; self.ai_model = MockAIModel()
        self.lock = threading.Lock(); self.mission_start_time = time.time(); self.log_file = "mission_log.txt"
        for i in range(5): self.fleet_data["satellites"].append({"id": f"SAT-0{i+1}", "status": "Nominal", "position": {"x":0,"y":0,"z":0}})
        with open(self.log_file, "w") as f: f.write("--- Mission Log Initialized ---\n")
    def _log_event(self, t, s, m, sev="low"):
        entry = {"timestamp": time.strftime('%H:%M:%S'), "type": t, "source": s, "message": m, "critical": sev == 'critical', "severity": sev}
        with self.lock:
            self.mission_log.append(entry);
            if len(self.mission_log) > 100: self.mission_log.pop(0)
            with open(self.log_file, "a") as f: f.write(f"[{entry['timestamp']}] ({entry['type']}) {entry['source']} -> {entry['message']}\n")
    def _update_sat_positions(self):
        t = time.time() - self.mission_start_time; e_pos = {"x": 100*math.cos(t*0.1), "y":0, "z": 100*math.sin(t*0.1)}
        for i, sat in enumerate(self.fleet_data["satellites"]):
            angle = t * (0.5 + i*0.1)
            sat['position'] = {"x": e_pos['x'] + 20*math.cos(angle), "y": 5*math.sin(t+i), "z": e_pos['z'] + 20*math.sin(angle)}
    def _check_prox_alerts(self):
        sats = self.fleet_data["satellites"]
        for i in range(len(sats)):
            for j in range(i+1, len(sats)):
                p1,p2=sats[i]['position'],sats[j]['position']; dist=math.sqrt((p1['x']-p2['x'])**2+(p1['y']-p2['y'])**2+(p1['z']-p2['z'])**2)
                if dist < 5:
                    msg = f"Proximity Alert: {sats[i]['id']} & {sats[j]['id']} too close! Dist: {dist:.2f}"
                    if not any(msg in log['message'] for log in self.mission_log[-20:]): self._log_event("ALERT", "AI_CollisionAvoidance", msg, sev="critical")
    def run_mission_loop(self):
        self._log_event("INFO", "AI_Core", "AI Worker initialized.", sev="low")
        while True:
            with self.lock:
                self._update_sat_positions(); self._check_prox_alerts()
                for sat in self.fleet_data["satellites"]:
                    if sat['status'] == "Under Diagnostics": continue
                    pred = self.ai_model.predict_anomaly({})
                    if pred["anomaly"]:
                        if sat["status"] != "Anomaly Detected": self._log_event("ALERT", "AI_AnomalyDetector", f"Anomaly in {sat['id']}", sev=pred['type'])
                        sat["status"] = "Anomaly Detected"
                    else: sat["status"] = "Nominal"
            time.sleep(2)
    def run_diagnostics(self, sat_id):
        def task():
            sat = next((s for s in self.fleet_data["satellites"] if s["id"] == sat_id), None)
            if not sat: return
            self._log_event("CMD", "AI_Core", f"Running diagnostics on {sat_id}...", sev="medium")
            with self.lock: sat['status'] = "Under Diagnostics"
            time.sleep(5)
            with self.lock: sat['status'] = "Nominal"
            self._log_event("INFO", "AI_Core", f"Diagnostics complete on {sat_id}.", sev="low")
        threading.Thread(target=task).start()
        return {"status": "success", "message": f"Diagnostics started for {sat_id}"}
    def get_fleet_status(self):
        with self.lock: return {"ai_status": "Online", "active_anomalies": sum(1 for s in self.fleet_data["satellites"] if s["status"]=="Anomaly Detected"), "total_satellites": len(self.fleet_data["satellites"]), "satellites": self.fleet_data["satellites"]}
    def get_mission_log(self):
        with self.lock: return {"ai_summary": self.ai_model.generate_narrative_summary(self.mission_log), "logs": self.mission_log[::-1]}
    def get_log_filter(self, severity=None, source=None):
        with self.lock:
            filt = self.mission_log
            if severity: filt=[l for l in filt if l.get('severity')==severity]
            if source: filt=[l for l in filt if l.get('source')==source]
            return filt[::-1]
    def get_fleet_plot(self):
        t=time.time()-self.mission_start_time; d=[100+math.sin(t+i*0.5)*10 for i in range(20)]; return {"labels": list(range(20)), "data": d}
    def get_fleet_drift(self):
        d=[random.uniform(-0.5, 0.5) for _ in range(5)]; return {"labels": [f"Axis-{i+1}" for i in range(5)], "data": d}
    def get_orbital_overlay(self):
        t=time.time()-self.mission_start_time
        with self.lock:
            e_pos={"x":100*math.cos(t*0.1),"y":0,"z":100*math.sin(t*0.1)}
            o_data=[{"id":"sun","type":"star","size":15,"color":"#FFD700","position":{"x":0,"y":0,"z":0}},{"id":"earth","type":"planet","size":5,"color":"#4D96FF","position":e_pos}]
            for sat in self.fleet_data["satellites"]: o_data.append({"id":sat['id'],"type":"satellite","size":1,"color":"#FFFFFF","position":sat['position'],"status":sat['status']})
            return o_data
    def get_navpanel(self): return {"target_lock": "Mars", "eta": "240 days"}
    def get_ambient_feed(self): return {"cosmic_radiation_level": round(random.uniform(0.1, 1.5), 2)}
class MockAIModel:
    def predict_anomaly(self, d):
        if random.random() > 0.95: return {"anomaly": True, "confidence": random.uniform(0.9, 1.0), "type": "critical"}
        if random.random() > 0.85: return {"anomaly": True, "confidence": random.uniform(0.7, 0.9), "type": "medium"}
        return {"anomaly": False}
    def generate_narrative_summary(self, log):
        if not log: return "All systems nominal."
        criticals = [l['message'] for l in log if l.get('severity') == 'critical']
        if criticals: return f"Priority Alert: {len(criticals)} critical event(s). Recent: '{criticals[-1]}'."
        return f"System normal. Monitoring {len(log)} events."

# ===================================================================
# Part 2: The Flask Server Logic (from app.py)
# ===================================================================

# Create the instances that Flask will use
worker_instance = AIWorker(config={})
flask_app = Flask(__name__)

# --- All the Flask routes, pointing to our worker_instance ---
@flask_app.route('/')
def dashboard(): return render_template('dashboard.html')
@flask_app.route('/fleetstatus')
def fleet_status(): return jsonify(worker_instance.get_fleet_status())
@flask_app.route('/fleetplot')
def fleet_plot(): return jsonify(worker_instance.get_fleet_plot())
@flask_app.route('/fleetdrift')
def fleet_drift(): return jsonify(worker_instance.get_fleet_drift())
@flask_app.route('/navpanel')
def nav_panel(): return jsonify(worker_instance.get_navpanel())
@flask_app.route('/ambientfeed')
def ambient_feed(): return jsonify(worker_instance.get_ambient_feed())
@flask_app.route('/orbitaldata')
def orbital_data(): return jsonify(worker_instance.get_orbital_overlay())
@flask_app.route('/missionlog')
def mission_log(): return jsonify(worker_instance.get_mission_log())
@flask_app.route('/logfilter')
def log_filter():
    return jsonify(worker_instance.get_log_filter(request.args.get('severity'), request.args.get('source')))
@flask_app.route('/run_diagnostics')
def run_diagnostics_route():
    return jsonify(worker_instance.run_diagnostics(request.args.get('id')))

# ===================================================================
# Part 3: The Function to Start Everything
# This is what your main app.py will call
# ===================================================================
def start_mission_control_dashboard():
    """Starts the AI worker and the Flask server in background threads."""
    print("[Mission Control] Starting AI worker thread...")
    threading.Thread(target=worker_instance.run_mission_loop, daemon=True).start()

    print("[Mission Control] Starting Flask server thread...")
    # Make Flask run in the background
    threading.Thread(target=lambda: flask_app.run(debug=False, use_reloader=False, port=5000), daemon=True).start()

    # Open the browser
    url = "http://127.0.0.1:5000"
    threading.Timer(2, lambda: webbrowser.open(url)).start()
    print(f"[Mission Control] Dashboard is active at {url}")
