# app.py
import os
import json
import time
import threading
import importlib
import sys
from queue import Queue, Empty
from pathlib import Path
from typing import List, Dict, Any, Optional
import pygame
import requests
try:
    import backoff
except ImportError:
    print("[ERROR] 'backoff' module not found. Install it with 'pip install backoff'.")
    backoff = None

sys.path.append(str(Path(__file__).parent))

GLOBAL_CONFIG = {}

def send_update_to_fleetbridge(data):
    """Send data to fleetbridge via shared queue."""
    queue = GLOBAL_CONFIG.get('shared_data_queue')
    if queue:
        queue.put({"type": "SEPFORECAST_UPDATE", "payload": data})
    else:
        print(f"[Studio] No shared queue for FleetBridge update: {data}")

def load_global_config():
    global GLOBAL_CONFIG
    config_path = Path("workers") / "config.json"
    print("[Vespera] Reading config...")
    if not config_path.exists():
        print(f"[Vespera] ERROR: '{config_path}' not found.")
        return {}
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        GLOBAL_CONFIG = config
        print("[Vespera] Config loaded.")
        return config
    except Exception as e:
        print(f"[ERROR] Loading config: {e}")
        return {}

def validate_api_key(api_key: str) -> bool:
    """Validate Gemini API key."""
    if not api_key or "PASTE_YOUR" in api_key:
        return False
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
        r = requests.post(url, json={"contents": [{"role": "user", "parts": [{"text": "test"}]}]}, timeout=10)
        return r.status_code in [200, 403]
    except requests.exceptions.RequestException:
        return False

class StudioLog:
    log_path = Path("workers") / "_studio_log.jsonl"
    @staticmethod
    def log_message(speaker: str, message: str):
        log_entry = {"timestamp": time.time(), "source": "Studio", "speaker": speaker, "message": message}
        try:
            if not hasattr(StudioLog, 'has_written'):
                StudioLog.log_path.unlink(missing_ok=True)
                StudioLog.has_written = True
            with open(StudioLog.log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"[StudioLog] ERROR writing to log: {e}")

class LLMClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or GLOBAL_CONFIG.get("api_keys", {}).get("VESPERA_API_KEY")
        self.model = model or "gemini-1.5-pro-latest"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        if not self.api_key or not validate_api_key(self.api_key):
            print("[LLMClient] WARNING: Invalid or missing VESPERA_API_KEY. Please update workers/config.json with a valid Gemini API key from https://makersuite.google.com/app/apikey.")
            self.api_key = None

    def chat(self, messages: List[Dict[str, str]]) -> Optional[str]:
        if not self.api_key:
            return f"Vespera: (Mock response for '{messages[-1]['content']}': Please configure a valid API key in workers/config.json.)"
        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        system_instruction = None
        contents = []
        for msg in messages:
            if msg['role'] == 'system':
                system_instruction = msg['content']
            else:
                role = 'model' if msg['role'] == 'assistant' else 'user'
                if 'parts' in msg:
                    contents.append({"role": role, "parts": msg['parts']})
                else:
                    contents.append({"role": role, "parts": [{"text": msg['content']}]})
        payload = {"contents": contents, "generationConfig": {"temperature": 0.5, "maxOutputTokens": 8192}}
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        if backoff:
            @backoff.on_exception(backoff.expo, requests.exceptions.HTTPError, max_tries=5, giveup=lambda e: e.response.status_code != 429)
            def make_request():
                r = requests.post(url, headers=headers, json=payload, timeout=180)
                r.raise_for_status()
                return r
        else:
            def make_request():
                r = requests.post(url, headers=headers, json=payload, timeout=180)
                r.raise_for_status()
                return r
        try:
            r = make_request()
            response = r.json()
            if not response.get("candidates") or not response["candidates"][0].get("content", {}).get("parts"):
                print("[LLMClient] ERROR: Empty or malformed response.")
                return f"Vespera: (No valid response for '{messages[-1]['content']}')"
            return response["candidates"][0]["content"]["parts"][0]["text"].strip()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("[LLMClient] Rate limit hit, no retries without backoff module.")
                return f"Vespera: (Rate limit exceeded for '{messages[-1]['content']}')"
            elif e.response.status_code == 401:
                print("[LLMClient] ERROR: Invalid API key. Please update VESPERA_API_KEY in workers/config.json.")
                return f"Vespera: (Invalid API key for '{messages[-1]['content']}')"
            return f"Vespera: (Connection error: {e.response.status_code} - {e.response.text})"
        except requests.exceptions.RequestException as e:
            return f"Vespera: (Network error: {e})"
        except (KeyError, IndexError):
            return f"Vespera: (Confusing response from API for '{messages[-1]['content']}')"

