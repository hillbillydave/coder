# ai_worker.py

import time
import random
import threading
import math
import json

class MockAIModel:
    def predict_anomaly(self, sensor_data):
        if random.random() > 0.95: return {"anomaly": True, "confidence": random.uniform(0.9, 1.0), "type": "critical"}
        elif random.random() > 0.85: return {"anomaly": True, "confidence": random.uniform(0.7, 0.9), "type": "medium"}
        return {"anomaly": False}

    def generate_narrative_summary(self, mission_log):
        if not mission_log: return "All systems nominal. Awaiting telemetry data."
        critical_events = [log['message'] for log in mission_log if log.get('severity') == 'critical']
        if critical_events: return f"Priority Alert: Detected {len(critical_events)} critical event(s). Most recent: '{critical_events[-1]}'. Recommend immediate review."
        return f"System status normal. Monitoring {len(mission_log)} recent events. No critical alerts."

class AIWorker:
    def __init__(self, config):
        self.config = config
        self.fleet_data = {"satellites": []}
        self.mission_log = []
        self.ai_model = MockAIModel()
        self.lock = threading.Lock()
        self.mission_start_time = time.time()
        self.log_file = "mission_log.txt"

        for i in range(5):
            self.fleet_data["satellites"].append({
                "id": f"SAT-0{i+1}", "status": "Nominal",
                "position": {"x": 0, "y": 0, "z": 0}, "velocity": random.randint(7000, 8000)
            })
        
        with open(self.log_file, "w") as f: f.write("--- Mission Log Initialized ---\n")

    def _log_event(self, log_type, source, message, severity="low"):
        log_entry = { "timestamp": time.strftime('%H:%M:%S'), "type": log_type, "source": source, "message": message, "critical": severity == 'critical', "severity": severity }
        with self.lock:
            self.mission_log.append(log_entry)
            if len(self.mission_log) > 100: self.mission_log.pop(0)
            with open(self.log_file, "a") as f: f.write(f"[{log_entry['timestamp']}] ({log_entry['type']}) {log_entry['source']} -> {log_entry['message']}\n")

    def _update_satellite_positions(self):
        elapsed_time = time.time() - self.mission_start_time
        earth_pos = { "x": 100 * math.cos(elapsed_time * 0.1), "y": 0, "z": 100 * math.sin(elapsed_time * 0.1) }
        for i, sat in enumerate(self.fleet_data["satellites"]):
            angle = elapsed_time * (0.5 + i * 0.1)
            sat['position'] = { "x": earth_pos['x'] + 20 * math.cos(angle), "y": 5 * math.sin(elapsed_time + i), "z": earth_pos['z'] + 20 * math.sin(angle) }

    def _check_proximity_alerts(self):
        PROXIMITY_THRESHOLD = 5
        sats = self.fleet_data["satellites"]
        for i in range(len(sats)):
            for j in range(i + 1, len(sats)):
                p1, p2 = sats[i]['position'], sats[j]['position']
                distance = math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2 + (p1['z'] - p2['z'])**2)
                if distance < PROXIMITY_THRESHOLD:
                    log_message = f"Proximity Alert: {sats[i]['id']} and {sats[j]['id']} are too close! Dist: {distance:.2f}"
                    if not any(log_message in log['message'] for log in self.mission_log[-20:]):
                        self._log_event("ALERT", "AI_CollisionAvoidance", log_message, severity="critical")

    def run_mission_loop(self):
        self._log_event("INFO", "AI_Core", "AI Worker initialized and running.", severity="low")
        while True:
            with self.lock:
                self._update_satellite_positions()
                self._check_proximity_alerts()
                for sat in self.fleet_data["satellites"]:
                    if sat['status'] == "Under Diagnostics": continue
                    prediction = self.ai_model.predict_anomaly({})
                    if prediction["anomaly"]:
                        # Only log the event if the status is changing to anomaly
                        if sat["status"] != "Anomaly Detected":
                            self._log_event("ALERT", "AI_AnomalyDetector", f"Anomaly in {sat['id']} | Confidence: {prediction['confidence']:.1%}", severity=prediction['type'])
                        sat["status"] = "Anomaly Detected"
                    else:
                        # FIX: If the anomaly is gone, set it back to Nominal
                        sat["status"] = "Nominal"
            time.sleep(2)

    def run_diagnostics(self, satellite_id):
        def task():
            sat_to_fix = next((s for s in self.fleet_data["satellites"] if s["id"] == satellite_id), None)
            if not sat_to_fix: return
            self._log_event("CMD", "AI_Core", f"Running diagnostics on {satellite_id}...", severity="medium")
            with self.lock: sat_to_fix['status'] = "Under Diagnostics"
            time.sleep(5)
            with self.lock: sat_to_fix['status'] = "Nominal"
            self._log_event("INFO", "AI_Core", f"Diagnostics complete on {satellite_id}. All systems nominal.", severity="low")
        threading.Thread(target=task).start()
        return {"status": "success", "message": f"Diagnostics started for {satellite_id}"}
        
    def get_fleet_status(self):
        with self.lock:
            # We need to send the full satellite data here for the selection panel to stay in sync
            return {
                "ai_status": "Online | Real-time Monitoring Active",
                "active_anomalies": sum(1 for s in self.fleet_data["satellites"] if s["status"] == "Anomaly Detected"),
                "total_satellites": len(self.fleet_data["satellites"]),
                "satellites": self.fleet_data["satellites"] # NEW: Send all satellite data
            }

    # --- All other get_* methods remain the same ---
    def get_mission_log(self):
        with self.lock: return {"ai_summary": self.ai_model.generate_narrative_summary(self.mission_log), "logs": self.mission_log[::-1]}
    def get_log_filter(self, severity=None, source=None):
        with self.lock:
            filtered = self.mission_log
            if severity: filtered = [log for log in filtered if log.get('severity') == severity]
            if source: filtered = [log for log in filtered if log.get('source') == source]
            return filtered[::-1]
    def get_fleet_plot(self):
        elapsed_time = time.time() - self.mission_start_time
        data = [100 + math.sin(elapsed_time + i * 0.5) * 10 for i in range(20)]
        return {"labels": list(range(20)), "data": data}
    def get_fleet_drift(self):
        data = [random.uniform(-0.5, 0.5) for i in range(5)]
        return {"labels": [f"Axis-{i+1}" for i in range(5)], "data": data}
    def get_orbital_overlay(self):
        elapsed_time = time.time() - self.mission_start_time
        with self.lock:
            earth_pos = {"x": 100 * math.cos(elapsed_time * 0.1), "y": 0, "z": 100 * math.sin(elapsed_time * 0.1)}
            orbital_data = [
                {"id": "sun", "type": "star", "size": 15, "color": "#FFD700", "position": {"x": 0, "y": 0, "z": 0}},
                {"id": "earth", "type": "planet", "size": 5, "color": "#4D96FF", "position": earth_pos}
            ]
            for sat in self.fleet_data["satellites"]:
                orbital_data.append({"id": sat['id'], "type": "satellite", "size": 1, "color": "#FFFFFF", "position": sat['position'], "status": sat['status']})
        return orbital_data
    def get_navpanel(self): return {"target_lock": "Mars", "eta": "240 days"}
    def get_ambient_feed(self): return {"cosmic_radiation_level": round(random.uniform(0.1, 1.5), 2)}
