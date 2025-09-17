# warp_field_subsystems/thermal_stress_feedback.py

class ThermalStressFeedback:
    def __init__(self):
        self.temperature_map = {}
        self.stress_map = {}
        self.temp_drift_threshold_K = 5.0
        self.stress_threshold_Nm2 = 1e6
        self.commentary_mode = True
        self.status_log = []

    # ┌────────────────────────────────────────────┐
    # │ Subsystem Registration                     │
    # └────────────────────────────────────────────┘

    def register_subsystem(self, name, temperature_K, stress_Nm2):
        self.temperature_map[name] = temperature_K
        self.stress_map[name] = stress_Nm2
        self.narrate(f"Subsystem '{name}' registered with T={temperature_K}K, σ={stress_Nm2}N/m².")

    # ┌────────────────────────────────────────────┐
    # │ Drift & Stress Monitoring                  │
    # └────────────────────────────────────────────┘

    def calculate_temp_drift(self):
        temps = list(self.temperature_map.values())
        return round(max(temps) - min(temps), 4) if temps else 0.0

    def detect_stress_overload(self):
        return {
            name: stress for name, stress in self.stress_map.items()
            if stress > self.stress_threshold_Nm2
        }

    def run_diagnostics(self):
        drift = self.calculate_temp_drift()
        overloads = self.detect_stress_overload()
        status = "Stable" if drift <= self.temp_drift_threshold_K and not overloads else "Unstable"
        if status == "Unstable":
            self.narrate(f"⚠️ Thermal drift or stress overload detected.")
        return {
            "Temperature Drift (K)": drift,
            "Stress Overloads": overloads,
            "Status": status
        }

    # ┌────────────────────────────────────────────┐
    # │ Commentary & Logging                       │
    # └────────────────────────────────────────────┘

    def narrate(self, message):
        if self.commentary_mode:
            print(f"[ThermalStress Commentary] {message}")

    def log_status(self, message):
        self.status_log.append(message)

    def initialize(self):
        self.log_status("Thermal & Stress Feedback Loop initialized.")
        self.narrate("Thermal gradients and gravitic stress harmonized.")

