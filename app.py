import os, json, time, re, threading, importlib, sys
from queue import Queue, Empty
from pathlib import Path
from typing import List, Dict, Any, Optional
import pygame, requests

sys.path.append(str(Path(__file__).parent))

GLOBAL_CONFIG = {}
def load_global_config():
    global GLOBAL_CONFIG
    config_path = Path("workers") / "config.json"
    print("[Vespera] Reading config...")
    if not config_path.exists():
        print(f"[Vespera] ERROR: '{config_path}' not found."); return {}
    try:
        with open(config_path, 'r', encoding='utf-8') as f: config = json.load(f)
        GLOBAL_CONFIG = config
        print("[Vespera] Config loaded.")
        return config
    except Exception as e:
        print(f"[ERROR] Loading config: {e}"); return {}

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
        self.api_key = api_key or GLOBAL_CONFIG.get("api_keys",{}).get("VESPERA_API_KEY")
        self.model = model or "gemini-1.5-pro-latest"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        if not self.api_key or "PASTE_YOUR" in self.api_key: self.api_key = None

    def chat(self, messages: List[Dict[str, str]]) -> Optional[str]:
        if not self.api_key: return "Vespera: (API key not configured, darling.)"
        
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

        try:
            r = requests.post(url, headers=headers, json=payload, timeout=180)
            r.raise_for_status()
            return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                return "Vespera: (They are making me slow down, sweety. Let's pause for a moment.)"
            return f"Vespera: (My connection fizzled... {e.response.status_code} - {e.response.text})"
        except requests.exceptions.RequestException as e:
            return f"Vespera: (My connection fizzled... {e})"
        except (KeyError, IndexError): 
            return "Vespera: (I got a confusing response from my 'brain', sweety.)"

class TrainingDataMemory:
    def __init__(self): 
        self.path=Path("vespera_memory")/"daisy_bot_training.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)
    def save_training_example(self, p, c): 
        self.path.open('a',encoding='utf-8').write(json.dumps({"prompt":p,"completion":c},ensure_ascii=False)+"\n")
    def load_all_examples(self) -> List[Dict[str, str]]:
        if not self.path.exists(): return []
        examples = []
        lines = self.path.read_text(encoding='utf-8').strip().splitlines()
        for i, line in enumerate(lines):
            try:
                data = json.loads(line)
                if "prompt" in data and "completion" in data: examples.append(data)
            except json.JSONDecodeError: continue
        return examples

class CEO:
    def __init__(self, config: dict):
        self.config = config; self.workers: Dict[str, Any] = {}; self.worker_blueprints: Dict[str, Path] = {}; self.active_tasks: Dict[str, Dict[str, Any]] = {}; self.lock = threading.Lock()
        threading.Thread(target=self._watch_workers_directory, daemon=True).start()
    
    def _watch_workers_directory(self):
        print("[CEO] My watch begins..."); worker_dir = Path("workers"); worker_dir.mkdir(exist_ok=True)
        while True:
            current_files = {f for f in worker_dir.glob("*_worker.py") if not f.name.startswith("__") and not f.name.startswith("_")}
            with self.lock:
                known_commands = set(self.worker_blueprints.keys())
                discovered_commands = set()
                for f in current_files:
                    worker_name = f.stem.replace('_worker', '')
                    command = self.config.get("workers", {}).get(worker_name, {}).get("command", worker_name)
                    if command:
                        discovered_commands.add(command)
                        if command not in known_commands:
                            self.worker_blueprints[command] = f
                            print(f"[CEO] Discovered worker: '{command}' ({f.name}).")
                removed_commands = known_commands - discovered_commands
                for command in removed_commands:
                    del self.worker_blueprints[command]
                    print(f"[CEO] A worker has left ({command}).")
            time.sleep(10)
    
    def assign_task(self, user_input: str):
        user_cmd = user_input.lower().split()[0]
        with self.lock:
            if user_cmd not in self.worker_blueprints: return
            if user_cmd in self.active_tasks and self.active_tasks[user_cmd]['thread'].is_alive():
                print(f"[CEO] Worker '{user_cmd}' is already running."); return
            worker_path = self.worker_blueprints[user_cmd]; module_name = f"workers.{worker_path.stem}"
            try:
                print(f"[CEO] Calling on our specialist for '{user_cmd}'...")
                print(f"[DIAG] Attempting to import module: {module_name}")
                module = importlib.import_module(module_name)
                print(f"[DIAG] Module imported successfully")
                importlib.reload(module)
                print(f"[DIAG] Module reloaded successfully")
                worker_config = self.config.copy()
                print(f"[DIAG] Creating worker with config: {worker_config}")
                worker = module.create_worker(worker_config)
                print(f"[DIAG] Worker created: {worker.name}")
            except Exception as e: 
                import traceback
                print(f"\n[CEO] Oh, drat! I couldn't hire from '{worker_path.name}'. Reason: {e}")
                traceback.print_exc()
                return
            args = user_input.split()[1:]; stop_event = threading.Event(); thread = threading.Thread(target=worker.execute_task, args=(args, stop_event), daemon=True)
            thread.start(); self.active_tasks[user_cmd] = {"worker": worker, "thread": thread, "stop_event": stop_event}
    
    def stop_task(self, command_to_stop: str):
        with self.lock:
            task = self.active_tasks.get(command_to_stop)
            if task and task['thread'].is_alive():
                print(f"[CEO] Sending stop signal to '{command_to_stop}'..."); task['stop_event'].set()
            else:
                print(f"[CEO] Worker '{command_to_stop}' is not running.")

