# warp_field_subsystems/field_containment_shield.py

import math
import random

class FieldContainmentShield:
    def __init__(self, shield_thickness_cm, shield_area_m2, magnetic_field_T, gravitic_flux_Nm2):
        self.mu_0 = 4 * math.pi * 1e-7  # Vacuum permeability (H/m)
        self.shield_thickness = shield_thickness_cm * 1e-2  # Convert to meters
        self.area = shield_area_m2
        self.B = magnetic_field_T
        self.GF = gravitic_flux_Nm2

        self.commentary_mode = True
        self.status_log = []
        self.fault_code = None

    # ┌────────────────────────────────────────────┐
    # │ Shielding Calculations                     │
    # └────────────────────────────────────────────┘

    def magnetic_shielding_factor(self):
        # Simplified model: μ₀ * thickness * field strength
        return round(self.mu_0 * self.shield_thickness * self.B, 6)

    def gravitic_stress_index(self):
        # Heuristic: stress increases with flux and area
        stress = self.GF * self.area
        return round(stress, 2)

    def harmonic_integrity(self):
        # Simulate harmonic drift
        drift = random.uniform(0.0, 1.0)
        integrity = "Stable" if drift < 0.7 else "Unstable"
        if integrity == "Unstable":
            self.fault_code = "SHIELD-001: Harmonic drift detected"
        elif self.gravitic_stress_index() > 1e6:
            self.fault_code = "SHIELD-002: Gravitic stress overload"
        else:
            self.fault_code = None
        return integrity

    def run_diagnostics(self):
        return {
            "Shield Thickness (cm)": round(self.shield_thickness * 100, 2),
            "Shield Area (m²)": round(self.area, 2),
            "Magnetic Field Strength (T)": round(self.B, 2),
            "Gravitic Flux (N/m²)": round(self.GF, 2),
            "Magnetic Shielding Factor": self.magnetic_shielding_factor(),
            "Gravitic Stress Index": self.gravitic_stress_index(),
            "Harmonic Integrity": self.harmonic_integrity(),
            "Fault Code": self.fault_code or "None"
        }

    # ┌────────────────────────────────────────────┐
    # │ Commentary & Logging                       │
    # └────────────────────────────────────────────┘

    def narrate(self, message):
        if self.commentary_mode:
            print(f"[ContainmentShield Commentary] {message}")

    def log_status(self, message):
        self.status_log.append(message)

    def initialize(self):
        self.log_status("Field Containment Shield initialized.")
        self.narrate("Magnetic and gravitic harmonics aligned. Containment field active.")

