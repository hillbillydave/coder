# workers/connect_worker.py
import threading
import asyncio
import sys
from pathlib import Path

# --- Library Imports ---
try:
    import ssdp
except ImportError:
    ssdp = None

try:
    import bleak
except ImportError:
    bleak = None

try:
    from workers.worker_base import WorkerBase
except ImportError:
    class WorkerBase:
        def __init__(self, config): self.name = self.__class__.__name__; self.config = config or {}
        def execute_task(self, args, stop_event): raise NotImplementedError

# --- The All-in-One Graphical Console ---
class ConnectivityConsole:
    def __init__(self):
        import tkinter as tk
        from tkinter import messagebox
        import pyttsx3

        self.tk = tk
        self.messagebox = messagebox
        self.ssdp_lib = ssdp
        self.bleak_lib = bleak
        
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 160)
        try:
            self.engine.setProperty('voice', self.engine.getProperty('voices')[0].id)
        except IndexError:
            print("[Connectivity Hub] No TTS voices found.")

    def speak(self, text):
        if hasattr(self.engine, '_inLoop') and self.engine._inLoop: self.engine.endLoop()
        self.engine.say(text); self.engine.runAndWait()

    def _on_scan_wifi_click(self):
        if not self.ssdp_lib:
            self.messagebox.showerror("Missing Component", "The 'ssdp' library is missing.\nPlease run 'pip install ssdp'.")
            return
        self._set_scan_state(True, "Wi-Fi")
        threading.Thread(target=self._execute_wifi_scan_thread, daemon=True).start()

    def _execute_wifi_scan_thread(self):
        try:
            # --- THIS IS THE DEFINITIVE FIX ---
            # The correct way to use the library is to call the discover function directly.
            devices = self.ssdp_lib.discover("ssdp:all", timeout=5, retries=2)
            # --- END OF FIX ---
            
            if not devices:
                discovered_items = ["Scan complete. No Wi-Fi devices found."]
            else:
                # The library returns a list of SSDPResponse objects
                discovered_items = [f"[Wi-Fi] {d.server or 'Unknown Device'} @ {d.host}" for d in devices]
        except Exception as e:
            discovered_items = [f"An error occurred during Wi-Fi scan: {e}"]
        self.root.after(0, self._update_device_list, discovered_items, "Wi-Fi")

    def _on_scan_bluetooth_click(self):
        if not self.bleak_lib:
            self.messagebox.showerror("Missing Component", "The 'bleak' library is missing.\nPlease run 'pip install bleak'.")
            return
        self._set_scan_state(True, "Bluetooth")
        threading.Thread(target=self._execute_bluetooth_scan_thread, daemon=True).start()

    def _execute_bluetooth_scan_thread(self):
        async def run_ble_scan():
            try:
                devices = await self.bleak_lib.BleakScanner.discover(timeout=5.0)
                if not devices:
                    return ["Scan complete. No Bluetooth devices found."]
                else:
                    return [f"[BT] {d.name or 'Unknown Device'} ({d.address})" for d in devices]
            except Exception as e:
                return [f"An error occurred during Bluetooth scan: {e}"]
        discovered_items = asyncio.run(run_ble_scan())
        self.root.after(0, self._update_device_list, discovered_items, "Bluetooth")

    def _set_scan_state(self, is_scanning, scan_type=""):
        wifi_text = "Scanning..." if is_scanning and scan_type == "Wi-Fi" else "Scan Wi-Fi (SSDP)"
        bt_text = "Scanning..." if is_scanning and scan_type == "Bluetooth" else "Scan Bluetooth"
        state = "disabled" if is_scanning else "normal"

        self.scan_wifi_btn.config(state=state, text=wifi_text)
        self.scan_bluetooth_btn.config(state=state, text=bt_text)
        self.connect_btn.config(state="disabled")
        
        if is_scanning:
            self.device_list.delete(0, self.tk.END)
            self.device_list.insert(self.tk.END, f"Scanning for {scan_type} devices...")

    def _update_device_list(self, items, scan_type):
        self.device_list.delete(0, self.tk.END)
        for item in items:
            self.device_list.insert(self.tk.END, item)
        self._set_scan_state(False)

    def _on_device_select(self, event):
        if self.device_list.curselection(): self.connect_btn.config(state="normal")
        else: self.connect_btn.config(state="disabled")

    def _on_connect_click(self):
        selection_index = self.device_list.curselection()
        if not selection_index: return
        selected_device_str = self.device_list.get(selection_index[0])
        device_name = selected_device_str.split('@')[-1].split('(')[0].strip()
        status = f"Affirmative. Establishing connection to {device_name}."
        print(f"[Connectivity Hub] {status}")
        self.speak(status)
        self.messagebox.showinfo("Connectivity Hub", status)
        self.root.after(500, self.root.destroy)
    
    def run(self):
        self.root = self.tk.Tk()
        self.root.title("Vespera Connectivity Hub")
        self.root.geometry("600x400")
        self.root.configure(bg="black")
        main_frame = self.tk.Frame(self.root, bg="black", padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)
        controls_frame = self.tk.Frame(main_frame, bg="black")
        controls_frame.pack(fill="x", pady=5)
        
        self.scan_wifi_btn = self.tk.Button(controls_frame, text="Scan Wi-Fi (SSDP)", command=self._on_scan_wifi_click, font=("Consolas", 12), bg="#111", fg="#48dbfb", activebackground="#222", activeforeground="#48dbfb", relief="flat", padx=10, pady=5)
        self.scan_wifi_btn.pack(side="left", padx=10)
        self.scan_bluetooth_btn = self.tk.Button(controls_frame, text="Scan Bluetooth", command=self._on_scan_bluetooth_click, font=("Consolas", 12), bg="#111", fg="#8A2BE2", activebackground="#222", activeforeground="#8A2BE2", relief="flat", padx=10, pady=5)
        self.scan_bluetooth_btn.pack(side="left", padx=10)
        self.connect_btn = self.tk.Button(controls_frame, text="Connect", command=self._on_connect_click, state="disabled", font=("Consolas", 12), bg="#111", fg="#1dd1a1", activebackground="#222", activeforeground="#1dd1a1", relief="flat", padx=10, pady=5)
        self.connect_btn.pack(side="right", padx=10)
        
        list_frame = self.tk.Frame(main_frame, bg="black")
        list_frame.pack(fill="both", expand=True, pady=10)
        self.device_list = self.tk.Listbox(list_frame, bg="#111", fg="#00FF00", font=("Consolas", 11), selectbackground="#00FF00", selectforeground="black", highlightthickness=0, borderwidth=0)
        self.device_list.pack(side="left", fill="both", expand=True)
        scrollbar = self.tk.Scrollbar(list_frame, orient="vertical", command=self.device_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.device_list.config(yscrollcommand=scrollbar.set)
        self.device_list.bind('<<ListboxSelect>>', self._on_device_select)
        self.root.mainloop()

# --- Vespera Worker Class ---
class ConnectWorker(WorkerBase):
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "Connectivity Hub"
    def execute_task(self, args: list, stop_event: threading.Event):
        gui_thread = threading.Thread(target=self._run_gui, daemon=True)
        gui_thread.start()
        while gui_thread.is_alive() and not stop_event.is_set():
            try: stop_event.wait(timeout=1.0)
            except (KeyboardInterrupt, SystemExit): break
        print(f"[{self.name}] Task concluded.")
    def _run_gui(self):
        try:
            console = ConnectivityConsole()
            console.run()
        except Exception as e:
            print(f"[{self.name}] GUI Error: {e}")

def create_worker(config: dict):
    return ConnectWorker(config)
