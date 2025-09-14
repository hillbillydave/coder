# workers/learn_worker.py
import threading, time
from pathlib import Path
try:
    from workers.worker_base import WorkerBase
    from app import LLMClient, TrainingDataMemory
except ImportError:
    WorkerBase = object; LLMClient = None; TrainingDataMemory = None

class LearnWorker(WorkerBase):
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "Knowledge Ingestor"
        self.client = LLMClient(api_key=self.config.get("api_keys", {}).get("VESPERA_API_KEY"))
        self.train_mem = TrainingDataMemory()
        self.vespera_persona = self.config.get("personas", {}).get("VESPERA_PERSONA", "")
        self.is_ready = True if self.client.api_key else False

    def execute_task(self, args: list, stop_event: threading.Event):
        if not self.is_ready:
            print(f"[{self.name}] I can't learn without my API key, sweetie.")
            return

        if not args:
            print(f"[{self.name}] You need to tell me what file to learn from, darling.")
            return
        
        file_path = Path(" ".join(args))
        if not file_path.is_file():
            print(f"[{self.name}] I'm sorry, I couldn't find a file at '{file_path}'.")
            return

        print(f"[{self.name}] Reading and studying the document: {file_path.name}...")
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Ask the AI to summarize the document into key concepts
            prompt = (
                "You are an expert at distilling knowledge. Read the following document and "
                "summarize its most important facts and concepts into a concise paragraph. "
                "This summary will be used as a memory for an AI assistant.\n\n"
                f"--- DOCUMENT ---\n{content[:8000]}\n--- END DOCUMENT ---" # Limit to first 8k characters
            )
            
            messages = [
                {"role": "system", "content": self.vespera_persona},
                {"role": "user", "content": prompt}
            ]
            
            summary = self.client.chat(messages)
            
            # The "prompt" for Daisy's memory will be the filename
            # The "completion" will be the AI-generated summary
            self.train_mem.save_training_example(f"what are the key points from {file_path.name}", summary)
            
            print(f"\n[Vespera]> I've finished studying the document. I've learned about:")
            print(f"  {summary}\n")
            
        except Exception as e:
            print(f"[{self.name}] I had trouble reading that document, darling. {e}")

def create_worker(config: dict):
    return LearnWorker(config)
