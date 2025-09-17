# subsystems/coredeck_gui.py
from flask import Flask, jsonify, request
from queue import Queue
from subsystems.modules.EngineeringSuiteWorker import EngineeringSuiteWorker

class CoreDeckWebApp:
    def __init__(self, config, result_queue):
        self.server = Flask(__name__, template_folder="gui/templates", static_folder="gui/static")
        self.config = config
        self.result_queue = result_queue
        self.setup_routes()

    def setup_routes(self):
        @self.server.route('/')
        def index():
            return self.server.send_static_file('dashboard.html')

        @self.server.route('/daisy_engineering_metrics')
        def daisy_engineering_metrics():
            try:
                worker = EngineeringSuiteWorker(self.config, self.result_queue)
                return jsonify(worker.get_metrics())
            except Exception as e:
                print(f"[CoreDeckWeb] Daisy engineering metrics error: {e}")
                return jsonify({"error": str(e)}), 500

        @self.server.route('/daisy_engineering_command', methods=['POST'])
        def daisy_engineering_command():
            try:
                worker = EngineeringSuiteWorker(self.config, self.result_queue)
                data = request.json
                command = data.get('command', '')
                args = data.get('args', [])
                result = worker.execute_task([command] + args, None)
                return jsonify(result)
            except Exception as e:
                print(f"[CoreDeckWeb] Daisy command error: {e}")
                return jsonify({"error": str(e)}), 500

    def run(self, stop_event):
        print("🌐 Starting Flask server at http://127.0.0.1:5001")
        self.server.run(host="127.0.0.1", port=5001, debug=False, use_reloader=False)

if __name__ == "__main__":
    app = CoreDeckWebApp({"api_keys": {}, "workers": {}}, Queue())
    app.run(None)
