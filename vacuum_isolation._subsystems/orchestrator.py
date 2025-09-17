# subsystems/orchestrator.py

class SubsystemOrchestrator:
    def __init__(self):
        self.subsystems = {}
        self.commentary_mode = True
        self.status_log = []
        self.boot_sequence = []

    # ┌────────────────────────────────────────────┐
    # │ Subsystem Registration                     │
    # └────────────────────────────────────────────┘

    def register(self, name, instance, diagnostics_func=None, init_func=None):
        self.subsystems[name] = {
            "instance": instance,
            "diagnostics": diagnostics_func or getattr(instance, "run_diagnostics", None),
            "initialize": init_func or getattr(instance, "initialize", None)
        }
        self.narrate(f"Subsystem '{name}' registered.")

    def initialize_all(self):
        for name, module in self.subsystems.items():
            try:
                if module["initialize"]:
                    module["initialize"]()
                    self.boot_sequence.append(name)
                    self.log_status(f"{name} initialized.")
            except Exception as e:
                self.log_status(f"⚠️ Initialization failed for {name}: {e}")
                self.narrate(f"Subsystem '{name}' failed to initialize.")

    def collect_ensemble_diagnostics(self):
        snapshot = {}
        for name, module in self.subsystems.items():
            try:
                if module["diagnostics"]:
                    snapshot[name] = module["diagnostics"]()
            except Exception as e:
                snapshot[name] = {"error": str(e)}
                self.log_status(f"⚠️ Diagnostics failed for {name}: {e}")
        return snapshot

    # ┌────────────────────────────────────────────┐
    # │ Commentary & Logging                       │
    # └────────────────────────────────────────────┘

    def narrate(self, message):
        if self.commentary_mode:
            print(f"[Orchestrator] {message}")

    def log_status(self, message):
        self.status_log.append(message)

    def cli_fallback(self, command):
        if command == "status":
            return self.collect_ensemble_diagnostics()
        elif command == "boot":
            return self.boot_sequence
        elif command == "commentary":
            self.commentary_mode = not self.commentary_mode
            return f"Commentary mode {'enabled' if self.commentary_mode else 'disabled'}."
        else:
            return "Unknown command. Try: status, boot, commentary"

    def initialize(self):
        self.narrate("Subsystem Orchestrator initialized. Preparing ensemble boot sequence.")
        self.initialize_all()