class TrainingDataMemory:
    def __init__(self):
        self.path = Path("vespera_memory") / "daisy_bot_training.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)
    def save_training_example(self, p, c):
        try:
            self.path.open('a', encoding='utf-8').write(json.dumps({"prompt": p, "completion": c}, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[TrainingDataMemory] ERROR saving example: {e}")
    def load_all_examples(self) -> List[Dict[str, str]]:
        if not self.path.exists():
            return []
        examples = []
        try:
            lines = self.path.read_text(encoding='utf-8').strip().splitlines()
            for line in lines:
                try:
                    data = json.loads(line)
                    if "prompt" in data and "completion" in data:
                        examples.append(data)
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            print(f"[ERROR] Could not read training memory: {e}")
            return []
        return examples

class CEO:
    def __init__(self, config: dict):
        self.config = config
        self.workers: Dict[str, Any] = {}
        self.worker_blueprints: Dict[str, Path] = {}
        self.worker_commands: Dict[str, List[str]] = {}
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
        threading.Thread(target=self._watch_workers_directory, daemon=True).start()

    def _get_worker_commands(self, worker_path: Path) -> List[str]:
        try:
            module_name = f"workers.{worker_path.stem}"
            module = importlib.import_module(module_name)
            importlib.reload(module)
            if hasattr(module, 'create_worker'):
                try:
                    worker = module.create_worker(self.config)
                except TypeError:
                    worker = module.create_worker()
                if hasattr(worker, 'supported_commands'):
                    return worker.supported_commands()
                elif worker_path.stem == 'fleetbridge':
                    return ['plot <object_id>']
                elif worker_path.stem == 'learn':
                    return ['<topic>']
                else:
                    return ['<args>']
            return ['<args>']
        except Exception as e:
            print(f"[CEO] Error inspecting {worker_path.name}: {e}")
            return ['<args>']

    def _watch_workers_directory(self):
        print("[CEO] My watch begins...")
        worker_dir = Path("workers")
        worker_dir.mkdir(exist_ok=True)
        while True:
            current_files = {f for f in worker_dir.glob("*_worker.py") if not f.name.startswith("__") and not f.name.startswith("_")}
            with self.lock:
                known_commands = set(self.worker_blueprints.keys())
                discovered_commands = set()
                print("\n[Studio] Discovered Workers:")
                for f in sorted(current_files):
                    worker_name = f.stem.replace('_worker', '')
                    command = self.config.get("workers", {}).get(worker_name, {}).get("command", worker_name)
                    if command:
                        discovered_commands.add(command)
                        if command not in known_commands:
                            self.worker_blueprints[command] = f
                            self.worker_commands[command] = self._get_worker_commands(f)
                            print(f"[CEO] Discovered worker: '{command}' ({f.name}).")
                removed_commands = known_commands - discovered_commands
                for command in removed_commands:
                    del self.worker_blueprints[command]
                    del self.worker_commands[command]
                    print(f"[CEO] A worker has left ({command}).")
            time.sleep(10)

    def announce_and_list_commands(self):
        print("\n[CEO] Starting WorkerOrchestrator...")
        with self.lock:
            for cmd in sorted(self.worker_blueprints.keys()):
                commands = self.worker_commands.get(cmd, ['<args>'])
                print(f"[CEO] Discovered worker: '{cmd}' ({cmd}_worker.py)")
                print(f"[CEO] Commands for '{cmd}': {', '.join(c for c in commands if c)}")
        print()

    def assign_task(self, user_input: str, llm_client: LLMClient = None):
        user_cmd = user_input.lower().split()[0]
        with self.lock:
            if user_cmd not in self.worker_blueprints:
                print(f"[CEO] No worker found for '{user_cmd}'.")
                return
            if user_cmd in self.active_tasks and self.active_tasks[user_cmd]['thread'].is_alive():
                print(f"[CEO] Worker '{user_cmd}' is already running.")
                return
            worker_path = self.worker_blueprints[user_cmd]
            module_name = f"workers.{worker_path.stem}"
            try:
                print(f"[CEO] Calling on our specialist for '{user_cmd}'...")
                module = importlib.import_module(module_name)
                importlib.reload(module)
                worker_config = self.config.copy()
                try:
                    worker = module.create_worker(worker_config)
                except TypeError:
                    worker = module.create_worker()
            except Exception as e:
                print(f"[CEO] Oh, drat! I couldn't hire from '{worker_path.name}'. Reason: {e}")
                return
            args = user_input.split()[1:]
            stop_event = threading.Event()
            if user_cmd == 'fleetbridge' and not args:
                worker.execute_task(args, stop_event)
                self.active_tasks[user_cmd] = {"worker": worker, "thread": threading.current_thread(), "stop_event": stop_event}
            else:
                thread = threading.Thread(target=worker.execute_task, args=(args, stop_event), daemon=True)
                thread.start()
                self.active_tasks[user_cmd] = {"worker": worker, "thread": thread, "stop_event": stop_event}

    def stop_task(self, command_to_stop: str):
        with self.lock:
            task = self.active_tasks.get(command_to_stop)
            if task:
                print(f"[CEO] Sending stop signal to '{command_to_stop}'...")
                task['stop_event'].set()
                if task['thread'] is not threading.current_thread():
                    task['thread'].join(timeout=1.0)
                del self.active_tasks[command_to_stop]
            else:
                print(f"[CEO] Worker '{command_to_stop}' is not running.")

class DaisyBotAgent:
    def __init__(self, train_mem: TrainingDataMemory):
        self.train_mem = train_mem
        self.knowledge = self.train_mem.load_all_examples()
        print(f"[Daisy-Bot] Howdy! I'm ready with {len(self.knowledge)} lessons.")
    def get_offline_reply(self, user_prompt: str) -> Optional[str]:
        if not self.knowledge:
            return None
        user_words = set(user_prompt.lower().split())
        best_score, best_completion = -1, None
        for example in self.knowledge:
            prompt_words = set(example['prompt'].lower().split())
            if not prompt_words:
                continue
            score = len(user_words.intersection(prompt_words)) / len(user_words.union(prompt_words))
            if score > best_score:
                best_score, best_completion = score, example['completion']
        if best_score > 0.35:
            return best_completion
        return None

class VesperaAcademy:
    def __init__(self, client: LLMClient, train_mem: TrainingDataMemory, config: dict):
        self.client = client
        self.train_mem = train_mem
        self.daisy_persona = config.get("personas", {}).get("DAISY_PERSONA", "")
        self.vespera_persona = config.get("personas", {}).get("VESPERA_PERSONA", "")
        self.name = "Vespera's Academy"

    def run_lesson(self, topic: str, stop_event: threading.Event):
        print(f"\n[{self.name}] Lesson starting on: {topic}")
        conversation_history = [{"role": "system", "content": self.vespera_persona}]
        vespera_prompt = f"Begin a lesson for your student, Daisy-Bot, on the topic of: '{topic}'. Start with a simple, engaging introduction."
        conversation_history.append({"role": "user", "content": vespera_prompt})
        vespera_response = self.client.chat(conversation_history)
        if stop_event.is_set():
            print(f"\n[{self.name}] Lesson stopped.")
            return
        if "Vespera: (" in vespera_response:
            print(f"\n[Vespera]> {vespera_response}\n")
            return
        print(f"\n[Vespera]> {vespera_response}\n")
        StudioLog.log_message("Vespera", vespera_response)
        conversation_history.append({"role": "assistant", "content": vespera_response})
        for turn in range(3):
            if stop_event.is_set():
                print(f"\n[{self.name}] Lesson stopped.")
                return
            print(f"[{self.name}] Pausing for Daisy to think...")
            time.sleep(15)
            daisy_prompt = f"{self.daisy_persona}\nBased on the lesson so far, ask a short, simple clarifying question about what Vespera just said."
            conversation_history.append({"role": "user", "content": daisy_prompt})
            daisy_question = self.client.chat(conversation_history)
            conversation_history.pop
