# warp_field_subsystems/warp_orchestrator.py

class WarpOrchestrator:
    def __init__(self):
        self.subsystems = {}
        self.commentary_mode = True
        self.status_log = []

    # ┌────────────────────────────────────────────┐
    # │ Subsystem Registration                     │
    # └────────────────────────────────────────────┘

    def register(self, name, subsystem_obj):
        self.subsystems[name] = subsystem_obj
        self.narrate(f"Subsystem '{name}' registered with orchestrator.")

    def initialize_all(self):
        for name, obj in self.subsystems.items():
            try:
                obj.initialize()
                self.narrate(f"✅ '{name}' initialized successfully.")
            except Exception as e:
                self.narrate(f"❌ Initialization failed for '{name}': {e}")
                self.log_status(f"Error initializing '{name}': {e}")

    # ┌────────────────────────────────────────────┐
    # │ Ensemble Diagnostics                       │
    # └────────────────────────────────────────────┘

    def collect_ensemble_diagnostics(self):
        diagnostics = {}
        for name, obj in self.subsystems.items():
            try:
                diagnostics[name] = obj.run_diagnostics()
            except Exception as e:
                diagnostics[name] = {"error": str(e)}
                self.narrate(f"⚠️ Diagnostic error in '{name}': {e}")
        return diagnostics

    def detect_active_faults(self):
        faults = {}
        for name, obj in self.subsystems.items():
            try:
                diag = obj.run_diagnostics()
                fault = diag.get("Fault Code")
                if fault and fault != "None":
                    faults[name] = fault
            except Exception:
                continue
        return faults

    # ┌────────────────────────────────────────────┐
    # │ Commentary & Logging                       │
    # └────────────────────────────────────────────┘

    def narrate(self, message):
        if self.commentary_mode:
            print(f"[WarpOrchestrator Commentary] {message}")

    def log_status(self, message):
        self.status_log.append(message)

    def status_report(self):
        return {
            "Subsystem Count": len(self.subsystems),
            "Active Faults": self.detect_active_faults(),
            "Status Log": self.status_log
        }

