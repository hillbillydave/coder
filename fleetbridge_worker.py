# workers/fleetbridge_worker.py
import threading
import subprocess
import sys
import json
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
        self.name = "FleetBridge Orchestrator"
        self.process = None

    def execute_task(self, args: list, stop_event: threading.Event):
        print(f"[{self.name}] Launching the Solar Command Interface...")
        
        python_executable = sys.executable
        script_path = Path(__file__).parent / "_fleetbridge_gui.py"
        
        # This is the temporary file path for passing the config
        config_path = Path(__file__).parent / "_temp_gui_config.json"
        
        # --- THIS IS THE FIX ---
        # The 'with open...' block was missing its indentation and had syntax errors.
        # It is now correct.
        try:
            with open(config_path, 'w') as f:
                config_to_pass = {"api_keys": self.config.get("api_keys", {})}
                json.dump(config_to_pass, f)
        except Exception as e:
            print(f"[{self.name}] CRITICAL ERROR: Could not write temp config file: {e}")
            return # Stop the task if we can't write the config
        # --- END OF FIX ---

        try:
            self.process = subprocess.Popen([python_executable, str(script_path)])
            print(f"[{self.name}] GUI process has been launched (PID: {self.process.pid}).")
        except FileNotFoundError:
            print(f"[{self.name}] CRITICAL ERROR: Could not find the GUI script at '{script_path}'.")
            return
        except Exception as e:
            print(f"[{self.name}] CRITICAL ERROR: Failed to launch GUI process: {e}")
            return

        while self.process.poll() is None and not stop_event.is_set():
            try:
                stop_event.wait(timeout=1.0)
            except (KeyboardInterrupt, SystemExit):
                break
        
        if self.process.poll() is None:
            print(f"[{self.name}] Received stop signal. Terminating GUI process.")
            self.process.terminate()
        else:
            print(f"[{self.name}] GUI process terminated. Ending watch.")
        
        # Clean up the temporary config file
        if config_path.exists():
            config_path.unlink()

def create_worker(config: dict):
    return FleetbridgeWorker(config)
