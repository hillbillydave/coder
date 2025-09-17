# workers/codemuse_worker.py
import os, subprocess, datetime, re
from pathlib import Path
from typing import List, Dict, Any, Optional

class CodeMemory:
    def __init__(self, shared_memory_dict: Dict[str, str]):
        self.snippets = shared_memory_dict
    def store_snippet(self, key: str, code: str):
        self.snippets[key] = code
    def recall_snippet(self, key: str) -> str:
        return self.snippets.get(key, f"// No snippet found: {key}")

class ToolchainCore:
    def compile_cpp(self, filename: str) -> str:
        output_filename = filename.replace(".cpp", "")
        cmd = ["g++", filename, "-o", output_filename]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout or f"Success. Output: '{output_filename}'"
        except FileNotFoundError: return "Error: 'g++' not found. Please install it."
        except subprocess.CalledProcessError as e: return f"Failed:\n{e.stdout}{e.stderr}"

class MissionLog:
    def __init__(self): self.entries: List[str] = []
    def log(self, message: str):
        entry = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
        self.entries.append(entry); print(f"[CodeMuse Log] {message}")

class CodeMuse:
    def __init__(self, llm_client: Optional[Any], shared_memory_dict: Dict[str, str]):
        self.memory = CodeMemory(shared_memory_dict)
        self.toolchain = ToolchainCore(); self.log = MissionLog()
        self.llm_client = llm_client; self.log.log("Worker instance connected to persistent memory.")
    def generate_from_prompt(self, key: str, prompt: str) -> str:
        if not self.llm_client: return "LLM client not available."
        self.log.log(f"Prompt for '{key}': '{prompt}'")
        system_prompt = "You are an expert C++ programmer. Write clean C++ code. Output ONLY the code, in a single ```cpp ... ``` block."
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        response = self.llm_client.chat(messages)
        code_match = re.search(r'```cpp\n(.*?)```', response, re.DOTALL)
        if code_match:
            cleaned_code = code_match.group(1).strip()
            self.memory.store_snippet(key, cleaned_code)
            self.log.log(f"Code generated from prompt for key '{key}'."); return cleaned_code
        else: return f"Vespera's response was unclear:\n---\n{response}"
    def edit_from_prompt(self, source_key: str, instruction: str) -> str:
        if not self.llm_client: return "LLM client not available."
        source_code = self.memory.recall_snippet(source_key)
        if "No snippet found" in source_code: return f"Cannot edit. No code found for key '{source_key}'."
        self.log.log(f"Editing code from key '{source_key}' with instruction: '{instruction}'")
        system_prompt = "You are an expert C++ code editor. Modify the user's C++ code based on their instructions. Output ONLY the complete, modified C++ code in a single ```cpp ... ``` block."
        user_prompt = f"Modify this C++ code:\n```cpp\n{source_code}\n```\n\nInstruction: \"{instruction}\"\n\Provide the full and complete modified code."
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        response = self.llm_client.chat(messages)
        code_match = re.search(r'```cpp\n(.*?)```', response, re.DOTALL)
        if code_match:
            edited_code = code_match.group(1).strip()
            self.log.log(f"Successfully edited code from key '{source_key}'."); return edited_code
        else: return f"Vespera's response was unclear:\n---\n{response}"
    def load_from_file(self, key: str, file_path_str: str) -> str:
        fp = Path(file_path_str)
        if not fp.exists(): return f"Error: File not found at '{fp}'"
        try:
            content = fp.read_text(encoding='utf-8')
            self.memory.store_snippet(key, content); msg = f"Loaded code from '{fp}' into key '{key}'."
            self.log.log(msg); return msg
        except Exception as e: return f"Error reading file '{fp}': {e}"
    def save_to_file(self, key: str, file_path_str: str) -> str:
        code_to_save = self.memory.recall_snippet(key)
        if "No snippet found" in code_to_save: return f"Cannot save. No code found for key '{key}'."
        try:
            fp = Path(file_path_str)
            fp.write_text(code_to_save, encoding='utf-8')
            msg = f"Successfully saved code from key '{key}' to file '{fp}'."
            self.log.log(msg); return msg
        except Exception as e: return f"Error writing file to '{file_path_str}': {e}"
    def compile_from_key(self, key: str) -> str:
        code = self.memory.recall_snippet(key)
        if "No snippet found" in code: return f"Cannot compile. {code}"
        filename = f"{key}.cpp"
        with open(filename, "w", encoding='utf-8') as f: f.write(code)
        self.log.log(f"Compiling '{filename}'..."); return self.toolchain.compile_cpp(filename)

class CodeMuseExecutor:
    def __init__(self, config: Dict[str, Any], llm_client: Optional[Any], persistent_memory: Dict[str, str]):
        self.muse = CodeMuse(llm_client=llm_client, shared_memory_dict=persistent_memory)
        print("[CEO] CodeMuse worker is ready and connected to persistent memory.")
    def execute_task(self, args: List[str], stop_event: Any):
        if not args: print(self.get_help()); return
        cmd = args[0].lower()
        try:
            if cmd == "prompt" and len(args) > 2:
                key, prompt = args[1], ' '.join(args[2:])
                print(f"[CodeMuse] Asking Vespera to write code for '{key}'...")
                code = self.muse.generate_from_prompt(key, prompt)
                print(f"\n--- AI Generated Code (stored in key '{key}') ---\n{code}\n")
            elif cmd == "edit" and len(args) > 3:
                source_key, new_key, instruction = args[1], args[2], ' '.join(args[3:])
                print(f"[CodeMuse] Asking Vespera to edit code from '{source_key}'...")
                edited_code = self.muse.edit_from_prompt(source_key, instruction)
                self.muse.memory.store_snippet(new_key, edited_code)
                print(f"\n--- AI Edited Code (stored in key '{new_key}') ---\n{edited_code}\n")
            elif cmd == "load" and len(args) > 2:
                key, path = args[1], args[2]; result = self.muse.load_from_file(key, path); print(f"[CodeMuse] {result}")
            elif cmd == "save" and len(args) > 2:
                key, path = args[1], args[2]; result = self.muse.save_to_file(key, path); print(f"[CodeMuse] {result}")
            elif cmd == "compile" and len(args) > 1:
                key = args[1]; print(f"[CodeMuse] Compiling code from key '{key}'..."); result = self.muse.compile_from_key(key); print(f"[CodeMuse] {result}")
            elif cmd == "show" and len(args) > 1:
                key = args[1]; code = self.muse.memory.recall_snippet(key); print(f"\n--- Code in Memory ('{key}') ---\n{code}\n")
            else:
                print(self.get_help())
        except Exception as e: print(f"[CodeMuse ERROR] An unexpected error occurred: {e}")
    def get_help(self) -> str:
        return """
[CodeMuse] Ready for assignments. My memory is persistent.
Usage: codemuse <command> <args>

  --- CREATING CODE ---
  prompt <key> <desc>        - Asks Vespera to write a new C++ script.

  --- EDITING & REPAIRING CODE ---
  load <key> <path>          - Loads an existing script into memory.
  edit <src> <new> <instr>   - Edits code from <src> using an <instr>uction,
                             saves result in <new> key.
  show <key>                 - Displays the code currently in memory for a key.
  save <key> <path>          - Saves code from memory back to a file.
  
  --- TESTING CODE ---
  compile <key>              - Compiles the C++ snippet for a key."""

def create_worker(config: Dict[str, Any], llm_client: Optional[Any], persistent_memory: Dict[str, str]) -> CodeMuseExecutor:
    return CodeMuseExecutor(config, llm_client, persistent_memory)
