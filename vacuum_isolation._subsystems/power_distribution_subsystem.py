# power_distribution_subsystem.py

import random

class PowerDistributionMonitor:
    def __init__(self):
        self.subsystem_power_map = {}
        self.voltage_nominal = 12.0  # Volts
        self.commentary_mode = True
        self.status_log = []

    # ┌────────────────────────────────────────────┐
    # │ Subsystem Registration                     │
    # └────────────────────────────────────────────┘

    def register_subsystem(self, name, power_draw_W):
        self.subsystem_power_map[name] = {
            "nominal_power": power_draw_W,
            "voltage": self.voltage_nominal,
            "current": round(power_draw_W / self.voltage_nominal, 3),
            "status": "OK"
        }
        self.narrate(f"Subsystem '{name}' registered with {power_draw_W}W draw.")

    # ┌────────────────────────────────────────────┐
    # │ Power Monitoring & Fault Detection         │
    # └────────────────────────────────────────────┘

    def simulate_power_fluctuations(self):
        for name, data in self.subsystem_power_map.items():
            fluctuation = random.uniform(-0.2, 0.2)  # ±20% fluctuation
            new_power = data["nominal_power"] * (1 + fluctuation)
            new_current = round(new_power / self.voltage_nominal, 3)
            data["current"] = new_current
            data["status"] = "OK" if new_power < data["nominal_power"] * 1.2 else "OVERLOAD"
            if data["status"] == "OVERLOAD":
                self.log_status(f"⚠️ Power spike in '{name}': {round(new_power, 2)}W")
                self.narrate(f"Subsystem '{name}' experiencing overload.")

    def run_diagnostics(self):
        self.simulate_power_fluctuations()
        return {
            name: {
                "Voltage (V)": self.voltage_nominal,
                "Current (A)": data["current"],
                "Status": data["status"]
            }
            for name, data in self.subsystem_power_map.items()
        }

    # ┌────────────────────────────────────────────┐
    # │ Commentary & Logging                       │
    # └────────────────────────────────────────────┘

    def narrate(self, message):
        if self.commentary_mode:
            print(f"[Power Commentary] {message}")

    def log_status(self, message):
        self.status_log.append(message)

    def initialize(self):
        self.log_status("Power Distribution Monitor initialized.")
        self.narrate("Energy grid stabilized. Voltage nominal across all subsystems.")