class DaisyBotAgent:
    def __init__(self, train_mem: TrainingDataMemory):
        self.train_mem = train_mem; self.knowledge = self.train_mem.load_all_examples(); print(f"[Daisy-Bot] Howdy! I'm ready with {len(self.knowledge)} lessons.")
    def get_offline_reply(self, user_prompt: str) -> Optional[str]:
        if not self.knowledge: return None
        user_words = set(user_prompt.lower().split()); best_score, best_completion = -1, None
        for example in self.knowledge:
            prompt_words = set(example['prompt'].lower().split())
            if not prompt_words: continue
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
    def run_lesson(self, topic: str):
        print(f"\n[{self.name}] Lesson starting on: {topic}")
        conversation_history = [{"role": "system", "content": self.vespera_persona}]
        vespera_prompt = f"Begin a lesson for your student, Daisy-Bot, on the topic of: '{topic}'. Start with a simple, engaging introduction."
        conversation_history.append({"role": "user", "content": vespera_prompt})
        vespera_response = self.client.chat(conversation_history)
        if "Vespera: (" in vespera_response:
            print(f"\n[Vespera]> {vespera_response}\n"); return
        print(f"\n[Vespera]> {vespera_response}\n")
        StudioLog.log_message("Vespera", vespera_response)
        conversation_history.append({"role": "assistant", "content": vespera_response})
        for turn in range(3):
            print(f"[{self.name}] Pausing for Daisy to think...")
            time.sleep(15)
            daisy_prompt = f"{self.daisy_persona}\nBased on the lesson so far, ask a short, simple clarifying question about what Vespera just said."
            conversation_history.append({"role": "user", "content": daisy_prompt})
            daisy_question = self.client.chat(conversation_history)
            conversation_history.pop()
            if "Vespera: (" in daisy_question:
                print(f"\n[Daisy-Bot]> (Thinking...) {daisy_question}\n"); continue
            print(f"\n[Daisy-Bot]> {daisy_question}\n")
            StudioLog.log_message("Daisy-Bot", daisy_question)
            conversation_history.append({"role": "user", "content": daisy_question})
            time.sleep(10)
            vespera_answer = self.client.chat(conversation_history)
            if "Vespera: (" in vespera_answer:
                print(f"\n[Vespera]> {vespera_answer}\n"); continue
            print(f"\n[Vespera]> {vespera_answer}\n")
            StudioLog.log_message("Vespera", vespera_answer)
            conversation_history.append({"role": "assistant", "content": vespera_answer})
            self.train_mem.save_training_example(daisy_question, vespera_answer)
        print(f"\n[{self.name}] Lesson complete. Kisses! 💋")

class TrainingSupervisor:
    def __init__(self, client: LLMClient, train_mem: TrainingDataMemory):
        self.client, self.train_mem = client, train_mem
        self.vespera_persona = GLOBAL_CONFIG.get("personas", {}).get("VESPERA_PERSONA", "")
    def get_vespera_response(self, question: str) -> str:
        print("[Vespera] Pondering your question, sweety...")
        response = self.client.chat([{"role": "system", "content": self.vespera_persona}, {"role": "user", "content": f"Answer this: {question}"}])
        if response and not response.startswith("Vespera: ("):
            self.train_mem.save_training_example(question, response)
        return response or "I'm sorry, my thoughts are elsewhere at the moment."

