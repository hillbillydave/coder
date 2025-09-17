# magnetic_shielding_subsystem.py

class MagneticShieldMonitor:
    def __init__(self, permeability_mu, wall_thickness_mm, diameter_cm, ambient_flux_mG):
        self.mu = permeability_mu
        self.d = wall_thickness_mm * 1e-3  # meters
        self.D = diameter_cm * 1e-2        # meters
        self.B_ambient = ambient_flux_mG   # milliGauss

        self.shielding_factor = None
        self.B_internal = None

        self.commentary_mode = True
        self.status_log = []

    # ┌────────────────────────────────────────────┐
    # │ Core Calculations                          │
    # └────────────────────────────────────────────┘

    def calculate_shielding_factor(self):
        self.shielding_factor = (self.mu * self.d) / self.D
        return self.shielding_factor

    def calculate_internal_flux(self):
        if self.shielding_factor is None:
            self.calculate_shielding_factor()
        self.B_internal = self.B_ambient / self.shielding_factor
        return self.B_internal

    def run_diagnostics(self):
        return {
            "Shielding Factor (S)": round(self.shielding_factor, 2),
            "Ambient Flux (mG)": round(self.B_ambient, 3),
            "Internal Flux (mG)": round(self.B_internal, 6)
        }

    def narrate(self, message):
        if self.commentary_mode:
            print(f"[Magnetic Commentary] {message}")

    def log_status(self, message):
        self.status_log.append(message)

    def initialize(self):
        self.calculate_shielding_factor()
        self.calculate_internal_flux()
        self.log_status("Magnetic Shield Monitor initialized.")
        self.narrate("Mu-metal field engaged. Ambient flux suppressed to safe levels.")

