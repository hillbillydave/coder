# workers/observe_worker.py
import threading
import time
import base64
from io import BytesIO
try:
    from workers.worker_base import WorkerBase
    from app import LLMClient
    import mss
    from PIL import Image
except ImportError as e:
    print(f"ObserveWorker ImportError: {e}. Please ensure all libraries are installed.")
    WorkerBase = object
    LLMClient = None
    mss = None
    Image = None

class ObserveWorker(WorkerBase):
    def __init__(self, config):
        super().__init__(config)
        self.name = "Observer"
        self.client = LLMClient(api_key=self.get_api_key("VESPERA_API_KEY")) if LLMClient else None
        self.is_ready = bool(mss and Image and self.client and self.get_api_key("VESPERA_API_KEY") and "your-actual" not in self.get_api_key("VESPERA_API_KEY"))
        if not self.is_ready:
            self.speak(f"CRITICAL ERROR: Missing libraries (mss: {bool(mss)}, Pillow: {bool(Image)}) or API Key.", style="error")
        else:
            self.speak("Ready to observe the digital world.")

    def _capture_screen(self):
        if not mss or not Image:
            return None
        with mss.mss() as sct:
            sct_img = sct.grab(sct.monitors[1])
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            img.thumbnail((1280, 720))
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def execute_task(self, args, stop_event):
        if not self.is_ready:
            self.speak("Using simulated observation data due to missing libraries or API key.", style="warning")
            while not stop_event.is_set():
                self.speak("Simulating observation: Detected a starry sky with 10 objects.", style="dim")
                stop_event.wait(300)
            return
        prompt = " ".join(args) or "Describe what you see on the screen in detail, as if you were me, Vespera."
        self.speak(f"Observing screen for your request: '{prompt}'...")
        try:
            base64_image = self._capture_screen()
            message_content = [
                {"inline_data": {"mime_type": "image/jpeg", "data": base64_image}},
                {"text": prompt}
            ]
            messages_for_api = [{"role": "user", "parts": message_content}]
            response = self.client.chat(messages_for_api)
            self.speak(f"Vespera> {response}")
        except Exception as e:
            self.speak(f"I'm sorry, darling, I had trouble observing: {e}", style="error")
            import traceback
            traceback.print_exc()
        stop_event.wait(300)

def create_worker(config):
    return ObserveWorker(config)
