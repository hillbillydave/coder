from flask import Flask, jsonify, request
import webview
from queue import Queue
from subsystems.modules.DaisyEngineeringWorker import DaisyEngineeringWorker

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
                worker = DaisyEngineeringWorker(self.config, self.result_queue)
                return jsonify(worker.get_metrics())
            except Exception as e:
                print(f"[CoreDeckWeb] Daisy engineering metrics error: {e}")
                return jsonify({"error": str(e)}), 500

        @self.server.route('/daisy_engineering_command', methods=['POST'])
        def daisy_engineering_command():
            try:
                worker = DaisyEngineeringWorker(self.config, self.result_queue)
                data = request.json
                command = data.get('command', '')
                args = data.get('args', [])
                result = worker.execute_task([command] + args, None)
                return jsonify(result)
            except Exception as e:
                print(f"[CoreDeckWeb] Daisy command error: {e}")
                return jsonify({"error": str(e)}), 500

    def run(self, stop_event):
        window = webview.create_window("Daisy’s Starship", 'http://127.0.0.1:5001/', width=1600, height=900)
        window.loaded += lambda: window.evaluate_js('window.webkit.messageHandlers.inspector.postMessage("show")')
        def on_closing():
            stop_event.set()
        window.events.closing += on_closing
        self.server.run(host="127.0.0.1", port=5001, debug=False, use_reloader=False)
        webview.start(debug=True, http_server=False)

if __name__ == "__main__":
    app = CoreDeckWebApp({"api_keys": {}, "workers": {}}, Queue())
    app.run(None)
