# subsystem_registry.py

class SubsystemRegistry:
    def __init__(self):
        self.registry = {}
        self.commentary_mode = True

    def register(self, name, role="Subsystem", tone="neutral"):
        self.registry[name] = {
            "role": role,
            "tone": tone
        }
        self.narrate(f"Registered '{name}' as '{role}' with tone '{tone}'.")

    def get_metadata(self, name):
        return self.registry.get(name, {"role": "Unknown", "tone": "neutral"})

    def narrate(self, message):
        if self.commentary_mode:
            print(f"[Registry Commentary] {message}")

    def initialize(self):
        self.narrate("Subsystem Registry initialized. Metadata channels open.")

