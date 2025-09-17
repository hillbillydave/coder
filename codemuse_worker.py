# workers/codemuse_worker.py
import os, subprocess, datetime, re
from pathlib import Path
from typing import List, Dict, Any, Optional

class CodeMemory:
    def __init__(self): self.snippets: Dict[str, str] = {}
    def store_snippet(self, key: str, code: str): self.snippets[key] = code
    def recall_snippet(self, key: str) -> str: return self.snippets.get(key, f"// No snippet found: {key}")

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
        self.entries.append(entry); print(f"[CodeMuse] {message}")
    def get_logs(self) -> str: return "\n".join(self.entries)

class CodeMuse:
    def __init__(self, llm_client: Optional[Any] = None):
        self.memory = CodeMemory(); self.toolchain = ToolchainCore(); self.log = MissionLog()
        self.llm_client = llm_client; self.log.log("Worker initialized.")
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
    def load_from_file(self, key: str, file_path_str: str) -> str:
        fp = Path(file_path_str)
        if not fp.exists(): return f"Error: File not found at '{fp}'"
        try:
            content = fp.read_text(encoding='utf-8')
            self.memory.store_snippet(key, content); msg = f"Loaded code from '{fp}' into key '{key}'."
            self.log.log(msg); return msg
        except Exception as e: return f"Error reading file '{fp}': {e}"
    def compile_from_key(self, key: str) -> str:
        code = self.memory.recall_snippet(key)
        if "No snippet found" in code: return f"Cannot compile. {code}"
        filename = f"{key}.cpp"
        with open(filename, "w", encoding='utf-8') as f: f.write(code)
        self.log.log(f"Compiling '{filename}'..."); return self.toolchain.compile_cpp(filename)

class CodeMuseExecutor:
    def __init__(self, config: Dict[str, Any], llm_client: Optional[Any] = None):
        self.muse = CodeMuse(llm_client=llm_client)
        print("[CEO] CodeMuse worker is ready for advanced assignments.")
    def execute_task(self, args: List[str], stop_event: Any):
        if not args: print(self.get_help()); return
        cmd = args[0].lower()
        if cmd == "prompt" and len(args) > 2: print(f"\n--- AI Code: {args[1]} ---\n{self.muse.generate_from_prompt(args[1], ' '.join(args[2:]))}\n")
        elif cmd == "load" and len(args) > 2: print(f"\n--- Load File ---\n{self.muse.load_from_file(args[1], args[2])}\n")
        elif cmd == "compile" and len(args) > 1: print(f"\n--- Compiler: {args[1]} ---\n{self.muse.compile_from_key(args[1])}\n")
        else: print(self.get_help())
    def get_help(self) -> str: return """
[CodeMuse] Ready for advanced assignments, darling.
Usage: codemuse <command> <args>
  prompt <key> <desc>    - Asks Vespera to write a full C++ script.
  load <key> <path>      - Loads a script into memory.
  compile <key>          - Compiles the C++ snippet for a key."""

def create_worker(config: Dict[str, Any], llm_client: Optional[Any] = None) -> CodeMuseExecutor:
    return CodeMuseExecutor(config, llm_client)
