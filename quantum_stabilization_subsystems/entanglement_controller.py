# quantum_stabilization_subsystems/entanglement_controller.py

import math
import random
import cmath

class EntanglementController:
    def __init__(self, alpha=1/math.sqrt(2), beta=1/math.sqrt(2)):
        # Quantum amplitudes for superposition
        self.alpha = complex(alpha)
        self.beta = complex(beta)
        self.normalize_state()

        self.commentary_mode = True
        self.status_log = []
        self.fault_code = None

    # ┌────────────────────────────────────────────┐
    # │ Quantum State Logic                        │
    # └────────────────────────────────────────────┘

    def normalize_state(self):
        norm = abs(self.alpha)**2 + abs(self.beta)**2
        if not math.isclose(norm, 1.0, rel_tol=1e-9):
            self.alpha /= cmath.sqrt(norm)
            self.beta /= cmath.sqrt(norm)

    def generate_bell_state(self):
        # Ψ⁺ = (|01⟩ + |10⟩) / √2
        return {
            "Bell State Ψ⁺": f"(1/√2) * (|01⟩ + |10⟩)",
            "Entangled": True
        }

    def is_separable(self):
        # Heuristic: if amplitudes are real and one is zero, it's separable
        return abs(self.alpha) == 1.0 or abs(self.beta) == 1.0

    def decoherence_index(self):
        # Simulate decoherence drift
        drift = random.uniform(0.0, 1.0)
        index = round(1 - drift, 6)
        if index < 0.5:
            self.fault_code = "ENT-001: Decoherence threshold breached"
        else:
            self.fault_code = None
        return index

    def run_diagnostics(self):
        return {
            "State Vector |ψ⟩": f"{self.alpha:.3f}|0⟩ + {self.beta:.3f}|1⟩",
            "Normalized": math.isclose(abs(self.alpha)**2 + abs(self.beta)**2, 1.0),
            "Separable": self.is_separable(),
            "Decoherence Index": self.decoherence_index(),
            "Bell State": self.generate_bell_state()["Bell State Ψ⁺"],
            "Fault Code": self.fault_code or "None"
        }

    # ┌────────────────────────────────────────────┐
    # │ Commentary & Logging                       │
    # └────────────────────────────────────────────┘

    def narrate(self, message):
        if self.commentary_mode:
            print(f"[Entanglement Commentary] {message}")

    def log_status(self, message):
        self.status_log.append(message)

    def initialize(self):
        self.log_status("Entanglement Controller initialized.")
        self.narrate("Quantum linkages established. Bell state coherence aligned.")

