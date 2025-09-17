# vacuum_isolation_subsystem.py

import math
import random

class VacuumIsolationModule:
    def __init__(self, chamber_volume_liters, pump_area_cm2, gas_mass_amu, surface_area_cm2, surface_temp_K):
        self.k = 1.380649e-23
        self.R = 8.314
        self.sigma = 5.670374419e-8
        self.mu = 80000
        self.tau_0 = 1e-13

        self.V = chamber_volume_liters * 1e-3
        self.A = pump_area_cm2 * 1e-4
        self.M = gas_mass_amu * 1.660539e-27
        self.surface_area = surface_area_cm2 * 1e-4
        self.T = surface_temp_K

        self.commentary_mode = True
        self.status_log = []
        self.fault_code = None

    def calculate_pumping_speed(self):
        return self.A * math.sqrt(self.k * self.T / self.M)

    def calculate_evacuation_time(self):
        S = self.calculate_pumping_speed()
        return self.V / S

    def calculate_radiative_heat(self, emissivity=0.1):
        return emissivity * self.sigma * self.surface_area * self.T**4

    def calculate_residence_time(self, E_v_kJmol):
        E_v = E_v_kJmol * 1000
        return self.tau_0 * math.exp(E_v / (self.R * self.T))

    def calculate_shielding_factor(self, wall_thickness_mm, diameter_cm):
        d = wall_thickness_mm * 1e-3
        D = diameter_cm * 1e-2
        return (self.mu * d) / D

    def simulate_live_conditions(self):
        self.T += random.uniform(-0.5, 0.5)
        pressure = random.uniform(1e-10, 1e-8)
        if pressure > 1e-9:
            self.fault_code = "VAC-001: Pressure above UHV threshold"
        elif self.T > 25:
            self.fault_code = "VAC-002: Cryopump surface overheating"
        else:
            self.fault_code = None
        return pressure

    def run_diagnostics(self):
        pressure = self.simulate_live_conditions()
        return {
            "Pumping Speed (m³/s)": round(self.calculate_pumping_speed(), 6),
            "Evacuation Time (s)": round(self.calculate_evacuation_time(), 2),
            "Radiative Heat Load (W)": round(self.calculate_radiative_heat(), 4),
            "Gas Residence Time (s)": "{:.2e}".format(self.calculate_residence_time(40)),
            "Magnetic Shielding Factor": round(self.calculate_shielding_factor(2, 10), 2),
            "Live Pressure (Torr)": "{:.2e}".format(pressure),
            "Fault Code": self.fault_code or "None"
        }

    def monitor_faults(self, recovery_engine):
        diag = self.run_diagnostics()
        fault = diag.get("Fault Code")
        if fault and fault != "None":
            recovery_engine.log_fault("VacuumIsolation", fault, severity="high")

    def narrate(self, message):
        if self.commentary_mode:
            print(f"[Vacuum Commentary] {message}")

    def log_status(self, message):
        self.status_log.append(message)

    def initialize(self):
        self.log_status("Vacuum Isolation Module initialized.")
        self.narrate("Quantum silence achieved. Isolation field geometry stabilized.")

