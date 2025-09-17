# workers/fleetbridge_worker.py
import threading
import subprocess
import sys
import json
import time
import os
from pathlib import Path

try:
    from workers.worker_base import WorkerBase
except ImportError:
    class WorkerBase:
        def __init__(self, config): self.name = self.__class__.__name__; self.config = config or {}
        def execute_task(self, args, stop_event): raise NotImplementedError

class FleetbridgeWorker(WorkerBase):
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = Path(__file__).stem.replace('_worker', '').capitalize() + " Worker"
        self.process = None

    def execute_task(self, args: list, stop_event: threading.Event):
        print(f"[DIAG] FleetbridgeWorker.execute_task STARTED with args: {args}")
        print(f"[{self.name}] Launching the Solar Command Interface (non-blocking)...")

        python_executable = sys.executable
        script_path = Path(__file__).parent / "_fleetbridge_gui.py"
        config_path = Path(__file__).parent / "_temp_gui_config.json"

        try:
            with open(config_path, 'w') as f:
                config_to_pass = {"api_keys": self.config.get("api_keys", {})}
                json.dump(config_to_pass, f)
        except Exception as e:
            print(f"[DIAG] CRITICAL ERROR: Could not write temp config file: {e}")
            return

        def launch_gui():
            print(f"[DIAG] FleetbridgeWorker.launch_gui thread STARTED.")
            try:
                env = os.environ.copy()
                env['PYTHONPATH'] = os.pathsep.join([str(Path(__file__).parent.parent)] + os.environ.get('PYTHONPATH', '').split(os.pathsep))
                self.process = subprocess.Popen([python_executable, str(script_path)], env=env)
                print(f"[DIAG] GUI process has been launched (PID: {self.process.pid}).")
                while self.process.poll() is None and not stop_event.is_set():
                    stop_event.wait(timeout=1.0)
                if self.process.poll() is None:
                    print(f"[DIAG] Received stop signal. Terminating GUI process.")
                    self.process.terminate()
                else:
                    print(f"[DIAG] GUI process terminated. Ending watch.")
            except Exception as e:
                print(f"[DIAG] Exception in launch_gui thread: {e}")
            finally:
                if config_path.exists():
                    config_path.unlink()
                print(f"[DIAG] FleetbridgeWorker.launch_gui thread FINISHED.")

        threading.Thread(target=launch_gui, daemon=True).start()
        print(f"[DIAG] FleetbridgeWorker.execute_task FINISHED (thread launched, returning control).")

def create_worker(config: dict):
    return FleetbridgeWorker(config)
