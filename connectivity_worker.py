# workers/connectivity_worker.py
import threading
import subprocess
import sys
from pathlib import Path

try:
    from workers.worker_base import WorkerBase
except ImportError:
    class WorkerBase:
        def __init__(self, config): self.name = self.__class__.__name__; self.config = config or {}
        def execute_task(self, args, stop_event): raise NotImplementedError

# --- This section contains the Pairing Console logic ---
class PairingConsole:
    # ... (The entire PairingConsole class is perfect and does not need to be changed)
    def __init__(self):
        import tkinter as tk
        from tkinter import messagebox
        import pyttsx3
        self.tk = tk
        self.messagebox = messagebox
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 160)
        try:
            self.engine.setProperty('voice', self.engine.getProperty('voices')[0].id)
        except IndexError:
            print("[Pairing Console] No TTS voices found.")
    def speak(self, text):
        if hasattr(self.engine, '_inLoop') and self.engine._inLoop: self.engine.endLoop()
        self.engine.say(text); self.engine.runAndWait()
    def _pair_devices(self, wifi_code, bt_code):
        status = f"Initiating pairing sequence. Wi-Fi code is {wifi_code}, and the Bluetooth code is {bt_code}."
        print(f"[Pairing Console] {status}")
        self.speak(status)
        self.messagebox.showinfo("Device Pairing", status)
    def _on_submit(self):
        wifi_code = self.wifi_entry.get()
        bt_code = self.bt_entry.get()
        if all(c.isdigit() and 4 <= len(c) <= 5 for c in [wifi_code, bt_code]):
            self._pair_devices(wifi_code, bt_code)
            self.root.after(500, self.root.destroy)
        else:
            self.speak("Invalid codes. Please enter 4 to 5 digit numbers for both.")
            self.messagebox.showerror("Device Pairing", "Enter valid 4–5 digit codes.")
    def _pulse_glow(self, canvas, colors, delay=100, index=0):
        canvas.itemconfig("glow", fill=colors[index])
        next_index = (index + 1) % len(colors)
        canvas.after(delay, self._pulse_glow, canvas, colors, delay, next_index)
    def _create_glowing_entry(self, parent, label_text):
        frame = self.tk.Frame(parent, bg="black")
        label = self.tk.Label(frame, text=label_text, font=("Consolas", 12), fg="#00FF00", bg="black")
        label.pack()
        entry = self.tk.Entry(frame, font=("Consolas", 16), justify="center", bg="black", fg="#00FF00", 
                              insertbackground="#00FF00", relief="flat", bd=0)
        entry.pack(pady=(0, 2)) 
        glow = self.tk.Canvas(frame, width=200, height=5, bg="black", highlightthickness=0)
        glow.create_oval(-10, -10, 210, 15, fill="#00FF00", outline="", tags="glow")
        glow.pack() 
        pulse_colors = ["#00FF00", "#33FF99", "#00FF00", "#009966"]
        self._pulse_glow(glow, pulse_colors)
        return frame, entry
    def run(self):
        self.root = self.tk.Tk()
        self.root.title("FleetBridge Pairing Console")
        self.root.geometry("420x320")
        self.root.configure(bg="black")
        wifi_frame, self.wifi_entry = self._create_glowing_entry(self.root, "Wi-Fi Code")
        bt_frame, self.bt_entry = self._create_glowing_entry(self.root, "Bluetooth Code")
        wifi_frame.pack(pady=20)
        bt_frame.pack(pady=10)
        submit_btn = self.tk.Button(self.root, text="Pair Devices", command=self._on_submit,
                               font=("Consolas", 14), bg="#111", fg="#00FF00",
                               activebackground="#222", activeforeground="#00FF00",
                               relief="flat", padx=10, pady=5)
        submit_btn.pack(pady=20)
        self.root.mainloop()


# --- THIS IS THE NEW, SIMPLER WORKER LOGIC ---
class NetworkScannerWorker(WorkerBase):
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "Network Topographer"
    def execute_task(self, args: list, stop_event: threading.Event):
        try:
            import ssdp
        except ImportError:
            print(f"[{self.name}] The 'ssdp' library is missing. Please run 'pip install ssdp'.")
            return
        print(f"\n[{self.name}] Scanning your local network...")
        try:
            devices = ssdp.discover(timeout=5, retries=2)
            if stop_event.is_set(): print(f"[{self.name}] Scan cancelled."); return
            if not devices: print(f"\n[{self.name}] Scan complete. No devices found."); return
            print(f"\n--- Discovered Devices ---")
            for i, device in enumerate(devices):
                print(f"  {i+1}. {device.server or 'Unknown Device':<50} IP: {device.host}")
            print(f"--------------------------")
        except Exception as e:
            print(f"[{self.name}] An error occurred during scan: {e}")

class PairingConsoleWorker(WorkerBase):
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "Pairing Console"
    def execute_task(self, args: list, stop_event: threading.Event):
        print(f"[{self.name}] Launching the Pairing Console interface...")
        process = subprocess.Popen([sys.executable, __file__, "--run-gui"])
        while process.poll() is None and not stop_event.is_set():
            try: stop_event.wait(timeout=1.0)
            except (KeyboardInterrupt, SystemExit): break
        if process.poll() is None:
            process.terminate()
            print(f"[{self.name}] GUI process terminated.")

