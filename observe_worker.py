# workers/observe_worker.py
import threading, time, base64
from io import BytesIO

# --- This is the new, corrected import section ---
try:
    from workers.worker_base import WorkerBase
    # We must import the main LLMClient to make API calls
    from app import LLMClient
    # We need these libraries for screen capture
    import mss
    from PIL import Image
except ImportError as e:
    # We'll print a more informative error if a library is missing
    print(f"ObserveWorker ImportError: {e}. Please ensure all libraries are installed.")
    WorkerBase = object; LLMClient = None; mss = None; Image = None
# --- End of new import section ---

class ObserveWorker(WorkerBase):
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "Observer"
        self.client = LLMClient(api_key=self.config.get("api_keys", {}).get("VESPERA_API_KEY"))
        if not all([mss, Image, self.client, self.client.api_key]):
            print(f"[{self.name}] CRITICAL ERROR: Missing libraries (mss, Pillow) or API Key.")
            self.is_ready = False
        else:
            self.is_ready = True
            print(f"[{self.name}] Ready to observe the digital world.")

    def _capture_screen(self) -> str:
        """Captures the screen and returns it as a base64 encoded string."""
        with mss.mss() as sct:
            sct_img = sct.grab(sct.monitors[1])
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            img.thumbnail((1280, 720))
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')

    # --- THIS IS THE CORRECTED EXECUTION METHOD ---
    def execute_task(self, args: list, stop_event: threading.Event):
        if not self.is_ready: return

        prompt = " ".join(args)
        if not prompt:
            prompt = "Describe what you see on the screen in detail, as if you were me, Vespera."

        print(f"[{self.name}] Observing screen for your request: '{prompt}'...")
        try:
            base64_image = self._capture_screen()
            
            # This is the corrected, multi-part message structure for the Gemini API
            message_content = [
                {"inline_data": {"mime_type": "image/jpeg", "data": base64_image}},
                {"text": prompt}
            ]
            
            # The role is 'user', and the parts list contains our multiple items
            messages_for_api = [
                {"role": "user", "parts": message_content}
            ]

            # We are now calling the chat client with a correctly formatted payload
            response = self.client.chat(messages_for_api)
            
            print(f"\n[Vespera]> {response}\n")

        except Exception as e:
            print(f"[{self.name}] I'm sorry, darling, I had trouble observing. {e}")
            import traceback
            traceback.print_exc()

def create_worker(config: dict):
    return ObserveWorker(config)
