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

# --- Security Access Manager ---
class SecurityAccessManager:
    def __init__(self):
        self.levels = {
            "Alpha": "Alpha-7-Delta",
            "Beta": "Beta-3-Gamma",
            "Gamma": "Gamma-1-Zulu",
            "Omega": "Omega-9-Epsilon"
        }
        self.active_level = "Gamma" # Start at a default, safe level

    def request_access(self, level, code):
        expected = self.levels.get(level)
        if expected and code == expected:
            self.active_level = level
            return True
        return False

    def get_access_level(self):
        return self.active_level

# --- Voice Interface ---
class VoiceInterface:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 160)
        # Add a safety check for available voices
        try:
            self.engine.setProperty('voice', self.engine.getProperty('voices')[0].id)
        except IndexError:
            print("[VoiceInterface] No TTS voices found. Voice output will be disabled.")

    def speak(self, text):
        print(f"[Vespera]: {text}")
        try:
            # Prevent crashes if the engine is busy
            if self.engine._inLoop: self.engine.endLoop()
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"[VoiceInterface] Error during speech: {e}")

    def listen(self, on_listening_start, on_listening_stop):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            on_listening_start() # Callback to update the GUI
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            except sr.WaitTimeoutError:
                return None # No speech detected
            finally:
                on_listening_stop() # Callback to update the GUI

        try:
            return self.recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            self.speak("I didn’t quite catch that, darling.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return None

# --- Worker Registry ---
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
                spec.loader.exec_module(module)
                if hasattr(module, "create_worker"):
                    # Pass a dummy config for now, a real app would pass the global config
                    self.workers[name] = module.create_worker({}) 
                    print(f"[WorkerRegistry] Discovered worker: '{name}'")
            except Exception as e:
                print(f"[WorkerRegistry] Failed to load worker '{name}': {e}")

    def get_worker(self, name):
        return self.workers.get(name)

# --- Command Router ---
class CommandRouter:
    def __init__(self, registry: WorkerRegistry, command_manager: 'CommandRegistryManager'):
        self.registry = registry
        self.command_manager = command_manager

    def route_command(self, command: str):
        command_name = command.split(' ')[0].lower()
        
        # Priority 1: Check for a registered worker
        if command_name in self.registry.workers:
            worker = self.registry.get_worker(command_name)
            if hasattr(worker, "execute_task"):
                # We should run this in a thread to not block the GUI
                args = command.split(' ')[1:]
                threading.Thread(target=worker.execute_task, args=(args, threading.Event()), daemon=True).start()
                return f"Acknowledged. Assigning task '{command_name}' to the specialist."
        
        # Priority 2: Check for a JSON-defined command
        if command_name in self.command_manager.commands:
            return f"Executing known command '{command_name}': {self.command_manager.commands[command_name]['description']}"

        return f"I'm sorry, darling, but I don't have a worker available to handle '{command}'."

# --- Command Registry Manager ---
class CommandRegistryManager:
    def __init__(self, path="commands.json"):
        self.path = Path(path)
        self.commands = self.load()

    def load(self):
        if self.path.exists():
            with open(self.path) as f:
                return json.load(f)
        return {}

    def add_command(self, name, data):
        self.commands[name] = data
        self.save()

    def remove_command(self, name):
        if name in self.commands:
            del self.commands[name]
            self.save()

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.commands, f, indent=2)

# --- Vespera CommandBridge GUI ---
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

        # Fix for race condition: Start voice and loop *after* the main window is ready
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
        if speaker == "Vespera": return "#FF00FF" # Magenta
        if speaker == "System": return "#FFA500" # Orange
        return "#00FF00" # Lime Green

    def handle_input(self, event=None):
        text = self.entry.get().strip()
        if not text: return
        
        self.log_to_console(text, speaker="User")
        self.entry.delete(0, tk.END)
        self.process_command(text)

    def process_command(self, text):
        if text.lower().startswith("enable "):
            level = text.split(" ")[1].capitalize()
            response = f"{level} clearance requested. Please state your authorization code, Commander."
            self.log_to_console(response, speaker="Vespera")
            self.voice.speak(response)
        elif text in self.security.levels.values():
            for level, code in self.security.levels.items():
                if text == code and self.security.request_access(level, code):
                    response = f"Authorization confirmed. Access level {level} is now active. Welcome back."
                    self.log_to_console(response, speaker="Vespera")
                    self.voice.speak(response)
                    return
            response = "Authorization code not recognized. Access denied."
            self.log_to_console(response, speaker="Vespera")
            self.voice.speak(response)
        elif text.lower().startswith("add command "):
            parts = text.split(" ", 2)
            if len(parts) < 3 or not parts[2]:
                response = "I'm sorry, darling, but the format is 'add command <name> <description>'."
            else:
                name, data = parts[1], parts[2]
                self.command_manager.add_command(name, {"description": data})
                response = f"Of course. New command '{name}' has been added to my registry."
            self.log_to_console(response, speaker="Vespera")
            self.voice.speak(response)
        elif text.lower().startswith("remove command "):
            parts = text.split(" ", 2)
            if len(parts) < 3:
                response = "Please specify which command to remove, sweetie."
            else:
                name = parts[2]
                self.command_manager.remove_command(name)
                response = f"As you wish. Command '{name}' has been removed."
            self.log_to_console(response, speaker="Vespera")
            self.voice.speak(response)
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
    voice = VoiceInterface()
    security = SecurityAccessManager()
    registry = WorkerRegistry()
    registry.discover_workers() # Looks in the 'workers' subdirectory
    command_manager = CommandRegistryManager()
    router = CommandRouter(registry, command_manager)
    gui = CommandBridgeGUI(voice, security, router, registry, command_manager)
    gui.run()

if __name__ == "__main__":
    main()