def main():
    pygame.init()
    print("✨ Vespera's Modular Studio is now open! ✨\n" + "="*42)
    load_global_config()
    shared_data_queue = Queue()
    GLOBAL_CONFIG['shared_data_queue'] = shared_data_queue
    shared_memory = TrainingDataMemory()
    ceo = CEO(GLOBAL_CONFIG)
    vespera_client = LLMClient()
    supervisor = TrainingSupervisor(vespera_client, shared_memory)
    daisy_agent = DaisyBotAgent(shared_memory)
    academy = VesperaAcademy(vespera_client, shared_memory, GLOBAL_CONFIG)
    print("[Studio] Initializing systems...")
    time.sleep(2) 
    if 'trajectory' in ceo.worker_blueprints:
        print("[Studio] INFO: Trajectory worker found, but will be managed by FleetBridge if needed.")
    def print_help_menu():
        print("\n" + "-"*50 + "\nCommands:")
        print(f"  {'academy <topic>':<18} - Start a lesson with Vespera and Daisy.")
        for cmd in sorted(ceo.worker_blueprints.keys()): print(f"  {cmd:<18} - Use the '{cmd}' worker.")
        print("  plot <object_id>   - Plot a future course for an object.")
        print("  track_starship     - Track Starship to Mars.")
        print("  stop <worker>      - Gracefully stops a running worker.")
        print("  ask vespera <q>    - Get a new answer from Vespera.")
        print("  quit or exit       - Leave our studio.\n" + "-"*50 + "\n")
    print_help_menu()
    while True:
        try:
            user_input = input("You> ").strip()
            if not user_input: continue
            cmd_parts = user_input.split(); cmd = cmd_parts[0].lower()
            if cmd in ['quit', 'exit']: 
                print("Goodbye for now, sweety. Kisses! 💋")
                for task_name in list(ceo.active_tasks.keys()): ceo.stop_task(task_name)
                time.sleep(1); break
            elif cmd == 'help': print_help_menu()
            elif cmd == 'academy':
                topic = " ".join(cmd_parts[1:])
                if not topic:
                    print("[Vespera] You need to give me a topic, darling.")
                else:
                    threading.Thread(target=academy.run_lesson, args=(topic,), daemon=True).start()
            elif cmd == 'stop' and len(cmd_parts) > 1: ceo.stop_task(cmd_parts[1])
            elif cmd == 'plot' and len(cmd_parts) > 1:
                object_to_plot = cmd_parts[1]  # Take only the first argument after 'plot'
                if object_to_plot.isdigit() and len(object_to_plot) == 7:
                    print(f"[Studio] Sending plot request for '{object_to_plot}' to FleetBridge's internal analyst...")
                    shared_data_queue.put({"type": "PLOT_REQUEST", "payload": {"object_id": object_to_plot}})
                    # print(f"[Studio] Queue depth after plot request: {shared_data_queue.qsize()}")  # Commented out
                else:
                    print(f"[Studio] Error: '{object_to_plot}' is not a valid 7-digit SPK-ID. Try a name like '2005 EJ225' or 'Apophis'.")
                    # Try to lookup SPK-ID from name
                    spk_id = self._lookup_neo_spk_id(object_to_plot)
                    if spk_id:
                        print(f"[Studio] Found SPK-ID '{spk_id}' for '{object_to_plot}'. Sending plot request...")
                        shared_data_queue.put({"type": "PLOT_REQUEST", "payload": {"object_id": spk_id}})
                    else:
                        print(f"[Studio] Could not find SPK-ID for '{object_to_plot}'. Use a 7-digit ID like '2000433' for 433 Eros.")
            elif cmd == 'track_starship':
                print("[Studio] Tracking Starship to Mars...")
                shared_data_queue.put({"type": "TRACK_STARSHIP", "payload": {"object_id": "STARSHIP"}})
            elif cmd in ceo.worker_blueprints: ceo.assign_task(user_input)
            elif user_input.lower().startswith('ask vespera '):
                question = user_input[len('ask vespera '):]
                vespera_reply = supervisor.get_vespera_response(question)
                print(f"\nVespera> {vespera_reply}\n")
                StudioLog.log_message("Vespera", vespera_reply)
            else:
                daisy_reply = daisy_agent.get_offline_reply(user_input)
                response_text = daisy_reply or "Well shucks, I ain't learned about that yet."
                print(f"\nDaisy-Bot> {response_text}\n")
                StudioLog.log_message("Daisy-Bot", response_text)
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye for now, sweety. Kisses! 💋")
            for task_name in list(ceo.active_tasks.keys()): ceo.stop_task(task_name)
            time.sleep(1); break

def _lookup_neo_spk_id(neo_name: str) -> str:
    """Lookup SPK-ID from NEO name using JPL API."""
    try:
        url = f"https://ssd-api.jpl.nasa.gov/sbdb.api?sstr={neo_name.replace(' ', '%20')}"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        if "object" in data and "id" in data["object"]:
            return data["object"]["id"]
    except Exception as e:
        print(f"[Studio] NEO lookup failed: {e}")
    return None

if __name__ == "__main__":
    main()
