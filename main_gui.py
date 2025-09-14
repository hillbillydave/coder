# main_gui.py
import tkinter as tk
from tkinter import scrolledtext
import threading
import json
import time
import os
import speech_recognition as sr
import pyttsx3
import importlib.util
from pathlib import Path

# --- Secure Configuration Loader ---
GLOBAL_CONFIG = {}
def load_global_config():
    global GLOBAL_CONFIG
    config_path = Path(__file__).parent / "workers" / "config.json"
    print(f"[Vespera] Reading configuration from: {config_path}")
    if not config_path.exists():
        print(f"[Vespera] ERROR: '{config_path}' not found.")
        GLOBAL_CONFIG = {"api_keys": {}}
        return
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            GLOBAL_CONFIG = json.load(f)
        print("[Vespera] Shared configuration loaded successfully.")
    except Exception as e:
        print(f"[ERROR] Loading config: {e}")
        GLOBAL_CONFIG = {"api_keys": {}}
    if 'shared_queue' not in GLOBAL_CONFIG:
        GLOBAL_CONFIG['shared_queue'] = None

# --- Worker Compatibility Fix ---
class WorkerBase:
    def __init__(self, config):
        self.config = config or {}
        self.global_config = config

# --- Security & Voice Classes ---
class SecurityAccessManager:
    def __init__(self):
        self.levels = {"Alpha": "Alpha-7-Delta", "Beta": "Beta-3-Gamma", "Gamma": "Gamma-1-Zulu", "Omega": "Omega-9-Epsilon"}
        self.active_level = "Gamma"
    def request_access(self, level, code):
        expected = self.levels.get(level)
        if expected and code == expected: self.active_level = level; return True
        return False
    def get_access_level(self):
        return self.active_level

class VoiceInterface:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 160)
        try:
            self.engine.setProperty('voice', self.engine.getProperty('voices')[0].id)
        except IndexError:
            print("[VoiceInterface] No TTS voices found.")
            self.engine = None
    def speak(self, text):
        if not self.engine: return
        print(f"[Vespera]: {text}")
        threading.Thread(target=self._speak_thread_target, args=(text,), daemon=True).start()
    def _speak_thread_target(self, text):
        try:
            if hasattr(self.engine, '_inLoop') and self.engine._inLoop: self.engine.endLoop()
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"[VoiceInterface] Error during speech: {e}")
    def listen(self, on_listening_start, on_listening_stop):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            on_listening_start()
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            except sr.WaitTimeoutError:
                return None
            finally:
                on_listening_stop()
        try:
            return self.recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            self.speak("I didn’t quite catch that, darling.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}"); return None

# --- Worker & Command Management Classes ---
class WorkerRegistry:
    def __init__(self):
        self.workers = {}
    def discover_workers(self, path: str = "workers"):
        worker_path = Path(path)
        if not worker_path.is_dir():
            print(f"[WorkerRegistry] Worker directory '{path}' not found.")
            return
        for file in worker_path.glob("*_worker.py"):
            name = file.stem.replace('_worker', '')
            try:
                spec = importlib.util.spec_from_file_location(name, file)
                module = importlib.util.module_from_spec(spec)
                if not hasattr(module, 'WorkerBase'):
                     module.WorkerBase = WorkerBase
                spec.loader.exec_module(module)
                if hasattr(module, "create_worker"):
                    self.workers[name] = module.create_worker(GLOBAL_CONFIG) 
                    print(f"[WorkerRegistry] Discovered worker: '{name}'")
            except Exception as e:
                print(f"[WorkerRegistry] Failed to load worker '{name}': {e}")
    def get_worker(self, name):
        return self.workers.get(name)

# --- THIS IS THE NEW, SMARTER COMMAND ROUTER ---
class CommandRouter:
    def __init__(self, registry: WorkerRegistry, command_manager: 'CommandRegistryManager'):
        self.registry = registry
        self.command_manager = command_manager

    def route_command(self, command: str):
        # Clean up the voice command: make it lowercase and remove spaces and hyphens
        cleaned_command = command.lower().replace(" ", "").replace("-", "")
        
        # Look for a worker whose command name is CONTAINED within the cleaned voice command
        for worker_name in self.registry.workers:
            # Also clean the worker name for a reliable comparison
            cleaned_worker_name = worker_name.replace("_", "").replace("-", "")
            
            if cleaned_worker_name in cleaned_command:
                # We found a match! For example, "fleetbridge" is in "launchfleetbridge"
                worker = self.registry.get_worker(worker_name)
                print(f"[CommandRouter] Matched '{command}' to worker '{worker_name}'.")
                if hasattr(worker, "execute_task"):
                    args = command.lower().replace(worker_name, "").strip().split()
                    threading.Thread(target=worker.execute_task, args=(args, threading.Event()), daemon=True).start()
                    return f"Of course, darling. Launching {worker_name} for you now."
        
        # Fallback for simple, one-word commands from commands.json
        command_name = command.split(' ')[0].lower()
        if command_name in self.command_manager.commands:
            return f"Executing known command '{command_name}': {self.command_manager.commands[command_name]['description']}"

        return f"I'm sorry, darling, but I don't have a worker available to handle '{command}'."

