# quantum_stabilization_subsystems/quantum_telemetry.py

class QuantumTelemetry:
    def __init__(self):
        self.subsystem_map = {}
        self.commentary_mode = True
        self.status_log = []

    # ┌────────────────────────────────────────────┐
    # │ Subsystem Registration                     │
    # └────────────────────────────────────────────┘

    def register_subsystem(self, name, diagnostics_func):
        self.subsystem_map[name] = diagnostics_func
        self.narrate(f"Quantum subsystem '{name}' registered for telemetry aggregation.")

    # ┌────────────────────────────────────────────┐
    # │ Ensemble Diagnostics                       │
    # └────────────────────────────────────────────┘

    def collect_telemetry(self):
        snapshot = {}
        for name, diag_func in self.subsystem_map.items():
            try:
                snapshot[name] = diag_func()
            except Exception as e:
                snapshot[name] = {"error": str(e)}
                self.narrate(f"⚠️ Telemetry error in '{name}': {e}")
        return snapshot

    def detect_faults(self):
        faults = {}
        for name, diag_func in self.subsystem_map.items():
            try:
                data = diag_func()
                fault = data.get("Fault Code")
                if fault and fault != "None":
                    faults[name] = fault
            except Exception:
                continue
        return faults

    def run_summary(self):
        telemetry = self.collect_telemetry()
        faults = self.detect_faults()
        summary = {
            "Quantum Subsystem Count": len(self.subsystem_map),
            "Active Faults": faults,
            "Telemetry Snapshot": telemetry
        }
        return summary

    # ┌────────────────────────────────────────────┐
    # │ Commentary & Logging                       │
    # └────────────────────────────────────────────┘

    def narrate(self, message):
        if self.commentary_mode:
            print(f"[QuantumTelemetry Commentary] {message}")

    def log_status(self, message):
        self.status_log.append(message)

    def initialize(self):
        self.log_status("Quantum Telemetry Engine initialized.")
        self.narrate("Quantum telemetry channels open. Coherence metrics flowing.")

