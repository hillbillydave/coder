# boundary_geometry_subsystem.py

import math

class BoundaryGeometryController:
    def __init__(self, cavity_length_m, cavity_width_m, cavity_height_m, mode_frequency_Hz):
        self.L = cavity_length_m
        self.W = cavity_width_m
        self.H = cavity_height_m
        self.f_mode = mode_frequency_Hz

        self.c = 299792458  # Speed of light (m/s)
        self.commentary_mode = True
        self.status_log = []

    # ┌────────────────────────────────────────────┐
    # │ Core Calculations                          │
    # └────────────────────────────────────────────┘

    def calculate_mode_wavelength(self):
        return self.c / self.f_mode

    def calculate_resonance_condition(self):
        λ = self.calculate_mode_wavelength()
        return {
            "λ_mode (m)": round(λ, 6),
            "Fits Along Length": round(self.L / λ, 2),
            "Fits Along Width": round(self.W / λ, 2),
            "Fits Along Height": round(self.H / λ, 2)
        }

    def calculate_fluctuation_suppression_index(self):
        ratios = self.calculate_resonance_condition()
        suppression_score = sum([abs(ratios[k] - round(ratios[k])) for k in ratios if "Fits" in k])
        return round(suppression_score, 3)

    def run_diagnostics(self):
        resonance = self.calculate_resonance_condition()
        suppression = self.calculate_fluctuation_suppression_index()
        return {
            **resonance,
            "Suppression Index": suppression
        }

    def narrate(self, message):
        if self.commentary_mode:
            print(f"[Geometry Commentary] {message}")

    def log_status(self, message):
        self.status_log.append(message)

    def initialize(self):
        self.log_status("Boundary Geometry Controller initialized.")
        self.narrate("Spatial harmonics aligned. Vacuum fluctuations sculpted into silence.")

