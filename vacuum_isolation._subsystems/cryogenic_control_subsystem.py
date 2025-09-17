# cryogenic_control_subsystem.py

import math

class CryogenicControl:
    def __init__(self, loop_length_m, cross_section_area_m2, thermal_conductivity_WmK,
                 surface_area_m2, emissivity, ambient_temp_K, chamber_temp_K):
        self.L = loop_length_m
        self.A = cross_section_area_m2
        self.k = thermal_conductivity_WmK
        self.surface_area = surface_area_m2
        self.epsilon = emissivity
        self.T_ambient = ambient_temp_K
        self.T_chamber = chamber_temp_K

        self.sigma = 5.670374419e-8  # Stefan-Boltzmann constant
        self.commentary_mode = True
        self.status_log = []

    # ┌────────────────────────────────────────────┐
    # │ Core Calculations                          │
    # └────────────────────────────────────────────┘

    def calculate_conductive_cooling(self):
        delta_T = self.T_ambient - self.T_chamber
        return self.k * self.A * delta_T / self.L

    def calculate_radiative_cooling(self):
        return self.epsilon * self.sigma * self.surface_area * (self.T_ambient**4 - self.T_chamber**4)

    def calculate_total_cooling(self):
        return self.calculate_conductive_cooling() + self.calculate_radiative_cooling()

    def run_diagnostics(self):
        return {
            "Conductive Cooling (W)": round(self.calculate_conductive_cooling(), 4),
            "Radiative Cooling (W)": round(self.calculate_radiative_cooling(), 4),
            "Total Cooling Power (W)": round(self.calculate_total_cooling(), 4)
        }

    def narrate(self, message):
        if self.commentary_mode:
            print(f"[Cryogenic Commentary] {message}")

    def log_status(self, message):
        self.status_log.append(message)

    def initialize(self):
        self.log_status("Cryogenic Control subsystem initialized.")
        self.narrate("Thermal gradients aligned. Space-borne silence flowing through the loop.")

