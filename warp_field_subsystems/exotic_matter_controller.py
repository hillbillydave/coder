# warp_field_subsystems/exotic_matter_controller.py

import math

class ExoticMatterController:
    def __init__(self, plate_separation_nm, plate_area_cm2, vacuum_temp_K):
        self.h = 6.62607015e-34  # Planck constant (J·s)
        self.c = 299792458       # Speed of light (m/s)
        self.pi = math.pi

        self.d = plate_separation_nm * 1e-9  # Convert to meters
        self.A = plate_area_cm2 * 1e-4       # Convert to m²
        self.T = vacuum_temp_K

        self.commentary_mode = True
        self.status_log = []

    # ┌────────────────────────────────────────────┐
    # │ Core Casimir & Quantum Calculations        │
    # └────────────────────────────────────────────┘

    def casimir_energy_density(self):
        # Casimir energy per unit area between plates
        return - (self.pi**2 * self.h * self.c) / (240 * self.d**4)

    def total_casimir_energy(self):
        return self.casimir_energy_density() * self.A

    def fluctuation_suppression_index(self):
        # Heuristic: lower temperature and smaller separation = better suppression
        suppression = 1 / (self.d * self.T)
        return round(suppression, 6)

    def run_diagnostics(self):
        return {
            "Plate Separation (nm)": round(self.d * 1e9, 2),
            "Plate Area (cm²)": round(self.A * 1e4, 2),
            "Vacuum Temperature (K)": round(self.T, 2),
            "Casimir Energy Density (J/m²)": "{:.2e}".format(self.casimir_energy_density()),
            "Total Casimir Energy (J)": "{:.2e}".format(self.total_casimir_energy()),
            "Fluctuation Suppression Index": self.fluctuation_suppression_index()
        }

    # ┌────────────────────────────────────────────┐
    # │ Commentary & Logging                       │
    # └────────────────────────────────────────────┘

    def narrate(self, message):
        if self.commentary_mode:
            print(f"[ExoticMatter Commentary] {message}")

    def log_status(self, message):
        self.status_log.append(message)

    def initialize(self):
        self.log_status("Exotic Matter Controller initialized.")
        self.narrate("Casimir plates aligned. Vacuum fluctuations suppressed.")

