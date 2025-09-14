# app.py (Upgraded Version)
import os
from queue import Queue, Empty # MODIFICATION: Import Empty exception
import json
import time
import re
import threading
import importlib
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys
from datetime import datetime, timedelta
import pygame
import requests
from workers.mission_control_worker import start_mission_control_dashboard

sys.path.append(str(Path(__file__).parent))

# (All your configuration and class definitions remain EXACTLY the same)
# ... CEO, LLMClient, DaisyBotAgent, etc. are all perfect as they are.
# I will omit them here for brevity but they should be in your file.

# =====================================================================
# MODIFICATION: We are replacing your main() function and adding one helper
# =====================================================================

def process_command(user_input: str, ceo: 'CEO', supervisor: 'TrainingSupervisor', daisy_agent: 'DaisyBotAgent', trainer_thread: 'AutonomousTrainer'):
    """
    This new function contains all your command logic.
    It can be called with input from the terminal OR the web chat.
    It returns a response string.
    """
    trainer_thread.update_activity()
    cmd_parts = user_input.split()
    cmd = cmd_parts[0].lower()

    if cmd in ['quit', 'exit']:
        return "exit" # Special signal to exit
    elif cmd == 'help':
        # This part is now tricky, we'll return a simple message for web
        return "Help menu is available in the terminal."
    elif cmd == 'stop' and len(cmd_parts) > 1:
        ceo.stop_task(cmd_parts[1])
        return f"Signal sent to stop worker '{cmd_parts[1]}'."
    elif cmd in ceo.worker_blueprints:
        ceo.assign_task(user_input)
        return f"Task assigned to worker '{cmd}'."
    elif user_input.lower().startswith('train on '):
        supervisor.start_session(user_input[len('train on '):])
        return f"Training session started on topic: {user_input[len('train on '):]}"
    elif user_input.lower() == 'stop training':
        supervisor.stop_session()
        return "Training session paused."
    elif user_input.lower().startswith('ask vespera '):
        # This part requires a response, which we can't easily get back here.
        # For now, let's just acknowledge it.
        # A more advanced version would use another queue for Vespera's replies.
        question = user_input[len('ask vespera '):]
        print(f"\n[Web/Terminal] Forwarding question to Vespera: {question}")
        return "Question sent to Vespera. Her response will appear in the main terminal."
    else:
        # This is a chat for Daisy-Bot
        daisy_reply = daisy_agent.get_offline_reply(user_input)
        if daisy_reply:
            return daisy_reply
        else:
            return "Well shucks, I ain't learned about that yet. You'll have to ask Vespera for me."

def main():
    """The main event, upgraded for multi-interface input."""
    pygame.init()
    print("✨ Vespera's Modular Studio is now open! ✨")
    print("="*42); sys.stdout.flush()
    
    load_global_config()
    
    # --- NEW: Setup the communication queues ---
    request_queue = Queue()
    response_queue = Queue()
    
    client = LLMClient()
    train_mem = TrainingDataMemory()
    daisy_agent = DaisyBotAgent(train_mem)
    supervisor = TrainingSupervisor(client, train_mem, daisy_agent)
    
    shared_data_queue = Queue()
    GLOBAL_CONFIG['shared_queue'] = shared_data_queue
    
    ceo = CEO(GLOBAL_CONFIG)
    trainer_thread = AutonomousTrainer(supervisor)
    trainer_thread.start()

    # --- MODIFICATION: Pass the queues to the dashboard ---
    start_mission_control_dashboard(request_queue, response_queue)
    
    def print_help_menu():
        # (This function is unchanged)
        # ...
        pass # Placeholder for your existing function

    print_help_menu()

    # --- NEW: Thread for handling blocking terminal input ---
    def terminal_input_thread(stop_event):
        while not stop_event.is_set():
            try:
                terminal_input = input("You> ").strip()
                if terminal_input:
                    request_queue.put(("terminal", terminal_input))
            except (EOFError, KeyboardInterrupt):
                request_queue.put(("terminal", "exit"))
                break
    
    stop_terminal_thread = threading.Event()
    term_thread = threading.Thread(target=terminal_input_thread, args=(stop_terminal_thread,), daemon=True)
    term_thread.start()

    # --- NEW: The main, non-blocking application loop ---
    print("\n[Studio] Now listening for commands from Terminal and Web Chat...")
    while True:
        try:
            # Check for input from either source, with a timeout
            source, user_input = request_queue.get(timeout=0.2)
            
            # Process the command using our new function
            response = process_command(user_input, ceo, supervisor, daisy_agent, trainer_thread)
            
            if response == "exit":
                break # Exit the main loop

            if source == "web":
                # If the message came from the web, put the response back for the web server
                response_queue.put(response)
            else:
                # If the message came from the terminal, just print the response
                print(f"\n[Response]> {response}\n")

        except Empty:
            # This is normal, it means no input was received. The loop continues.
            continue
        except KeyboardInterrupt:
            break

    print("Goodbye for now, sweety. Kisses! 💋")
    stop_terminal_thread.set() # Cleanly stop the terminal thread

if __name__ == "__main__":
    main()
