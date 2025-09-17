# warp_field_subsystems/power_containment_monitor.py

import random

class PowerContainmentMonitor:
    def __init__(self):
        self.subsystem_power_map = {}
        self.nominal_voltage = 1e9  # Volts (warp-scale)
        self.commentary_mode = True
        self.status_log = []

    # ┌────────────────────────────────────────────┐
    # │ Subsystem Registration                     │
    # └────────────────────────────────────────────┘

    def register_subsystem(self, name, power_draw_GW):
        self.subsystem_power_map[name] = {
            "nominal_power": power_draw_GW,
            "voltage": self.nominal_voltage,
            "current": round(power_draw_GW * 1e9 / self.nominal_voltage, 3),
            "status": "OK"
        }
        self.narrate(f"Subsystem '{name}' registered with {power_draw_GW} GW draw.")

    # ┌────────────────────────────────────────────┐
    # │ Power Monitoring & Containment Checks      │
    # └────────────────────────────────────────────┘

    def simulate_fluctuations(self):
        for name, data in self.subsystem_power_map.items():
            fluctuation = random.uniform(-0.3, 0.3)
            new_power = data["nominal_power"] * (1 + fluctuation)
            new_current = round(new_power * 1e9 / self.nominal_voltage, 3)
            data["current"] = new_current
            data["status"] = "OK" if new_power < data["nominal_power"] * 1.3 else "OVERLOAD"
            if data["status"] == "OVERLOAD":
                self.log_status(f"⚠️ Power overload in '{name}': {round(new_power, 2)} GW")
                self.narrate(f"Containment breach risk in '{name}'.")

    def run_diagnostics(self):
        self.simulate_fluctuations()
        return {
            name: {
                "Voltage (V)": self.nominal_voltage,
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
            print(f"[PowerContainment Commentary] {message}")

    def log_status(self, message):
        self.status_log.append(message)

    def initialize(self):
        self.log_status("Power & Containment Monitor initialized.")
        self.narrate("Energy grid stabilized. Containment fields nominal.")