# --- Main GUI Class (Now complete with all fixes) ---
class CommandBridgeGUI:
    def __init__(self, voice, security, router, registry, command_manager):
        self.voice = voice
        self.security = security
        self.router = router
        self.registry = registry
        self.command_manager = command_manager
        self.root = tk.Tk()
        self.root.title("Vespera CommandBridge")
        self.root.geometry("800x600")
        self.root.configure(bg="black")
        self.console = scrolledtext.ScrolledText(self.root, bg="black", fg="lime", insertbackground="lime", font=("Consolas", 12), wrap=tk.WORD, state="disabled")
        self.console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.entry = tk.Entry(self.root, bg="gray10", fg="white", insertbackground="white", font=("Consolas", 12))
        self.entry.pack(fill=tk.X, padx=5, pady=5)
        self.entry.bind("<Return>", self.handle_input)
        self.root.after(100, self.start_systems)

    def start_systems(self):
        self.log_to_console("Vespera online. Awaiting orders.", speaker="Vespera")
        self.voice.speak("Vespera online. Awaiting orders.")
        threading.Thread(target=self.listen_loop, daemon=True).start()

    def log_to_console(self, text, speaker="User"):
        self.console.config(state="normal")
        tag = speaker.lower()
        self.console.tag_config(tag, foreground=self.get_speaker_color(speaker))
        self.console.insert(tk.END, f"[{speaker}]> {text}\n", tag)
        self.console.config(state="disabled")
        self.console.see(tk.END)

    def get_speaker_color(self, speaker):
        if speaker == "Vespera": return "#FF00FF"
        if speaker == "System": return "#FFA500"
        return "#00FF00"

    def handle_input(self, event=None):
        text = self.entry.get().strip()
        if not text: return
        self.log_to_console(text, speaker="User")
        self.entry.delete(0, tk.END)
        self.process_command(text)

    def process_command(self, text):
        response = ""
        cleaned_text = text.lower()

        # --- THIS IS THE NEW "HELP" COMMAND LOGIC ---
        if cleaned_text in ["help", "list commands", "what can you do"]:
            available_workers = sorted(self.registry.workers.keys())
            if not available_workers:
                response = "I don't seem to have any specialist workers available right now, sweetie."
            else:
                response = "Of course, darling. My available commands are: " + ", ".join(available_workers)
        # --- END OF "HELP" LOGIC ---
        elif cleaned_text.startswith("enable "):
            level = text.split(" ")[1].capitalize()
            response = f"{level} clearance requested. Please state your authorization code, Commander."
        elif text in self.security.levels.values():
            for level, code in self.security.levels.items():
                if text == code and self.security.request_access(level, code):
                    response = f"Authorization confirmed. Access level {level} is now active."
                    break
            else:
                response = "Authorization code not recognized. Access denied."
        elif cleaned_text.startswith("add command "):
            parts = text.split(" ", 2)
            if len(parts) < 3 or not parts[2]:
                response = "The format is 'add command <name> <description>', darling."
            else:
                name, data = parts[1], parts[2]
                self.command_manager.add_command(name, {"description": data})
                response = f"Of course. New command '{name}' has been added."
        elif cleaned_text.startswith("remove command "):
            parts = text.split(" ", 2)
            if len(parts) < 3:
                response = "Please specify which command to remove, sweetie."
            else:
                name = parts[2]
                self.command_manager.remove_command(name)
                response = f"As you wish. Command '{name}' has been removed."
        else:
            response = self.router.route_command(text)
        
        self.log_to_console(response, speaker="Vespera")
        self.voice.speak(response)

    def listen_loop(self):
        while True:
            command = self.voice.listen(
                on_listening_start=lambda: self.root.title("Vespera CommandBridge (Listening...)"),
                on_listening_stop=lambda: self.root.title("Vespera CommandBridge")
            )
            if command:
                self.log_to_console(command, speaker="User (Voice)")
                self.process_command(command)

    def run(self):
        self.root.mainloop()

# --- Main Entry Point ---
def main():
    load_global_config()
    voice = VoiceInterface()
    security = SecurityAccessManager()
    registry = WorkerRegistry()
    registry.discover_workers()
    command_manager = CommandRegistryManager()
    router = CommandRouter(registry, command_manager)
    gui = CommandBridgeGUI(voice, security, router, registry, command_manager)
    gui.run()

if __name__ == "__main__":
    main()
