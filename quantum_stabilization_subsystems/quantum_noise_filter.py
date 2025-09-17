# quantum_stabilization_subsystems/quantum_noise_filter.py

import random
import math

class QuantumNoiseFilter:
    def __init__(self, signal_amplitude=1.0, noise_amplitude=0.05, fidelity_threshold=0.95):
        self.signal = signal_amplitude
        self.noise = noise_amplitude
        self.threshold = fidelity_threshold

        self.commentary_mode = True
        self.status_log = []
        self.fault_code = None

    # ┌────────────────────────────────────────────┐
    # │ Noise Suppression & Fidelity Logic         │
    # └────────────────────────────────────────────┘

    def calculate_fidelity(self):
        # Fidelity = signal² / (signal² + noise²)
        fidelity = self.signal**2 / (self.signal**2 + self.noise**2)
        return round(fidelity, 6)

    def simulate_environmental_noise(self):
        # Simulate drift in noise amplitude
        drift = random.uniform(-0.02, 0.02)
        self.noise = max(0.001, self.noise + drift)

    def run_diagnostics(self):
        self.simulate_environmental_noise()
        fidelity = self.calculate_fidelity()
        if fidelity < self.threshold:
            self.fault_code = "NOISE-001: Quantum fidelity below threshold"
        else:
            self.fault_code = None

        return {
            "Signal Amplitude": round(self.signal, 4),
            "Noise Amplitude": round(self.noise, 4),
            "Quantum Fidelity": fidelity,
            "Fidelity Threshold": self.threshold,
            "Fault Code": self.fault_code or "None"
        }

    # ┌────────────────────────────────────────────┐
    # │ Commentary & Logging                       │
    # └────────────────────────────────────────────┘

    def narrate(self, message):
        if self.commentary_mode:
            print(f"[QuantumNoise Commentary] {message}")

    def log_status(self, message):
        self.status_log.append(message)

    def initialize(self):
        self.log_status("Quantum Noise Filter initialized.")
        self.narrate("Signal clarity aligned. Decoherence suppression active.")

