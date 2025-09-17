# subsystem_registry.py

class SubsystemRegistry:
    def __init__(self):
        self.registry = {}
        self.commentary_mode = True
        self.status_log = []

    # ┌────────────────────────────────────────────┐
    # │ Registration & Metadata                    │
    # └────────────────────────────────────────────┘

    def register(self, name, role, tone="neutral", avatar=None, diagnostics_func=None):
        self.registry[name] = {
            "role": role,
            "tone": tone,
            "avatar": avatar,
            "diagnostics": diagnostics_func
        }
        self.narrate(f"Subsystem '{name}' registered as '{role}' with tone '{tone}'.")

    def get_metadata(self, name):
        return self.registry.get(name, None)

    def list_subsystems(self):
        return list(self.registry.keys())

    def run_diagnostics(self, name):
        if name in self.registry and self.registry[name]["diagnostics"]:
            try:
                return self.registry[name]["diagnostics"]()
            except Exception as e:
                return {"error": str(e)}
        return {"error": "Subsystem not found or diagnostics unavailable."}

    # ┌────────────────────────────────────────────┐
    # │ Commentary & Logging                       │
    # └────────────────────────────────────────────┘

    def narrate(self, message):
        if self.commentary_mode:
            print(f"[Registry Commentary] {message}")

    def log_status(self, message):
        self.status_log.append(message)

    def initialize(self):
        self.log_status("Subsystem Registry initialized.")
        self.narrate("Metadata layer active. Roles and personalities mapped.")

