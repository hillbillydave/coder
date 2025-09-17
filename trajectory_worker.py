# workers/trajectory_worker.py
import threading
from typing import List

from workers.worker_base import WorkerBase

class TrajectoryWorker(WorkerBase):
    """
    A user-facing worker that acts as a gateway. It takes plotting
    commands from the user and places a formal request on the shared queue
    for the Trajectory Analyst to process.
    """
    def __init__(self, config: dict):
        super().__init__(config)
        self.shared_queue = config.get("shared_queue")

    def can_handle(self, args: list) -> bool:
        """This worker handles the 'plot' subcommand."""
        if not args:
            return False
        return args[0].lower() == "plot"

    def execute_task(self, args: List[str], stop_event: threading.Event):
        """Takes user input and sends a PLOT_REQUEST to the shared queue."""
        if not self.can_handle(args):
            return super().execute_task(args, stop_event)
        
        if not self.shared_queue:
            self.speak("I can't send requests without a connection to the shared queue.")
            return

        if len(args) < 2:
            self.speak("Please specify an object to plot. Usage: trajectory plot <object_name_or_id>")
            return
            
        object_id = ' '.join(args[1:])
        
        # This is the worker's entire job: create and send the message.
        plot_request_message = {
            "type": "PLOT_REQUEST",
            "payload": {
                "object_id": object_id
            }
        }
        
        self.shared_queue.put(plot_request_message)
        self.speak(f"Request sent. The Trajectory Analyst will now plot the course for '{object_id}'.")


def create_worker(config: dict) -> TrajectoryWorker:
    """Standard entry point for the AI to 'hire' this worker."""
    return TrajectoryWorker(config)
