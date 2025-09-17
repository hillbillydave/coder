# subsystems/vibration_damping.py

import math

class VibrationDampingBase:
    def __init__(self, mass_kg, spring_constant_Nm, damping_coefficient_Ns_m):
        self.m = mass_kg
        self.k = spring_constant_Nm
        self.c = damping_coefficient_Ns_m

        # Derived quantities
        self.omega_n = math.sqrt(self.k / self.m)  # Natural frequency (rad/s)
        self.c_critical = 2 * math.sqrt(self.k * self.m)
        self.zeta = self.c / self.c_critical  # Damping ratio

        self.commentary_mode = True
        self.status_log = []

    # ┌────────────────────────────────────────────┐
    # │ Core Calculations                          │
    # └────────────────────────────────────────────┘

    def calculate_response_type(self):
        if self.zeta < 1:
            return "Underdamped"
        elif self.zeta == 1:
            return "Critically Damped"
        else:
            return "Overdamped"

    def calculate_displacement(self, F_N, t_s):
        # Solves m*x'' + c*x' + k*x = F(t) for a step input
        # Simplified model: displacement at time t for unit force
        omega_d = self.omega_n * math.sqrt(1 - self.zeta**2) if self.zeta < 1 else 0
        if self.zeta < 1:
            A = F_N / self.k
            return A * math.exp(-self.zeta * self.omega_n * t_s) * math.cos(omega_d * t_s)
        elif self.zeta == 1:
            A = F_N / self.k
            return A * math.exp(-self.omega_n * t_s)
        else:
            return F_N / self.k  # Overdamped: slow return to equilibrium

    def run_diagnostics(self, F_N=0.01, t_s=1.0):
        return {
            "Natural Frequency (rad/s)": round(self.omega_n, 3),
            "Critical Damping Coefficient": round(self.c_critical, 3),
            "Damping Ratio (ζ)": round(self.zeta, 3),
            "Response Type": self.calculate_response_type(),
            "Displacement at t=1s (m)": round(self.calculate_displacement(F_N, t_s), 6)
        }

    def narrate(self, message):
        if self.commentary_mode:
            print(f"[Vibration Commentary] {message}")

    def log_status(self, message):
        self.status_log.append(message)

    def initialize(self):
        self.log_status("Vibration Damping Base initialized.")
        response = self.calculate_response_type()
        self.narrate(f"Oscillations suppressed. System is {response.lower()} and stable.")

