# thermal_feedback_subsystem.py

class ThermalFeedbackLoop:
    def __init__(self):
        self.temperature_map = {}
        self.drift_threshold_K = 2.0  # Max allowed drift in Kelvin
        self.commentary_mode = True
        self.status_log = []

    # ┌────────────────────────────────────────────┐
    # │ Subsystem Registration                     │
    # └────────────────────────────────────────────┘

    def register_subsystem(self, name, temperature_K):
        self.temperature_map[name] = temperature_K
        self.narrate(f"Subsystem '{name}' registered at {temperature_K}K.")

    def update_temperature(self, name, new_temp_K):
        if name in self.temperature_map:
            self.temperature_map[name] = new_temp_K
            self.narrate(f"Temperature updated for '{name}': {new_temp_K}K.")

    # ┌────────────────────────────────────────────┐
    # │ Drift Monitoring & Gradient Analysis       │
    # └────────────────────────────────────────────┘

    def calculate_drift(self):
        temps = list(self.temperature_map.values())
        if not temps:
            return 0.0
        max_temp = max(temps)
        min_temp = min(temps)
        return round(max_temp - min_temp, 4)

    def check_stability(self):
        drift = self.calculate_drift()
        status = "Stable" if drift <= self.drift_threshold_K else "Unstable"
        if status == "Unstable":
            self.narrate(f"⚠️ Thermal drift detected: {drift}K across subsystems.")
        return {
            "Drift (K)": drift,
            "Status": status
        }

    def run_diagnostics(self):
        return {
            "Subsystem Temperatures (K)": self.temperature_map,
            **self.check_stability()
        }

    # ┌────────────────────────────────────────────┐
    # │ Commentary & Logging                       │
    # └────────────────────────────────────────────┘

    def narrate(self, message):
        if self.commentary_mode:
            print(f"[Thermal Commentary] {message}")

    def log_status(self, message):
        self.status_log.append(message)

    def initialize(self):
        self.log_status("Thermal Feedback Loop initialized.")
        self.narrate("Entropy harmonized. Thermal gradients flowing in balance.")

