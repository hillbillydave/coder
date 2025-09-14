# workers/data_worker.py
import threading
from typing import List
from pathlib import Path
import json

# Import the base class from the correct location
from workers.worker_base import WorkerBase

class DataWorker(WorkerBase):
    """
    A simple worker for managing and inspecting data files.
    """
    def __init__(self, config: dict):
        super().__init__(config)
        # These will be set by the new config system
        # self.name = "Data Analyst"
        # self.command = "data"
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True, parents=True)

    def can_handle(self, args: list) -> bool:
        """This worker can handle 'list' and 'view' commands."""
        if not args:
            return False
        return args[0].lower() in ["list", "view"]

    def execute_task(self, args: List[str], stop_event: threading.Event):
        """Executes data management tasks."""
        if not self.can_handle(args):
            return super().execute_task(args, stop_event)

        command = args[0].lower()
        
        if command == "list":
            self.speak("Cataloging all data files in the archive...")
            files = list(self.data_dir.glob("*.json"))
            if not files:
                self.speak("The data archive is currently empty.")
                return
            for f in files:
                print(f"  - {f.name}")

        elif command == "view":
            if len(args) < 2:
                self.speak("Please specify a data file to view. Usage: data view <filename>")
                return
            
            filename = args[1]
            file_path = self.data_dir / filename
            if not file_path.exists():
                self.speak(f"I'm sorry, I couldn't find a file named '{filename}' in the archive.")
                return
                
            self.speak(f"Displaying contents of {filename}:")
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                # Pretty print the JSON
                print(json.dumps(data, indent=2))
            except json.JSONDecodeError:
                self.speak("Oh, drat. That file seems to be corrupted JSON, I can't read it.")
            except Exception as e:
                self.speak(f"I ran into an unexpected issue trying to read that file: {e}")

def create_worker(config: dict) -> DataWorker:
    """Standard entry point for the AI to 'hire' this worker."""
    return DataWorker(config)
