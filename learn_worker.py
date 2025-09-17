# workers/fleetbridge_worker.py
import multiprocessing
import threading
import webview
import time
import json
import random
from typing import List, Dict
from pathlib import Path

# Use an absolute import for robustness
from workers.worker_base import WorkerBase

# ==============================================================================
# 1. EMBEDDED FRONTEND ASSETS
# ==============================================================================
# --- PASTE YOUR FULL HTML, CSS, AND JS STRING VARIABLES HERE ---
HTML_CONTENT = """ ... """
CSS_CONTENT = """ ... """
INTERFACE_JS_CONTENT = """ ... """

# ==============================================================================
# THE GUI APPLICATION LOGIC (NOW SEPARATED)
# ==============================================================================

# This class will be instantiated in the new process
class GuiApi:
    def __init__(self):
        self.window = None

    def generate_terrain(self, payload: dict):
        # Note: This runs in a different process, so it can't call self.speak
        print("[FleetBridge GUI] Received terrain generation request.")
        start_time = time.time()
        width = payload.get('width', 128); height = payload.get('height', 128)
        vertices = [random.uniform(0, 50) for _ in range(width * height)]
        time.sleep(1.5)
        generation_time = round((time.time() - start_time) * 1000)
        print(f"[FleetBridge GUI] Terrain generated in {generation_time}ms.")
        return { "vertices": vertices, "generation_time": generation_time }

    def shutdown(self):
        if self.window:
            self.window.destroy()

def run_gui_process():
    """This function is the entry point for the new GUI process."""
    import sys
    from queue import Queue
    from flask import Flask, request, jsonify
    
    # Add parent dir to path to allow imports
    sys.path.append(str(Path(__file__).parent.parent))

    gui_data_queue = Queue()
    api = GuiApi()

    def _queue_listener(window):
        while True:
            data = gui_data_queue.get()
            if window:
                json_data_str = json.dumps(data)
                window.evaluate_js(f'handleWorkerUpdate({json.dumps(json_data_str)})')

    server = Flask(__name__)
    @server.route('/update', methods=['POST'])
    def receive_update():
        gui_data_queue.put(request.json)
        return jsonify({"status": "success"})

    def run_server():
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        server.run(host='127.0.0.1', port=5555)

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    def load_asset(request):
        if request.url.endswith('style.css'): return CSS_CONTENT, 'text/css'
        if request.url.endswith('interface.js'): return INTERFACE_JS_CONTENT, 'application/javascript'
        return None, None

    window = webview.create_window(
        '🛰️ FleetBridge — Solar Command Interface',
        html=HTML_CONTENT, js_api=api, width=1600, height=900, frameless=True
    )
    api.window = window
    
    listener_thread = threading.Thread(target=_queue_listener, args=(window,), daemon=True)
    listener_thread.start()
    
    print("[FleetBridge GUI] Process started. Ready and listening on port 5555.")
    webview.start(http_server=True, func=load_asset, debug=False)

# ==============================================================================
# THE AI WORKER CLASS (NOW JUST A SIMPLE LAUNCHER)
# ==============================================================================

class FleetBridgeWorker(WorkerBase):
    def __init__(self, config: dict):
        super().__init__(config)
        self.gui_process = None

    def execute_task(self, args: List[str], stop_event: threading.Event):
        """Launches the GUI in a completely separate, independent process."""
        if self.gui_process and self.gui_process.is_alive():
            self.speak("The Solar Command Interface is already running, honey.")
            return
            
        self.speak("Launching the Solar Command Interface...")
        
        # multiprocessing.Process is a robust way to run a function in a new process
        self.gui_process = multiprocessing.Process(target=run_gui_process)
        self.gui_process.start()
        
        self.speak("GUI process launched. Control returned to main AI.")

def create_worker(config: dict) -> FleetBridgeWorker:
    """Standard entry point for the AI to 'hire' this worker."""
    return FleetBridgeWorker(config)
