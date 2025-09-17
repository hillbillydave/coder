# warp_field_subsystems/energy_core_stabilizer.py

import math
import random

class EnergyCoreStabilizer:
    def __init__(self, core_mass_kg, plasma_temp_MK, containment_field_strength_T):
        self.c = 299792458  # Speed of light (m/s)
        self.core_mass = core_mass_kg
        self.T = plasma_temp_MK * 1e6  # Convert to Kelvin
        self.B = containment_field_strength_T  # Tesla

        self.nominal_energy_output = self.calculate_mass_energy()
        self.commentary_mode = True
        self.status_log = []
        self.fault_code = None

    # ┌────────────────────────────────────────────┐
    # │ Core Energy Calculations                   │
    # └────────────────────────────────────────────┘

    def calculate_mass_energy(self):
        # E = mc²
        return self.core_mass * self.c**2

    def fusion_efficiency(self):
        # Heuristic: efficiency drops with unstable plasma or weak containment
        instability = random.uniform(0.95, 1.05)
        efficiency = (self.B / 10) * (self.T / 1e8) * instability
        return round(min(efficiency, 1.0), 4)

    def containment_integrity(self):
        # Simple model: integrity drops if field strength < threshold
        threshold = 5.0  # Tesla
        return "Stable" if self.B >= threshold else "Unstable"

    def simulate_energy_output(self):
        efficiency = self.fusion_efficiency()
        output = self.nominal_energy_output * efficiency
        if efficiency < 0.5:
            self.fault_code = "CORE-001: Fusion instability detected"
        elif self.containment_integrity() == "Unstable":
            self.fault_code = "CORE-002: Containment field below threshold"
        else:
            self.fault_code = None
        return output

    def run_diagnostics(self):
        output = self.simulate_energy_output()
        return {
            "Core Mass (kg)": round(self.core_mass, 2),
            "Plasma Temperature (K)": round(self.T, 2),
            "Containment Field (T)": round(self.B, 2),
            "Nominal Mass-Energy (J)": "{:.2e}".format(self.nominal_energy_output),
            "Fusion Efficiency": self.fusion_efficiency(),
            "Containment Integrity": self.containment_integrity(),
            "Live Energy Output (J)": "{:.2e}".format(output),
            "Fault Code": self.fault_code or "None"
        }

    # ┌────────────────────────────────────────────┐
    # │ Commentary & Logging                       │
    # └────────────────────────────────────────────┘

    def narrate(self, message):
        if self.commentary_mode:
            print(f"[EnergyCore Commentary] {message}")

    def log_status(self, message):
        self.status_log.append(message)

    def initialize(self):
        self.log_status("Energy Core Stabilizer initialized.")
        self.narrate("Fusion chamber online. Containment field harmonized.")

