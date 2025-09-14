# workers/shop_code_worker.py
import json
import os
import time
import threading
import psutil
import socket
from pathlib import Path
from workers.worker_base import WorkerBase
from workers.connectivity_worker import PairingConsoleWorker

try:
    import obd
except ImportError:
    obd = None
    print("[ShopCodeWorker] Warning: 'obd' library not found. Install with 'pip install obd' in venv.")

def create_worker(config: dict):
    return ShopCodeWorker(config)

class ShopCodeWorker(WorkerBase):
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "ShopCodeWorker"
        self.task_templates = self.load_task_templates()
        self.use_db = config.get("use_db", True)
        if self.use_db:
            try:
                from database import ShopHubLite
                self.db = ShopHubLite()
            except ImportError:
                print(f"[{self.name}] Warning: database.py not found, running without DB.")
                self.use_db = False

    def load_task_templates(self):
        config_path = Path("workers") / "config.json"
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get("diagnostics", {})
            else:
                print(f"[{self.name}] Config file {config_path} not found, using default templates.")
                return {}
        except Exception as e:
            print(f"[{self.name}] Error loading config: {e}")
            return {}

    def execute_task(self, args: list, stop_event: threading.Event):
        if not args:
            print(f"[{self.name}] Please specify a task (e.g., obdii_scan, battery_integration).")
            return
        
        task_name = args[0].lower()
        wo_id = int(args[1]) if len(args) > 1 and args[1].isdigit() else 0
        connector = None
        use_real_obd = args[2].lower() == "real" if len(args) > 2 else False
        wifi_ip = args[3] if len(args) > 3 else "192.168.0.10"
        wifi_port = int(args[4]) if len(args) > 4 and args[4].isdigit() else 35000

        if task_name in ["obdii_scan", "ecu_tuning", "vats_reprogram", "elm327", "j2534"]:
            if not use_real_obd:
                try:
                    from connector import FakeElm327Connector, FakeJ2534Connector
                    connector_type = args[2] if len(args) > 2 else "basic"
                    connector = FakeElm327Connector() if connector_type in ["basic", "elm327"] else FakeJ2534Connector()
                except ImportError:
                    print(f"[{self.name}] Error: connector.py not found. Required for mock mode.")
                    return
        kwargs = {"system_voltage": 350, "power_needs": 1000} if task_name == "battery_integration" else {}

        try:
            if task_name in self.task_templates:
                task = self.task_templates[task_name]
                print(f"[{self.name}] Running task: {task['description']}")
                
                if stop_event.is_set():
                    print(f"[{self.name}] Task {task_name} cancelled.")
                    return
                
                exec_locals = {}
                if task_name == "obdii_scan":
                    if not connector and not use_real_obd:
                        print(f"[{self.name}] Error: OBD-II scan requires a connector in mock mode.")
                        return
                    if use_real_obd and not obd:
                        print(f"[{self.name}] Error: 'obd' library required for real OBD-II. Install with 'pip install obd' in venv.")
                        return
                    exec(task["code"], {"connector": connector, "obd": obd, "wifi_ip": wifi_ip, "wifi_port": wifi_port}, exec_locals)
                    result = exec_locals["scan_obdii"](connector, use_real_obd, wifi_ip, wifi_port)
                elif task_name == "battery_integration":
                    exec(task["code"], {}, exec_locals)
                    result = exec_locals["integrate_m18_battery"](kwargs["system_voltage"], kwargs["power_needs"])
                elif task_name in ["ecu_tuning", "elm327", "j2534"]:
                    if not connector:
                        print(f"[{self.name}] Error: {task_name} requires a connector.")
                        return
                    exec(task["code"], {"connector": connector}, exec_locals)
                    result = exec_locals[task_name.replace("_", "_")](connector)
                elif task_name == "vats_reprogram":
                    if not connector:
                        print(f"[{self.name}] Error: VATS reprogramming requires a connector.")
                        return
                    exec(task["code"], {"connector": connector}, exec_locals)
                    result = exec_locals["reprogram_vats"](connector)
                else:
                    exec(task["code"], {}, exec_locals)
                    result = exec_locals[task_name.replace("_", "_")]()
                
                if self.use_db and wo_id:
                    dtc_string = result.get("dtc_codes", result.get("result", str(result)))
                    if isinstance(dtc_string, list):
                        dtc_string = "\n".join(dtc_string)
                    self.db.link_diagnostic_report(
                        wo_id,
                        task["description"],
                        result.get("vin", "N/A"),
                        dtc_string
                    )
                
                print(f"[{self.name}] Result: {result}")
            else:
                print(f"[{self.name}] Error: Task '{task_name}' not found.")
        except Exception as e:
            print(f"[{self.name}] Error executing task: {str(e)}")
        finally:
            if stop_event.is_set():
                print(f"[{self.name}] Task {task_name} stopped.")

    def monitor_system(self):
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory().percent
            return {"system_id": "SYS001", "cpu_usage": cpu_usage, "memory_usage": memory}
        except Exception as e:
            return {"error": f"System monitoring failed: {str(e)}"}
