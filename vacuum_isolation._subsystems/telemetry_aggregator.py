# subsystems/telemetry_aggregator.py

import datetime

class TelemetryAggregator:
    def __init__(self):
        self.telemetry_streams = {}
        self.fault_registry = []
        self.commentary_mode = True

    # ┌────────────────────────────────────────────┐
    # │ Subsystem Registration                     │
    # └────────────────────────────────────────────┘

    def register_subsystem(self, name, diagnostics_func):
        self.telemetry_streams[name] = diagnostics_func
        self.narrate(f"Subsystem '{name}' registered for telemetry.")

    def collect_telemetry(self):
        snapshot = {}
        for name, func in self.telemetry_streams.items():
            try:
                snapshot[name] = func()
            except Exception as e:
                self.log_fault(name, str(e))
                snapshot[name] = {"error": str(e)}
        return snapshot

    # ┌────────────────────────────────────────────┐
    # │ Fault Logging                              │
    # └────────────────────────────────────────────┘

    def log_fault(self, subsystem_name, fault_description):
        timestamp = datetime.datetime.now().isoformat()
        fault_entry = {
            "subsystem": subsystem_name,
            "description": fault_description,
            "timestamp": timestamp
        }
        self.fault_registry.append(fault_entry)
        self.narrate(f"⚠️ Fault detected in '{subsystem_name}': {fault_description}")

    def get_fault_log(self):
        return self.fault_registry

    # ┌────────────────────────────────────────────┐
    # │ Commentary & CLI Fallback                  │
    # └────────────────────────────────────────────┘

    def narrate(self, message):
        if self.commentary_mode:
            print(f"[Telemetry Commentary] {message}")

    def cli_fallback(self, command):
        if command == "snapshot":
            return self.collect_telemetry()
        elif command == "faults":
            return self.get_fault_log()
        elif command == "commentary":
            self.commentary_mode = not self.commentary_mode
            return f"Commentary mode {'enabled' if self.commentary_mode else 'disabled'}."
        else:
            return "Unknown command. Try: snapshot, faults, commentary"

    def initialize(self):
        self.narrate("Telemetry Aggregator initialized. Listening to the ensemble.")

