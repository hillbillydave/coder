import sys
import random
import math
import datetime
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QGridLayout, QPushButton, QHBoxLayout, QProgressBar, QApplication, QGroupBox, QTabWidget, QCheckBox
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtGui import QPen, QColor

class MockWorker:
    def __init__(self, config=None, queue=None):
        self.name = "MockEngineeringWorker"
        self.warp_factor = 0.0
        self.config = config or {}
        self.shared_data_queue = queue
        # Initialize particle selection
        self.particle_selection = {name: False for name in PARTICLES}
        # Initialize all tunable variables
        self.injection_rate = 0.3
        self.warp_field_strength = 50.0
        self.antimatter_flow_rate = 0.2
        self.dilithium_alignment = 95.0
        self.coolant_flow = 10.0
        self.magnetic_confinement = 90.0
        self.power_output = 1000.0
        self.quantum_phase_variance = 90.0
        self.stabilization_field = 1.0
        self.entanglement_resonance = 300.0
        self.boot_sequence_timing = 0.5
        self.quantum_init_energy = 10.0
        self.quantum_core_angle = 2.5
        self.quantum_core_offset = 0.05
        self.coherence_field_strength = 1.0
        self.coherence_stability = 95.0
        self.emitter_angle = 5.0
        self.emitter_offset = 0.025
        self.entanglement_coupling = 90.0
        self.entanglement_node_angle = 7.5
        self.node_offset = 0.01
        self.noise_suppression = 25.0
        self.filter_bandwidth = 50.0
        self.filter_angle = 2.5
        self.orchestration_latency = 0.05
        self.subsystem_sync_accuracy = 98.0
        self.orchestrator_offset = 0.005
        self.telemetry_sampling_rate = 5.0
        self.telemetry_sensor_angle = 5.0
        self.recovery_cycle_duration = 3.0
        self.recovery_actuator_position = 0.025
        self.vacuum_integrity = 95.0
        self.isolation_energy = 30.0
        self.particle_contamination = 10.0
        self.boundary_curvature = 0.5
        self.geometric_stability = 95.0
        self.boundary_panel_angle = 5.0
        self.boundary_offset = 0.025
        self.cryogenic_temperature = 30.0
        self.cryo_coolant_flow = 10.0
        self.cryogenic_coil_angle = 2.5
        self.shielding_strength = 1.0
        self.shielding_coverage = 90.0
        self.shield_emitter_angle = 7.5
        self.shield_offset = 0.015
        self.isolation_sync_accuracy = 98.0
        self.isolation_orchestrator_angle = 2.5
        self.power_allocation = 1000.0
        self.power_conduit_angle = 5.0
        self.suite_activation = 50.0
        self.control_module_position = 0.01
        self.telemetry_update_rate = 5.0
        self.telemetry_sensor_angle_vacuum = 5.0
        self.thermal_dissipation = 300.0
        self.heat_sink_angle = 5.0
        self.isolation_chamber_angle = 2.5
        self.damping_coefficient = 0.5
        self.vibration_suppression = 50.0
        self.damper_offset = 0.025
        self.core_stability = 95.0
        self.energy_flux = 5.0
        self.core_alignment_angle = 2.5
        self.core_offset = 0.05
        self.exotic_matter_density = 0.5
        self.exotic_injection_rate = 0.05
        self.injector_angle = 5.0
        self.containment_strength = 90.0
        self.containment_emitter_angle = 7.5
        self.containment_efficiency = 95.0
        self.containment_sensor_angle = 5.0
        self.warp_field_geometry = 90.0
        self.geometry_projector_angle = 5.0
        self.projector_offset = 0.025
        self.field_oscillation = 5.0
        self.subspace_distortion = 0.5
        self.generator_coil_angle = 7.5
        self.stress_tolerance = 300.0
        self.stress_sensor_angle = 5.0
        self.field_sync_accuracy = 98.0
        self.field_orchestrator_angle = 2.5
        self.warp_telemetry_resolution = 0.5
        self.warp_telemetry_angle = 5.0
        print(f"[{self.name}] Initialized mock worker for Daisy's ship")

    def select_particle(self, particle_name, selected):
        if particle_name in self.particle_selection:
            self.particle_selection[particle_name] = selected
            return {"status": f"{particle_name} {'selected' if selected else 'deselected'}"}
        return {"error": f"Unknown particle: {particle_name}"}

    def simulate_particles(self):
        selected_particles = [PARTICLES[name] for name, selected in self.particle_selection.items() if selected]
        total_curvature = 0.0
        logs = []

    for p in selected_particles:
        mass_factor = p.mass_g_cm3 * self.exotic_injection_rate
        spin_factor = abs(math.sin(p.quantum_spin * math.pi))
        stability = p.stability_index

        curvature = (
            self.energy_flux * mass_factor * spin_factor * stability
        ) / (1 + (1 - self.containment_strength / 100.0))

        logs.append(f"→ {p.name}: curvature={curvature:.3f}")
        total_curvature += curvature

        distortion = math.log1p(total_curvature) * 0.8
        status = "Stable" if total_curvature > 1.0 else "Unstable"
        # Correct indentation starts here
           return {
               "timestamp": datetime.datetime.now().isoformat(),
               "curvature_index": round(total_curvature, 3),
               "subspace_distortion": round(distortion, 3),
               "containment_status": status,
               "particle_mix": [p.name for p in selected_particles],
               "logs": logs
        }
   
    def get_metrics(self):
        particle_telemetry, particle_logs = self.simulate_particles()
        metrics = {
        "engineering_data": {
            "warp_core": {
                "core_temperature": {"value": round(random.uniform(500.0, 700.0), 1), "unit": "°K"},
                "warp_field_strength": {"value": self.warp_field_strength, "unit": "%"},
                "status": "Stable" if self.warp_factor < 9.9 else "Critical"
            },
            "plasma_injectors": {
                "injection_rate": {"value": self.injection_rate, "unit": "mg/s"},
                "efficiency": {"value": round(random.uniform(80.0, 100.0), 1), "unit": "%"},  # Fixed
                "status": "Operational"
            },
            "antimatter_system": {
                "flow_rate": {"value": self.antimatter_flow_rate, "unit": "mg/s"},
                "status": "Stable"
            },
            "dilithium_matrix": {
                "alignment": {"value": self.dilithium_alignment, "unit": "%"},
                "status": "Aligned" if self.dilithium_alignment > 90.0 else "Misaligned"
            },
            "coolant_system": {
                "flow": {"value": self.coolant_flow, "unit": "L/min"},
                "status": "Operational"
            },
            "magnetic_confinement": {
                "strength": {"value": self.magnetic_confinement, "unit": "%"},
                "status": "Stable" if self.magnetic_confinement > 85.0 else "Unstable"
            },
            "power_system": {
                "output": {"value": self.power_output, "unit": "GW"},
                "status": "Nominal"
            },
            "quantum_stabilization": {
                "phase_variance": {"value": self.quantum_phase_variance, "unit": "%"},
                "stabilization_field": {"value": self.stabilization_field, "unit": "T"},
                "entanglement_resonance": {"value": self.entanglement_resonance, "unit": "Hz"},
                "boot_sequence_timing": {"value": self.boot_sequence_timing, "unit": "s"},
                "quantum_init_energy": {"value": self.quantum_init_energy, "unit": "MJ"},
                "quantum_core_angle": {"value": self.quantum_core_angle, "unit": "°"},
                "quantum_core_offset": {"value": self.quantum_core_offset, "unit": "m"},
                "coherence_field_strength": {"value": self.coherence_field_strength, "unit": "T"},
                "coherence_stability": {"value": self.coherence_stability, "unit": "%"},
                "emitter_angle": {"value": self.emitter_angle, "unit": "°"},
                "emitter_offset": {"value": self.emitter_offset, "unit": "m"},
                "entanglement_coupling": {"value": self.entanglement_coupling, "unit": "%"},
                "entanglement_node_angle": {"value": self.entanglement_node_angle, "unit": "°"},
                "node_offset": {"value": self.node_offset, "unit": "m"},
                "noise_suppression": {"value": self.noise_suppression, "unit": "dB"},
                "filter_bandwidth": {"value": self.filter_bandwidth, "unit": "kHz"},
                "filter_angle": {"value": self.filter_angle, "unit": "°"},
                "orchestration_latency": {"value": self.orchestration_latency, "unit": "s"},
                "subsystem_sync_accuracy": {"value": self.subsystem_sync_accuracy, "unit": "%"},
                "orchestrator_offset": {"value": self.orchestrator_offset, "unit": "m"},
                "telemetry_sampling_rate": {"value": self.telemetry_sampling_rate, "unit": "Hz"},
                "telemetry_sensor_angle": {"value": self.telemetry_sensor_angle, "unit": "°"},
                "recovery_cycle_duration": {"value": self.recovery_cycle_duration, "unit": "s"},
                "recovery_actuator_position": {"value": self.recovery_actuator_position, "unit": "m"},
                "status": "Stable" if self.quantum_phase_variance > 85.0 else "Unstable"
            },
            "vacuum_isolation": {
                "integrity": {"value": self.vacuum_integrity, "unit": "%"},
                "isolation_energy": {"value": self.isolation_energy, "unit": "MJ"},
                "particle_contamination": {"value": self.particle_contamination, "unit": "ppm"},
                "boundary_curvature": {"value": self.boundary_curvature, "unit": "units"},
                "geometric_stability": {"value": self.geometric_stability, "unit": "%"},
                "boundary_panel_angle": {"value": self.boundary_panel_angle, "unit": "°"},
                "boundary_offset": {"value": self.boundary_offset, "unit": "m"},
                "cryogenic_temperature": {"value": self.cryogenic_temperature, "unit": "K"},
                "cryo_coolant_flow": {"value": self.cryo_coolant_flow, "unit": "L/min"},
                "cryogenic_coil_angle": {"value": self.cryogenic_coil_angle, "unit": "°"},
                "shielding_strength": {"value": self.shielding_strength, "unit": "T"},
                "shielding_coverage": {"value": self.shielding_coverage, "unit": "%"},
                "shield_emitter_angle": {"value": self.shield_emitter_angle, "unit": "°"},
                "shield_offset": {"value": self.shield_offset, "unit": "m"},
                "isolation_sync_accuracy": {"value": self.isolation_sync_accuracy, "unit": "%"},
                "isolation_orchestrator_angle": {"value": self.isolation_orchestrator_angle, "unit": "°"},
                "power_allocation": {"value": self.power_allocation, "unit": "W"},
                "power_conduit_angle": {"value": self.power_conduit_angle, "unit": "°"},
                "suite_activation": {"value": self.suite_activation, "unit": "%"},
                "control_module_position": {"value": self.control_module_position, "unit": "m"},
                "telemetry_update_rate": {"value": self.telemetry_update_rate, "unit": "Hz"},
                "telemetry_sensor_angle_vacuum": {"value": self.telemetry_sensor_angle_vacuum, "unit": "°"},
                "thermal_dissipation": {"value": self.thermal_dissipation, "unit": "W/m²"},
                "heat_sink_angle": {"value": self.heat_sink_angle, "unit": "°"},
                "isolation_chamber_angle": {"value": self.isolation_chamber_angle, "unit": "°"},
                "damping_coefficient": {"value": self.damping_coefficient, "unit": ""},
                "vibration_suppression": {"value": self.vibration_suppression, "unit": "Hz"},
                "damper_offset": {"value": self.damper_offset, "unit": "m"},
                "status": "Sealed" if self.vacuum_integrity > 90.0 else "Compromised"
            },
            "warp_field": {
                "geometry": {"value": self.warp_field_geometry, "unit": "%"},
                "oscillation_frequency": {"value": self.field_oscillation, "unit": "kHz"},
                "subspace_distortion": {"value": self.subspace_distortion, "unit": "au"},
                "core_stability": {"value": self.core_stability, "unit": "%"},
                "energy_flux": {"value": self.energy_flux, "unit": "GW"},
                "core_alignment_angle": {"value": self.core_alignment_angle, "unit": "°"},
                "core_offset": {"value": self.core_offset, "unit": "m"},
                "exotic_matter_density": {"value": self.exotic_matter_density, "unit": "g/cm³"},
                "exotic_injection_rate": {"value": self.exotic_injection_rate, "unit": "mg/s"},
                "injector_angle": {"value": self.injector_angle, "unit": "°"},
                "containment_strength": {"value": self.containment_strength, "unit": "%"},
                "containment_emitter_angle": {"value": self.containment_emitter_angle, "unit": "°"},
                "containment_efficiency": {"value": self.containment_efficiency, "unit": "%"},
                "containment_sensor_angle": {"value": self.containment_sensor_angle, "unit": "°"},
                "geometry_projector_angle": {"value": self.geometry_projector_angle, "unit": "°"},
                "projector_offset": {"value": self.projector_offset, "unit": "m"},
                "stress_tolerance": {"value": self.stress_tolerance, "unit": "MPa"},
                "stress_sensor_angle": {"value": self.stress_sensor_angle, "unit": "°"},
                "field_sync_accuracy": {"value": self.field_sync_accuracy, "unit": "%"},
                "field_orchestrator_angle": {"value": self.field_orchestrator_angle, "unit": "°"},
                "telemetry_resolution": {"value": self.warp_telemetry_resolution, "unit": "au"},
                "warp_telemetry_angle": {"value": self.warp_telemetry_angle, "unit": "°"},
                "curvature_index": {"value": particle_telemetry["curvature_index"], "unit": ""},
                "particle_status": {"value": particle_telemetry["containment_status"], "unit": ""},
                "particle_mix": {"value": particle_telemetry["particle_mix"], "unit": ""},
                "status": "Coherent" if self.warp_field_geometry > 85.0 else "Disrupted"
            },
            "propulsion_data": {
                "warp_speed": {"value": self.warp_factor, "unit": "Warp Factor"}
            }
        }
    }
    if self.shared_data_queue:
        self.shared_data_queue.put({"type": "DAISY_ENGINEERING_METRICS", "payload": metrics})
        print(f"[{self.name}] Sent metrics to shared_data_queue")
    return metrics, particle_logs
    def _execute_command(self, command, args):
        commands = {
            "status": lambda: {"subsystem": "all", "status": "Online"},
            "metrics": self.get_metrics,
            "engage_warp": self._engage_warp,
            "select_particle": self.select_particle,
            "adjust_injectors": self._adjust_injectors,
            "adjust_coils": self._adjust_coils,
            "adjust_antimatter": self._adjust_antimatter,
            "adjust_crystals": self._adjust_crystals,
            "adjust_coolant": self._adjust_coolant,
            "adjust_confinement": self._adjust_confinement,
            "adjust_power": self._adjust_power,
            "adjust_quantum_phase": self._adjust_quantum_phase,
            "adjust_stabilization_field": self._adjust_stabilization_field,
            "adjust_entanglement": self._adjust_entanglement,
            "adjust_boot_timing": self._adjust_boot_timing,
            "adjust_quantum_init_energy": self._adjust_quantum_init_energy,
            "adjust_quantum_core_angle": self._adjust_quantum_core_angle,
            "adjust_quantum_core_offset": self._adjust_quantum_core_offset,
            "adjust_coherence_strength": self._adjust_coherence_strength,
            "adjust_coherence_stability": self._adjust_coherence_stability,
            "adjust_emitter_angle": self._adjust_emitter_angle,
            "adjust_emitter_offset": self._adjust_emitter_offset,
            "adjust_entanglement_coupling": self._adjust_entanglement_coupling,
            "adjust_entanglement_node_angle": self._adjust_entanglement_node_angle,
            "adjust_node_offset": self._adjust_node_offset,
            "adjust_noise_suppression": self._adjust_noise_suppression,
            "adjust_filter_bandwidth": self._adjust_filter_bandwidth,
            "adjust_filter_angle": self._adjust_filter_angle,
            "adjust_orchestration_latency": self._adjust_orchestration_latency,
            "adjust_subsystem_sync": self._adjust_subsystem_sync,
            "adjust_orchestrator_offset": self._adjust_orchestrator_offset,
            "adjust_telemetry_sampling": self._adjust_telemetry_sampling,
            "adjust_telemetry_sensor_angle": self._adjust_telemetry_sensor_angle,
            "adjust_recovery_cycle": self._adjust_recovery_cycle,
            "adjust_recovery_actuator_position": self._adjust_recovery_actuator_position,
            "adjust_vacuum_integrity": self._adjust_vacuum_integrity,
            "adjust_isolation_energy": self._adjust_isolation_energy,
            "adjust_contamination": self._adjust_contamination,
            "adjust_boundary_curvature": self._adjust_boundary_curvature,
            "adjust_geometric_stability": self._adjust_geometric_stability,
            "adjust_boundary_panel_angle": self._adjust_boundary_panel_angle,
            "adjust_boundary_offset": self._adjust_boundary_offset,
            "adjust_cryogenic_temperature": self._adjust_cryogenic_temperature,
            "adjust_cryo_coolant_flow": self._adjust_cryo_coolant_flow,
            "adjust_cryogenic_coil_angle": self._adjust_cryogenic_coil_angle,
            "adjust_shielding_strength": self._adjust_shielding_strength,
            "adjust_shielding_coverage": self._adjust_shielding_coverage,
            "adjust_shield_emitter_angle": self._adjust_shield_emitter_angle,
            "adjust_shield_offset": self._adjust_shield_offset,
            "adjust_isolation_sync": self._adjust_isolation_sync,
            "adjust_isolation_orchestrator_angle": self._adjust_isolation_orchestrator_angle,
            "adjust_power_allocation": self._adjust_power_allocation,
            "adjust_power_conduit_angle": self._adjust_power_conduit_angle,
            "adjust_suite_activation": self._adjust_suite_activation,
            "adjust_control_module_position": self._adjust_control_module_position,
            "adjust_telemetry_update": self._adjust_telemetry_update,
            "adjust_telemetry_sensor_angle_vacuum": self._adjust_telemetry_sensor_angle_vacuum,
            "adjust_thermal_dissipation": self._adjust_thermal_dissipation,
            "adjust_heat_sink_angle": self._adjust_heat_sink_angle,
            "adjust_isolation_chamber_angle": self._adjust_isolation_chamber_angle,
            "adjust_damping_coefficient": self._adjust_damping_coefficient,
            "adjust_vibration_suppression": self._adjust_vibration_suppression,
            "adjust_damper_offset": self._adjust_damper_offset,
            "adjust_core_stability": self._adjust_core_stability,
            "adjust_energy_flux": self._adjust_energy_flux,
            "adjust_core_alignment_angle": self._adjust_core_alignment_angle,
            "adjust_core_offset": self._adjust_core_offset,
            "adjust_exotic_density": self._adjust_exotic_density,
            "adjust_exotic_injection": self._adjust_exotic_injection,
            "adjust_injector_angle": self._adjust_injector_angle,
            "adjust_containment_strength": self._adjust_containment_strength,
            "adjust_containment_emitter_angle": self._adjust_containment_emitter_angle,
            "adjust_containment_efficiency": self._adjust_containment_efficiency,
            "adjust_containment_sensor_angle": self._adjust_containment_sensor_angle,
            "adjust_field_geometry": self._adjust_field_geometry,
            "adjust_geometry_projector_angle": self._adjust_geometry_projector_angle,
            "adjust_projector_offset": self._adjust_projector_offset,
            "adjust_oscillation": self._adjust_oscillation,
            "adjust_distortion": self._adjust_distortion,
            "adjust_stress_tolerance": self._adjust_stress_tolerance,
            "adjust_stress_sensor_angle": self._adjust_stress_sensor_angle,
            "adjust_field_sync": self._adjust_field_sync,
            "adjust_field_orchestrator_angle": self._adjust_field_orchestrator_angle,
            "adjust_warp_telemetry": self._adjust_warp_telemetry,
            "adjust_warp_telemetry_angle": self._adjust_warp_telemetry_angle
        }
        func = commands.get(command, lambda: {"error": f"Unknown command: {command}"})
        result = func() if not args else func(args[0])
        if "error" in result:
            print(f"[{self.name}] {result['error']}")
        return result

    def _engage_warp(self, warp_factor_str):
        try:
            warp_factor = float(warp_factor_str)
            if 0.0 <= warp_factor <= 9.9:
                self.warp_factor = warp_factor
                return {"status": f"Warp engaged at factor {warp_factor}"}
            return {"error": "Warp factor must be between 0.0 and 9.9"}
        except ValueError:
            return {"error": "Invalid warp factor"}

    def _adjust_injectors(self, rate_str):
        try:
            rate = float(rate_str)
            if 0.1 <= rate <= 0.5:
                self.injection_rate = rate
                return {"status": f"Plasma injectors adjusted to {rate} mg/s"}
            return {"error": "Injection rate must be between 0.1 and 0.5 mg/s"}
        except ValueError:
            return {"error": "Invalid injection rate"}

    def _adjust_coils(self, strength_str):
        try:
            strength = float(strength_str)
            if 0.0 <= strength <= 100.0:
                self.warp_field_strength = strength
                return {"status": f"Coils adjusted to {strength}%"}
            return {"error": "Coil strength must be between 0.0 and 100.0%"}
        except ValueError:
            return {"error": "Invalid coil strength"}

    def _adjust_antimatter(self, rate_str):
        try:
            rate = float(rate_str)
            if 0.1 <= rate <= 0.4:
                self.antimatter_flow_rate = rate
                return {"status": f"Antimatter flow adjusted to {rate} mg/s"}
            return {"error": "Antimatter flow rate must be between 0.1 and 0.4 mg/s"}
        except ValueError:
            return {"error": "Invalid antimatter flow rate"}

    def _adjust_crystals(self, alignment_str):
        try:
            alignment = float(alignment_str)
            if 80.0 <= alignment <= 100.0:
                self.dilithium_alignment = alignment
                return {"status": f"Dilithium alignment adjusted to {alignment}%"}
            return {"error": "Dilithium alignment must be between 80.0 and 100.0%"}
        except ValueError:
            return {"error": "Invalid dilithium alignment"}

    def _adjust_coolant(self, flow_str):
        try:
            flow = float(flow_str)
            if 5.0 <= flow <= 20.0:
                self.coolant_flow = flow
                return {"status": f"Coolant flow adjusted to {flow} L/min"}
            return {"error": "Coolant flow must be between 5.0 and 20.0 L/min"}
        except ValueError:
            return {"error": "Invalid coolant flow"}

    def _adjust_confinement(self, strength_str):
        try:
            strength = float(strength_str)
            if 70.0 <= strength <= 100.0:
                self.magnetic_confinement = strength
                return {"status": f"Magnetic confinement adjusted to {strength}%"}
            return {"error": "Magnetic confinement must be between 70.0 and 100.0%"}
        except ValueError:
            return {"error": "Invalid magnetic confinement strength"}

    def _adjust_power(self, output_str):
        try:
            output = float(output_str)
            if 500.0 <= output <= 2000.0:
                self.power_output = output
                return {"status": f"Power output adjusted to {output} GW"}
            return {"error": "Power output must be between 500.0 and 2000.0 GW"}
        except ValueError:
            return {"error": "Invalid power output"}

    def _adjust_quantum_phase(self, variance_str):
        try:
            variance = float(variance_str)
            if 80.0 <= variance <= 100.0:
                self.quantum_phase_variance = variance
                return {"status": f"Quantum phase variance adjusted to {variance}%"}
            return {"error": "Quantum phase variance must be between 80.0 and 100.0%"}
        except ValueError:
            return {"error": "Invalid quantum phase variance"}

    def _adjust_stabilization_field(self, field_str):
        try:
            field = float(field_str)
            if 0.5 <= field <= 2.0:
                self.stabilization_field = field
                return {"status": f"Stabilization field adjusted to {field} T"}
            return {"error": "Stabilization field must be between 0.5 and 2.0 T"}
        except ValueError:
            return {"error": "Invalid stabilization field"}

    def _adjust_entanglement(self, resonance_str):
        try:
            resonance = float(resonance_str)
            if 100.0 <= resonance <= 500.0:
                self.entanglement_resonance = resonance
                return {"status": f"Entanglement resonance adjusted to {resonance} Hz"}
            return {"error": "Entanglement resonance must be between 100.0 and 500.0 Hz"}
        except ValueError:
            return {"error": "Invalid entanglement resonance"}

    def _adjust_boot_timing(self, timing_str):
        try:
            timing = float(timing_str)
            if 0.1 <= timing <= 1.0:
                self.boot_sequence_timing = timing
                return {"status": f"Boot sequence timing adjusted to {timing} s"}
            return {"error": "Boot sequence timing must be between 0.1 and 1.0 s"}
        except ValueError:
            return {"error": "Invalid boot sequence timing"}

    def _adjust_quantum_init_energy(self, energy_str):
        try:
            energy = float(energy_str)
            if 5.0 <= energy <= 20.0:
                self.quantum_init_energy = energy
                return {"status": f"Quantum initialization energy adjusted to {energy} MJ"}
            return {"error": "Quantum initialization energy must be between 5.0 and 20.0 MJ"}
        except ValueError:
            return {"error": "Invalid quantum initialization energy"}

    def _adjust_quantum_core_angle(self, angle_str):
        try:
            angle = float(angle_str)
            if 0.0 <= angle <= 5.0:
                self.quantum_core_angle = angle
                return {"status": f"Quantum core angle adjusted to {angle}°"}
            return {"error": "Quantum core angle must be between 0.0 and 5.0°"}
        except ValueError:
            return {"error": "Invalid quantum core angle"}

    def _adjust_quantum_core_offset(self, offset_str):
        try:
            offset = float(offset_str)
            if 0.0 <= offset <= 0.1:
                self.quantum_core_offset = offset
                return {"status": f"Quantum core offset adjusted to {offset} m"}
            return {"error": "Quantum core offset must be between 0.0 and 0.1 m"}
        except ValueError:
            return {"error": "Invalid quantum core offset"}

    def _adjust_coherence_strength(self, strength_str):
        try:
            strength = float(strength_str)
            if 0.5 <= strength <= 2.0:
                self.coherence_field_strength = strength
                return {"status": f"Coherence field strength adjusted to {strength} T"}
            return {"error": "Coherence field strength must be between 0.5 and 2.0 T"}
        except ValueError:
            return {"error": "Invalid coherence field strength"}

    def _adjust_coherence_stability(self, stability_str):
        try:
            stability = float(stability_str)
            if 90.0 <= stability <= 100.0:
                self.coherence_stability = stability
                return {"status": f"Coherence stability adjusted to {stability}%"}
            return {"error": "Coherence stability must be between 90.0 and 100.0%"}
        except ValueError:
            return {"error": "Invalid coherence stability"}

    def _adjust_emitter_angle(self, angle_str):
        try:
            angle = float(angle_str)
            if 0.0 <= angle <= 10.0:
                self.emitter_angle = angle
                return {"status": f"Coherence emitter angle adjusted to {angle}°"}
            return {"error": "Coherence emitter angle must be between 0.0 and 10.0°"}
        except ValueError:
            return {"error": "Invalid coherence emitter angle"}

    def _adjust_emitter_offset(self, offset_str):
        try:
            offset = float(offset_str)
            if 0.0 <= offset <= 0.05:
                self.emitter_offset = offset
                return {"status": f"Coherence emitter offset adjusted to {offset} m"}
            return {"error": "Coherence emitter offset must be between 0.0 and 0.05 m"}
        except ValueError:
            return {"error": "Invalid coherence emitter offset"}

    def _adjust_entanglement_coupling(self, coupling_str):
        try:
            coupling = float(coupling_str)
            if 80.0 <= coupling <= 100.0:
                self.entanglement_coupling = coupling
                return {"status": f"Entanglement coupling adjusted to {coupling}%"}
            return {"error": "Entanglement coupling must be between 80.0 and 100.0%"}
        except ValueError:
            return {"error": "Invalid entanglement coupling"}

    def _adjust_entanglement_node_angle(self, angle_str):
        try:
            angle = float(angle_str)
            if 0.0 <= angle <= 15.0:
                self.entanglement_node_angle = angle
                return {"status": f"Entanglement node angle adjusted to {angle}°"}
            return {"error": "Entanglement node angle must be between 0.0 and 15.0°"}
        except ValueError:
            return {"error": "Invalid entanglement node angle"}

    def _adjust_node_offset(self, offset_str):
        try:
            offset = float(offset_str)
            if 0.0 <= offset <= 0.02:
                self.node_offset = offset
                return {"status": f"Entanglement node offset adjusted to {offset} m"}
            return {"error": "Entanglement node offset must be between 0.0 and 0.02 m"}
        except ValueError:
            return {"error": "Invalid entanglement node offset"}

    def _adjust_noise_suppression(self, suppression_str):
        try:
            suppression = float(suppression_str)
            if 0.0 <= suppression <= 50.0:
                self.noise_suppression = suppression
                return {"status": f"Noise suppression adjusted to {suppression} dB"}
            return {"error": "Noise suppression must be between 0.0 and 50.0 dB"}
        except ValueError:
            return {"error": "Invalid noise suppression"}

    def _adjust_filter_bandwidth(self, bandwidth_str):
        try:
            bandwidth = float(bandwidth_str)
            if 10.0 <= bandwidth <= 100.0:
                self.filter_bandwidth = bandwidth
                return {"status": f"Filter bandwidth adjusted to {bandwidth} kHz"}
            return {"error": "Filter bandwidth must be between 10.0 and 100.0 kHz"}
        except ValueError:
            return {"error": "Invalid filter bandwidth"}

    def _adjust_filter_angle(self, angle_str):
        try:
            angle = float(angle_str)
            if 0.0 <= angle <= 5.0:
                self.filter_angle = angle
                return {"status": f"Filter angle adjusted to {angle}°"}
            return {"error": "Filter angle must be between 0.0 and 5.0°"}
        except ValueError:
            return {"error": "Invalid filter angle"}

    def _adjust_orchestration_latency(self, latency_str):
        try:
            latency = float(latency_str)
            if 0.01 <= latency <= 0.1:
                self.orchestration_latency = latency
                return {"status": f"Orchestration latency adjusted to {latency} s"}
            return {"error": "Orchestration latency must be between 0.01 and 0.1 s"}
        except ValueError:
            return {"error": "Invalid orchestration latency"}

    def _adjust_subsystem_sync(self, sync_str):
        try:
            sync = float(sync_str)
            if 95.0 <= sync <= 100.0:
                self.subsystem_sync_accuracy = sync
                return {"status": f"Subsystem sync accuracy adjusted to {sync}%"}
            return {"error": "Subsystem sync accuracy must be between 95.0 and 100.0%"}
        except ValueError:
            return {"error": "Invalid subsystem sync accuracy"}

    def _adjust_orchestrator_offset(self, offset_str):
        try:
            offset = float(offset_str)
            if 0.0 <= offset <= 0.01:
                self.orchestrator_offset = offset
                return {"status": f"Orchestrator offset adjusted to {offset} m"}
            return {"error": "Orchestrator offset must be between 0.0 and 0.01 m"}
        except ValueError:
            return {"error": "Invalid orchestrator offset"}

    def _adjust_telemetry_sampling(self, rate_str):
        try:
            rate = float(rate_str)
            if 1.0 <= rate <= 10.0:
                self.telemetry_sampling_rate = rate
                return {"status": f"Telemetry sampling rate adjusted to {rate} Hz"}
            return {"error": "Telemetry sampling rate must be between 1.0 and 10.0 Hz"}
        except ValueError:
            return {"error": "Invalid telemetry sampling rate"}

    def _adjust_telemetry_sensor_angle(self, angle_str):
        try:
            angle = float(angle_str)
            if 0.0 <= angle <= 10.0:
                self.telemetry_sensor_angle = angle
                return {"status": f"Telemetry sensor angle adjusted to {angle}°"}
            return {"error": "Telemetry sensor angle must be between 0.0 and 10.0°"}
        except ValueError:
            return {"error": "Invalid telemetry sensor angle"}

    def _adjust_recovery_cycle(self, duration_str):
        try:
            duration = float(duration_str)
            if 1.0 <= duration <= 5.0:
                self.recovery_cycle_duration = duration
                return {"status": f"Recovery cycle duration adjusted to {duration} s"}
            return {"error": "Recovery cycle duration must be between 1.0 and 5.0 s"}
        except ValueError:
            return {"error": "Invalid recovery cycle duration"}

    def _adjust_recovery_actuator_position(self, position_str):
        try:
            position = float(position_str)
            if 0.0 <= position <= 0.05:
                self.recovery_actuator_position = position
                return {"status": f"Recovery actuator position adjusted to {position} m"}
            return {"error": "Recovery actuator position must be between 0.0 and 0.05 m"}
        except ValueError:
            return {"error": "Invalid recovery actuator position"}

    def _adjust_vacuum_integrity(self, integrity_str):
        try:
            integrity = float(integrity_str)
            if 90.0 <= integrity <= 100.0:
                self.vacuum_integrity = integrity
                return {"status": f"Vacuum integrity adjusted to {integrity}%"}
            return {"error": "Vacuum integrity must be between 90.0 and 100.0%"}
        except ValueError:
            return {"error": "Invalid vacuum integrity"}

    def _adjust_isolation_energy(self, energy_str):
        try:
            energy = float(energy_str)
            if 10.0 <= energy <= 50.0:
                self.isolation_energy = energy
                return {"status": f"Isolation energy adjusted to {energy} MJ"}
            return {"error": "Isolation energy must be between 10.0 and 50.0 MJ"}
        except ValueError:
            return {"error": "Invalid isolation energy"}

    def _adjust_contamination(self, contamination_str):
        try:
            contamination = float(contamination_str)
            if 0.0 <= contamination <= 100.0:
                self.particle_contamination = contamination
                return {"status": f"Particle contamination adjusted to {contamination} ppm"}
            return {"error": "Particle contamination must be between 0.0 and 100.0 ppm"}
        except ValueError:
            return {"error": "Invalid particle contamination"}

    def _adjust_boundary_curvature(self, curvature_str):
        try:
            curvature = float(curvature_str)
            if 0.1 <= curvature <= 1.0:
                self.boundary_curvature = curvature
                return {"status": f"Boundary curvature adjusted to {curvature} units"}
            return {"error": "Boundary curvature must be between 0.1 and 1.0 units"}
        except ValueError:
            return {"error": "Invalid boundary curvature"}

    def _adjust_geometric_stability(self, stability_str):
        try:
            stability = float(stability_str)
            if 90.0 <= stability <= 100.0:
                self.geometric_stability = stability
                return {"status": f"Geometric stability adjusted to {stability}%"}
            return {"error": "Geometric stability must be between 90.0 and 100.0%"}
        except ValueError:
            return {"error": "Invalid geometric stability"}

    def _adjust_boundary_panel_angle(self, angle_str):
        try:
            angle = float(angle_str)
            if 0.0 <= angle <= 10.0:
                self.boundary_panel_angle = angle
                return {"status": f"Boundary panel angle adjusted to {angle}°"}
            return {"error": "Boundary panel angle must be between 0.0 and 10.0°"}
        except ValueError:
            return {"error": "Invalid boundary panel angle"}

    def _adjust_boundary_offset(self, offset_str):
        try:
            offset = float(offset_str)
            if 0.0 <= offset <= 0.05:
                self.boundary_offset = offset
                return {"status": f"Boundary offset adjusted to {offset} m"}
            return {"error": "Boundary offset must be between 0.0 and 0.05 m"}
        except ValueError:
            return {"error": "Invalid boundary offset"}

    def _adjust_cryogenic_temperature(self, temp_str):
        try:
            temp = float(temp_str)
            if 10.0 <= temp <= 50.0:
                self.cryogenic_temperature = temp
                return {"status": f"Cryogenic temperature adjusted to {temp} K"}
            return {"error": "Cryogenic temperature must be between 10.0 and 50.0 K"}
        except ValueError:
            return {"error": "Invalid cryogenic temperature"}

    def _adjust_cryo_coolant_flow(self, flow_str):
        try:
            flow = float(flow_str)
            if 5.0 <= flow <= 20.0:
                self.cryo_coolant_flow = flow
                return {"status": f"Cryogenic coolant flow adjusted to {flow} L/min"}
            return {"error": "Cryogenic coolant flow must be between 5.0 and 20.0 L/min"}
        except ValueError:
            return {"error": "Invalid cryogenic coolant flow"}

    def _adjust_cryogenic_coil_angle(self, angle_str):
        try:
            angle = float(angle_str)
            if 0.0 <= angle <= 5.0:
                self.cryogenic_coil_angle = angle
                return {"status": f"Cryogenic coil angle adjusted to {angle}°"}
            return {"error": "Cryogenic coil angle must be between 0.0 and 5.0°"}
        except ValueError:
            return {"error": "Invalid cryogenic coil angle"}

    def _adjust_shielding_strength(self, strength_str):
        try:
            strength = float(strength_str)
            if 0.5 <= strength <= 2.0:
                self.shielding_strength = strength
                return {"status": f"Shielding strength adjusted to {strength} T"}
            return {"error": "Shielding strength must be between 0.5 and 2.0 T"}
        except ValueError:
            return {"error": "Invalid shielding strength"}

    def _adjust_shielding_coverage(self, coverage_str):
        try:
            coverage = float(coverage_str)
            if 85.0 <= coverage <= 100.0:
                self.shielding_coverage = coverage
                return {"status": f"Shielding coverage adjusted to {coverage}%"}
            return {"error": "Shielding coverage must be between 85.0 and 100.0%"}
        except ValueError:
            return {"error": "Invalid shielding coverage"}

    def _adjust_shield_emitter_angle(self, angle_str):
        try:
            angle = float(angle_str)
            if 0.0 <= angle <= 15.0:
                self.shield_emitter_angle = angle
                return {"status": f"Shield emitter angle adjusted to {angle}°"}
            return {"error": "Shield emitter angle must be between 0.0 and 15.0°"}
        except ValueError:
            return {"error": "Invalid shield emitter angle"}

    def _adjust_shield_offset(self, offset_str):
        try:
            offset = float(offset_str)
            if 0.0 <= offset <= 0.03:
                self.shield_offset = offset
                return {"status": f"Shield offset adjusted to {offset} m"}
            return {"error": "Shield offset must be between 0.0 and 0.03 m"}
        except ValueError:
            return {"error": "Invalid shield offset"}

    def _adjust_isolation_sync(self, sync_str):
        try:
            sync = float(sync_str)
            if 95.0 <= sync <= 100.0:
                self.isolation_sync_accuracy = sync
                return {"status": f"Isolation sync accuracy adjusted to {sync}%"}
            return {"error": "Isolation sync accuracy must be between 95.0 and 100.0%"}
        except ValueError:
            return {"error": "Invalid isolation sync accuracy"}

    def _adjust_isolation_orchestrator_angle(self, angle_str):
        try:
            angle = float(angle_str)
            if 0.0 <= angle <= 5.0:
                self.isolation_orchestrator_angle = angle
                return {"status": f"Isolation orchestrator angle adjusted to {angle}°"}
            return {"error": "Isolation orchestrator angle must be between 0.0 and 5.0°"}
        except ValueError:
            return {"error": "Invalid isolation orchestrator angle"}

    def _adjust_power_allocation(self, allocation_str):
        try:
            allocation = float(allocation_str)
            if 500.0 <= allocation <= 2000.0:
                self.power_allocation = allocation
                return {"status": f"Power allocation adjusted to {allocation} W"}
            return {"error": "Power allocation must be between 500.0 and 2000.0 W"}
        except ValueError:
            return {"error": "Invalid power allocation"}

    def _adjust_power_conduit_angle(self, angle_str):
        try:
            angle = float(angle_str)
            if 0.0 <= angle <= 10.0:
                self.power_conduit_angle = angle
                return {"status": f"Power conduit angle adjusted to {angle}°"}
            return {"error": "Power conduit angle must be between 0.0 and 10.0°"}
        except ValueError:
            return {"error": "Invalid power conduit angle"}

    def _adjust_suite_activation(self, activation_str):
        try:
            activation = float(activation_str)
            if 0.0 <= activation <= 100.0:
                self.suite_activation = activation
                return {"status": f"Suite activation adjusted to {activation}%"}
            return {"error": "Suite activation must be between 0.0 and 100.0%"}
        except ValueError:
            return {"error": "Invalid suite activation"}

    def _adjust_control_module_position(self, position_str):
        try:
            position = float(position_str)
            if 0.0 <= position <= 0.02:
                self.control_module_position = position
                return {"status": f"Control module position adjusted to {position} m"}
            return {"error": "Control module position must be between 0.0 and 0.02 m"}
        except ValueError:
            return {"error": "Invalid control module position"}

    def _adjust_telemetry_update(self, rate_str):
        try:
            rate = float(rate_str)
            if 1.0 <= rate <= 10.0:
                self.telemetry_update_rate = rate
                return {"status": f"Telemetry update rate adjusted to {rate} Hz"}
            return {"error": "Telemetry update rate must be between 1.0 and 10.0 Hz"}
        except ValueError:
            return {"error": "Invalid telemetry update rate"}

    def _adjust_telemetry_sensor_angle_vacuum(self, angle_str):
        try:
            angle = float(angle_str)
            if 0.0 <= angle <= 10.0:
                self.telemetry_sensor_angle_vacuum = angle
                return {"status": f"Vacuum telemetry sensor angle adjusted to {angle}°"}
            return {"error": "Vacuum telemetry sensor angle must be between 0.0 and 10.0°"}
        except ValueError:
            return {"error": "Invalid vacuum telemetry sensor angle"}

    def _adjust_thermal_dissipation(self, dissipation_str):
        try:
            dissipation = float(dissipation_str)
            if 100.0 <= dissipation <= 500.0:
                self.thermal_dissipation = dissipation
                return {"status": f"Thermal dissipation adjusted to {dissipation} W/m²"}
            return {"error": "Thermal dissipation must be between 100.0 and 500.0 W/m²"}
        except ValueError:
            return {"error": "Invalid thermal dissipation"}

    def _adjust_heat_sink_angle(self, angle_str):
        try:
            angle = float(angle_str)
            if 0.0 <= angle <= 10.0:
                self.heat_sink_angle = angle
                return {"status": f"Heat sink angle adjusted to {angle}°"}
            return {"error": "Heat sink angle must be between 0.0 and 10.0°"}
        except ValueError:
            return {"error": "Invalid heat sink angle"}

    def _adjust_isolation_chamber_angle(self, angle_str):
        try:
            angle = float(angle_str)
            if 0.0 <= angle <= 5.0:
                self.isolation_chamber_angle = angle
                return {"status": f"Isolation chamber angle adjusted to {angle}°"}
            return {"error": "Isolation chamber angle must be between 0.0 and 5.0°"}
        except ValueError:
            return {"error": "Invalid isolation chamber angle"}

    def _adjust_damping_coefficient(self, coefficient_str):
        try:
            coefficient = float(coefficient_str)
            if 0.1 <= coefficient <= 1.0:
                self.damping_coefficient = coefficient
                return {"status": f"Damping coefficient adjusted to {coefficient}"}
            return {"error": "Damping coefficient must be between 0.1 and 1.0"}
        except ValueError:
            return {"error": "Invalid damping coefficient"}

    def _adjust_vibration_suppression(self, suppression_str):
        try:
            suppression = float(suppression_str)
            if 10.0 <= suppression <= 100.0:
                self.vibration_suppression = suppression
                return {"status": f"Vibration suppression adjusted to {suppression} Hz"}
            return {"error": "Vibration suppression must be between 10.0 and 100.0 Hz"}
        except ValueError:
            return {"error": "Invalid vibration suppression"}

    def _adjust_damper_offset(self, offset_str):
        try:
            offset = float(offset_str)
            if 0.0 <= offset <= 0.05:
                self.damper_offset = offset
                return {"status": f"Damper offset adjusted to {offset} m"}
            return {"error": "Damper offset must be between 0.0 and 0.05 m"}
        except ValueError:
            return {"error": "Invalid damper offset"}

    def _adjust_core_stability(self, stability_str):
        try:
            stability = float(stability_str)
            if 90.0 <= stability <= 100.0:
                self.core_stability = stability
                return {"status": f"Core stability adjusted to {stability}%"}
            return {"error": "Core stability must be between 90.0 and 100.0%"}
        except ValueError:
            return {"error": "Invalid core stability"}

    def _adjust_energy_flux(self, flux_str):
        try:
            flux = float(flux_str)
            if 1.0 <= flux <= 10.0:
                self.energy_flux = flux
                return {"status": f"Core energy adjusted to {flux} GW"}
            return {"error": "Core energy must be between 1.0 and 10.0 GW"}
        except ValueError:
            return {"error": "Invalid core energy"}

    def _adjust_core_alignment_angle(self, angle_str):
        try:
            angle = float(angle_str)
            if 0.0 <= angle <= 5.0:
                self.core_alignment_angle = angle
                return {"status": f"Core alignment angle adjusted to {angle}°"}
            return {"error": "Core alignment angle must be between 0.0 and 5.0°"}
        except ValueError:
            return {"error": "Invalid core alignment angle"}

    def _adjust_core_offset(self, offset_str):
        try:
            offset = float(offset_str)
            if 0.0 <= offset <= 0.1:
                self.core_offset = offset
                return {"status": f"Core offset adjusted to {offset} m"}
            return {"error": "Core offset must be between 0.0 and 0.1 m"}
        except ValueError:
            return {"error": "Invalid core offset"}

    def _adjust_exotic_density(self, density_str):
        try:
            density = float(density_str)
            if 0.1 <= density <= 1.0:
                self.exotic_matter_density = density
                return {"status": f"Exotic matter density adjusted to {density} g/cm³"}
            return {"error": "Exotic matter density must be between 0.1 and 1.0 g/cm³"}
        except ValueError:
            return {"error": "Invalid exotic matter density"}

    def _adjust_exotic_injection(self, rate_str):
        try:
            rate = float(rate_str)
            if 0.01 <= rate <= 0.1:
                self.exotic_injection_rate = rate
                return {"status": f"Exotic injection rate adjusted to {rate} mg/s"}
            return {"error": "Exotic injection rate must be between 0.01 and 0.1 mg/s"}
        except ValueError:
            return {"error": "Invalid exotic injection rate"}

    def _adjust_injector_angle(self, angle_str):
        try:
            angle = float(angle_str)
            if 0.0 <= angle <= 10.0:
                self.injector_angle = angle
                return {"status": f"Injector angle adjusted to {angle}°"}
            return {"error": "Injector angle must be between 0.0 and 10.0°"}
        except ValueError:
            return {"error": "Invalid injector angle"}

    def _adjust_containment_strength(self, strength_str):
        try:
            strength = float(strength_str)
            if 85.0 <= strength <= 100.0:
                self.containment_strength = strength
                return {"status": f"Containment strength adjusted to {strength}%"}
            return {"error": "Containment strength must be between 85.0 and 100.0%"}
        except ValueError:
            return {"error": "Invalid containment strength"}

    def _adjust_containment_emitter_angle(self, angle_str):
        try:
            angle = float(angle_str)
            if 0.0 <= angle <= 15.0:
                self.containment_emitter_angle = angle
                return {"status": f"Containment emitter angle adjusted to {angle}°"}
            return {"error": "Containment emitter angle must be between 0.0 and 15.0°"}
        except ValueError:
            return {"error": "Invalid containment emitter angle"}

    def _adjust_containment_efficiency(self, efficiency_str):
        try:
            efficiency = float(efficiency_str)
            if 90.0 <= efficiency <= 100.0:
                self.containment_efficiency = efficiency
                return {"status": f"Containment efficiency adjusted to {efficiency}%"}
            return {"error": "Containment efficiency must be between 90.0 and 100.0%"}
        except ValueError:
            return {"error": "Invalid containment efficiency"}

    def _adjust_containment_sensor_angle(self, angle_str):
        try:
            angle = float(angle_str)
            if 0.0 <= angle <= 10.0:
                self.containment_sensor_angle = angle
                return {"status": f"Containment sensor angle adjusted to {angle}°"}
            return {"error": "Containment sensor angle must be between 0.0 and 10.0°"}
        except ValueError:
            return {"error": "Invalid containment sensor angle"}

    def _adjust_field_geometry(self, geometry_str):
        try:
            geometry = float(geometry_str)
            if 85.0 <= geometry <= 100.0:
                self.warp_field_geometry = geometry
                return {"status": f"Warp field geometry adjusted to {geometry}%"}
            return {"error": "Warp field geometry must be between 85.0 and 100.0%"}
        except ValueError:
            return {"error": "Invalid warp field geometry"}

    def _adjust_geometry_projector_angle(self, angle_str):
        try:
            angle = float(angle_str)
            if 0.0 <= angle <= 10.0:
                self.geometry_projector_angle = angle
                return {"status": f"Geometry projector angle adjusted to {angle}°"}
            return {"error": "Geometry projector angle must be between 0.0 and 10.0°"}
        except ValueError:
            return {"error": "Invalid geometry projector angle"}

    def _adjust_projector_offset(self, offset_str):
        try:
            offset = float(offset_str)
            if 0.0 <= offset <= 0.05:
                self.projector_offset = offset
                return {"status": f"Projector offset adjusted to {offset} m"}
            return {"error": "Projector offset must be between 0.0 and 0.05 m"}
        except ValueError:
            return {"error": "Invalid projector offset"}

    def _adjust_oscillation(self, frequency_str):
        try:
            frequency = float(frequency_str)
            if 1.0 <= frequency <= 10.0:
                self.field_oscillation = frequency
                return {"status": f"Field oscillation adjusted to {frequency} kHz"}
            return {"error": "Field oscillation frequency must be between 1.0 and 10.0 kHz"}
        except ValueError:
            return {"error": "Invalid field oscillation frequency"}

    def _adjust_distortion(self, distortion_str):
        try:
            distortion = float(distortion_str)
            if 0.1 <= distortion <= 1.0:
                self.subspace_distortion = distortion
                return {"status": f"Subspace distortion adjusted to {distortion} au"}
            return {"error": "Subspace distortion must be between 0.1 and 1.0 au"}
        except ValueError:
            return {"error": "Invalid subspace distortion"}

    def _adjust_stress_tolerance(self, tolerance_str):
        try:
            tolerance = float(tolerance_str)
            if 100.0 <= tolerance <= 500.0:
                self.stress_tolerance = tolerance
                return {"status": f"Stress tolerance adjusted to {tolerance} MPa"}
            return {"error": "Stress tolerance must be between 100.0 and 500.0 MPa"}
        except ValueError:
            return {"error": "Invalid stress tolerance"}

    def _adjust_stress_sensor_angle(self, angle_str):
        try:
            angle = float(angle_str)
            if 0.0 <= angle <= 10.0:
                self.stress_sensor_angle = angle
                return {"status": f"Stress sensor angle adjusted to {angle}°"}
            return {"error": "Stress sensor angle must be between 0.0 and 10.0°"}
        except ValueError:
            return {"error": "Invalid stress sensor angle"}

    def _adjust_field_sync(self, sync_str):
        try:
            sync = float(sync_str)
            if 95.0 <= sync <= 100.0:
                self.field_sync_accuracy = sync
                return {"status": f"Field sync accuracy adjusted to {sync}%"}
            return {"error": "Field sync accuracy must be between 95.0 and 100.0%"}
        except ValueError:
            return {"error": "Invalid field sync accuracy"}

    def _adjust_field_orchestrator_angle(self, angle_str):
        try:
            angle = float(angle_str)
            if 0.0 <= angle <= 5.0:
                self.field_orchestrator_angle = angle
                return {"status": f"Field orchestrator angle adjusted to {angle}°"}
            return {"error": "Field orchestrator angle must be between 0.0 and 5.0°"}
        except ValueError:
            return {"error": "Invalid field orchestrator angle"}

    def _adjust_warp_telemetry(self, resolution_str):
        try:
            resolution = float(resolution_str)
            if 0.1 <= resolution <= 1.0:
                self.warp_telemetry_resolution = resolution
                return {"status": f"Warp telemetry resolution adjusted to {resolution} au"}
            return {"error": "Warp telemetry resolution must be between 0.1 and 1.0 au"}
        except ValueError:
            return {"error": "Invalid warp telemetry resolution"}

    def _adjust_warp_telemetry_angle(self, angle_str):
        try:
            angle = float(angle_str)
            if 0.0 <= angle <= 10.0:
                self.warp_telemetry_angle = angle
                return {"status": f"Warp telemetry angle adjusted to {angle}°"}
            return {"error": "Warp telemetry angle must be between 0.0 and 10.0°"}
        except ValueError:
            return {"error": "Invalid warp telemetry angle"}

class DaisyEngineeringGUI(QWidget):
    def __init__(self, worker=None, registry=None, config=None):
        super().__init__()
        self.worker = worker or MockWorker()
        self.registry = registry or {}
        self.config = config or {"api_keys": {}, "workers": {}}
        self.time_elapsed = 0
        self.particle_checkboxes = {}
        self.init_ui()
        self.start_sequence()
        self.oldPos = self.pos()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def init_ui(self):
        self.setWindowTitle("Daisy’s Warp Engineering Console")
        layout = QVBoxLayout()

        # Title Bar
        title_bar = QHBoxLayout()
        title = QLabel("🌀 Daisy’s Warp Engineering Console")
        title.setStyleSheet("""
            color: #00FF00;
            font-size: 24px;
            font-weight: bold;
            background: rgba(0, 255, 0, 0.1);
            padding: 10px;
            border: 2px solid #00FF00;
            border-radius: 10px;
        """)
        title_bar.addWidget(title)
        title_bar.addStretch()
        close_btn = QPushButton("X")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 0, 0, 0.2);
                color: #FF0000;
                border: 2px solid #FF0000;
                border-radius: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(255, 0, 0, 0.4);
            }
        """)
        close_btn.clicked.connect(self.close)
        title_bar.addWidget(close_btn)
        layout.addLayout(title_bar)

        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #00FF00;
                background: rgba(0, 0, 0, 0.7);
                border-radius: 10px;
            }
            QTabBar::tab {
                background: rgba(0, 255, 0, 0.2);
                color: #00FF00;
                border: 1px solid #00FF00;
                padding: 5px;
                border-radius: 5px;
            }
            QTabBar::tab:selected {
                background: rgba(0, 255, 0, 0.4);
            }
        """)

        # Warp Core Tab
        warp_core_widget, warp_core_layout = self.create_tab("Warp Core Controls")
        self.add_particle_selection(warp_core_layout)
        self.add_metrics_display(warp_core_layout)
        warp_core_sliders = [
            ("Plasma Injector Rate (mg/s)", 10, 50, 30, self.adjust_injector, 100.0, "injector_slider"),
            ("Coil Pulse Rate (%)", 0, 1000, 500, self.adjust_coil, 10.0, "coil_slider"),
            ("Antimatter Flow Rate (mg/s)", 10, 40, 20, self.adjust_antimatter, 100.0, "antimatter_slider"),
            ("Dilithium Alignment (%)", 800, 1000, 950, self.adjust_crystals, 10.0, "crystal_slider"),
            ("Coolant Flow (L/min)", 50, 200, 100, self.adjust_coolant, 10.0, "coolant_slider"),
            ("Magnetic Confinement (%)", 700, 1000, 900, self.adjust_confinement, 10.0, "confinement_slider"),
            ("Power Output (GW)", 5000, 20000, 10000, self.adjust_power, 10.0, "power_slider")
        ]
        self.add_sliders(warp_core_layout, warp_core_sliders)
        tabs.addTab(warp_core_widget, "Warp Core")

        # Quantum Stabilization Tab
        quantum_widget, quantum_layout = self.create_tab("Quantum Stabilization Controls")
        quantum_sliders = [
            ("Quantum Phase Variance (%)", 800, 1000, 900, self.adjust_quantum_phase, 10.0, "quantum_phase_slider"),
            ("Stabilization Field (T)", 5, 20, 10, self.adjust_stabilization_field, 10.0, "stabilization_slider"),
            ("Entanglement Resonance (Hz)", 1000, 5000, 3000, self.adjust_entanglement, 10.0, "entanglement_slider"),
            ("Boot Sequence Timing (s)", 1, 10, 5, self.adjust_boot_timing, 10.0, "boot_timing_slider"),
            ("Quantum Init Energy (MJ)", 50, 200, 100, self.adjust_quantum_init_energy, 10.0, "quantum_init_energy_slider"),
            ("Quantum Core Angle (°)", 0, 50, 25, self.adjust_quantum_core_angle, 10.0, "quantum_core_angle_slider"),
            ("Quantum Core Offset (m)", 0, 10, 5, self.adjust_quantum_core_offset, 100.0, "quantum_core_offset_slider"),
            ("Coherence Field Strength (T)", 5, 20, 10, self.adjust_coherence_strength, 10.0, "coherence_strength_slider"),
            ("Coherence Stability (%)", 900, 1000, 950, self.adjust_coherence_stability, 10.0, "coherence_stability_slider"),
            ("Emitter Angle (°)", 0, 100, 50, self.adjust_emitter_angle, 10.0, "emitter_angle_slider"),
            ("Emitter Offset (m)", 0, 5, 2.5, self.adjust_emitter_offset, 100.0, "emitter_offset_slider"),
            ("Entanglement Coupling (%)", 800, 1000, 900, self.adjust_entanglement_coupling, 10.0, "entanglement_coupling_slider"),
            ("Entanglement Node Angle (°)", 0, 150, 75, self.adjust_entanglement_node_angle, 10.0, "entanglement_node_angle_slider"),
            ("Node Offset (m)", 0, 2, 1, self.adjust_node_offset, 100.0, "node_offset_slider"),
            ("Noise Suppression (dB)", 0, 500, 250, self.adjust_noise_suppression, 10.0, "noise_suppression_slider"),
            ("Filter Bandwidth (kHz)", 100, 1000, 500, self.adjust_filter_bandwidth, 10.0, "filter_bandwidth_slider"),
            ("Filter Angle (°)", 0, 50, 25, self.adjust_filter_angle, 10.0, "filter_angle_slider"),
            ("Orchestration Latency (s)", 1, 10, 5, self.adjust_orchestration_latency, 100.0, "orchestration_latency_slider"),
            ("Subsystem Sync Accuracy (%)", 950, 1000, 980, self.adjust_subsystem_sync, 10.0, "subsystem_sync_slider"),
            ("Orchestrator Offset (m)", 0, 1, 0.5, self.adjust_orchestrator_offset, 100.0, "orchestrator_offset_slider"),
            ("Telemetry Sampling Rate (Hz)", 10, 100, 50, self.adjust_telemetry_sampling, 10.0, "telemetry_sampling_slider"),
            ("Telemetry Sensor Angle (°)", 0, 100, 50, self.adjust_telemetry_sensor_angle, 10.0, "telemetry_sensor_angle_slider"),
            ("Recovery Cycle Duration (s)", 10, 50, 30, self.adjust_recovery_cycle, 10.0, "recovery_cycle_slider"),
            ("Recovery Actuator Position (m)", 0, 5, 2.5, self.adjust_recovery_actuator_position, 100.0, "recovery_actuator_position_slider")
        ]
        self.add_sliders(quantum_layout, quantum_sliders)
        tabs.addTab(quantum_widget, "Quantum Stabilization")

        # Vacuum Isolation Tab
        vacuum_sliders = [
    ("Boundary Panel Angle (°)", 0, 100, 50, self.adjust_boundary_panel_angle, 10.0, "boundary_panel_angle_slider"),
    ("Boundary Offset (m)", 0, 5, 2.5, self.adjust_boundary_offset, 100.0, "boundary_offset_slider"),
    ("Cryogenic Temperature (K)", 100, 500, 300, self.adjust_cryogenic_temperature, 10.0, "cryogenic_temperature_slider"),
    ("Cryogenic Coolant Flow (L/min)", 50, 200, 100, self.adjust_cryo_coolant_flow, 10.0, "cryo_coolant_flow_slider"),
    ("Cryogenic Coil Angle (°)", 0, 50, 25, self.adjust_cryogenic_coil_angle, 10.0, "cryogenic_coil_angle_slider"),
    ("Shielding Strength (T)", 5, 20, 10, self.adjust_shielding_strength, 10.0, "shielding_strength_slider"),
    ("Shielding Coverage (%)", 850, 1000, 900, self.adjust_shielding_coverage, 10.0, "shielding_coverage_slider"),
    ("Shield Emitter Angle (°)", 0, 150, 75, self.adjust_shield_emitter_angle, 10.0, "shield_emitter_angle_slider"),
    ("Shield Offset (m)", 0, 3, 1.5, self.adjust_shield_offset, 100.0, "shield_offset_slider"),
    ("Isolation Sync Accuracy (%)", 950, 1000, 980, self.adjust_isolation_sync, 10.0, "isolation_sync_slider"),
    ("Isolation Orchestrator Angle (°)", 0, 50, 25, self.adjust_isolation_orchestrator_angle, 10.0, "isolation_orchestrator_angle_slider"),
    ("Power Allocation (W)", 5000, 20000, 10000, self.adjust_power_allocation, 10.0, "power_allocation_slider"),
    ("Power Conduit Angle (°)", 0, 100, 50, self.adjust_power_conduit_angle, 10.0, "power_conduit_angle_slider"),
    ("Suite Activation (%)", 0, 1000, 500, self.adjust_suite_activation, 10.0, "suite_activation_slider"),
    ("Control Module Position (m)", 0, 2, 1, self.adjust_control_module_position, 100.0, "control_module_position_slider"),
    ("Telemetry Update Rate (Hz)", 10, 100, 50, self.adjust_telemetry_update, 10.0, "telemetry_update_slider"),
    ("Telemetry Sensor Angle Vacuum (°)", 0, 100, 50, self.adjust_telemetry_sensor_angle_vacuum, 10.0, "telemetry_sensor_angle_vacuum_slider"),
    ("Thermal Dissipation (W/m²)", 1000, 5000, 3000, self.adjust_thermal_dissipation, 10.0, "thermal_dissipation_slider"),
    ("Heat Sink Angle (°)", 0, 100, 50, self.adjust_heat_sink_angle, 10.0, "heat_sink_angle_slider"),
    ("Isolation Chamber Angle (°)", 0, 50, 25, self.adjust_isolation_chamber_angle, 10.0, "isolation_chamber_angle_slider"),
    ("Damping Coefficient", 1, 10, 5, self.adjust_damping_coefficient, 10.0, "damping_coefficient_slider"),
    ("Vibration Suppression (Hz)", 100, 1000, 500, self.adjust_vibration_suppression, 10.0, "vibration_suppression_slider"),
    ("Damper Offset (m)", 0, 5, 2.5, self.adjust_damper_offset, 100.0, "damper_offset_slider")
    ]
        self.add_sliders(vacuum_layout, vacuum_sliders)
        tabs.addTab(vacuum_widget, "Vacuum Isolation")

        layout.addWidget(tabs)
        self.setLayout(layout)

    def create_tab(self, title):
        widget = QWidget()
        layout = QGridLayout()
        group_box = QGroupBox(title)
        group_box.setStyleSheet("""
            QGroupBox {
                color: #00FF00;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #00FF00;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
                color: #00FF00;
            }
        """)
        group_box.setLayout(layout)
        widget_layout = QVBoxLayout()
        widget_layout.addWidget(group_box)
        widget.setLayout(widget_layout)
        return widget, layout

    def add_sliders(self, layout, sliders):
        for row, (label_text, min_val, max_val, default_val, callback, scale, obj_name) in enumerate(sliders):
            label = QLabel(label_text)
            label.setStyleSheet("color: #00FF00; font-size: 14px;")
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(min_val)
            slider.setMaximum(max_val)
            slider.setValue(default_val)
            slider.setObjectName(obj_name)
            slider.valueChanged.connect(lambda value, cb=callback, s=scale: cb(str(value / s)))
            value_label = QLabel(f"{default_val / scale:.2f}")
            value_label.setStyleSheet("color: #00FF00; font-size: 14px;")
            slider.valueChanged.connect(lambda value, vl=value_label, s=scale: vl.setText(f"{value / s:.2f}"))
            layout.addWidget(label, row, 0)
            layout.addWidget(slider, row, 1)
            layout.addWidget(value_label, row, 2)

    def add_particle_selection(self, layout):
        group_box = QGroupBox("Exotic Particle Selection")
        group_box.setStyleSheet("QGroupBox { color: #00FF00; font-size: 16px; border: 2px solid #00FF00; border-radius: 5px; }")
        particle_layout = QVBoxLayout()
        for name in PARTICLES:
            checkbox = QCheckBox(name)
            checkbox.setStyleSheet("color: #00FF00; font-size: 14px;")
            checkbox.stateChanged.connect(lambda state, n=name: self.worker.select_particle(n, state == Qt.Checked))
            self.particle_checkboxes[name] = checkbox
            particle_layout.addWidget(checkbox)
        group_box.setLayout(particle_layout)
        layout.addWidget(group_box)

    def add_metrics_display(self, layout):
        self.status_label = QLabel("Warp Core Status: Initializing")
        self.status_label.setStyleSheet("color: #00FF00; font-size: 14px;")
        layout.addWidget(self.status_label)
        self.chart = QChart()
        self.series = QLineSeries()
        self.chart.addSeries(self.series)
        self.axis_x = QValueAxis()
        self.axis_y = QValueAxis()
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)
        self.chart_view = QChartView(self.chart)
        self.chart_view.setStyleSheet("background: rgba(0, 0, 0, 0.7);")
        layout.addWidget(self.chart_view)

    def start_sequence(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(1000)

    def update_metrics(self):
        metrics, logs = self.worker.get_metrics()
        self.status_label.setText(f"Warp Core Status: {metrics['engineering_data']['warp_core']['status']}")
        curvature = metrics["engineering_data"]["warp_field"]["curvature_index"]["value"]
        self.series.append(self.time_elapsed, curvature)
        self.axis_x.setRange(0, self.time_elapsed + 1)
        self.axis_y.setRange(0, max(10, curvature * 1.2))
        self.time_elapsed += 1

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def adjust_injector(self, rate):
        self.worker.execute_task(["adjust_injectors", rate])

    def adjust_coil(self, strength):
        self.worker.execute_task(["adjust_coils", strength])

    def adjust_antimatter(self, rate):
        self.worker.execute_task(["adjust_antimatter", rate])

    def adjust_crystals(self, alignment):
        self.worker.execute_task(["adjust_crystals", alignment])

    def adjust_coolant(self, flow):
        self.worker.execute_task(["adjust_coolant", flow])

    def adjust_confinement(self, strength):
        self.worker.execute_task(["adjust_confinement", strength])

    def adjust_power(self, output):
        self.worker.execute_task(["adjust_power", output])

    def adjust_quantum_phase(self, variance):
        self.worker.execute_task(["adjust_quantum_phase", variance])

    def adjust_stabilization_field(self, field):
        self.worker.execute_task(["adjust_stabilization_field", field])

    def adjust_entanglement(self, resonance):
        self.worker.execute_task(["adjust_entanglement", resonance])

    def adjust_boot_timing(self, timing):
        self.worker.execute_task(["adjust_boot_timing", timing])

    def adjust_quantum_init_energy(self, energy):
        self.worker.execute_task(["adjust_quantum_init_energy", energy])

    def adjust_quantum_core_angle(self, angle):
        self.worker.execute_task(["adjust_quantum_core_angle", angle])

    def adjust_quantum_core_offset(self, offset):
        self.worker.execute_task(["adjust_quantum_core_offset", offset])

    def adjust_coherence_strength(self, strength):
        self.worker.execute_task(["adjust_coherence_strength", strength])

    def adjust_coherence_stability(self, stability):
        self.worker.execute_task(["adjust_coherence_stability", stability])

    def adjust_emitter_angle(self, angle):
        self.worker.execute_task(["adjust_emitter_angle", angle])

    def adjust_emitter_offset(self, offset):
        self.worker.execute_task(["adjust_emitter_offset", offset])

    def adjust_entanglement_coupling(self, coupling):
        self.worker.execute_task(["adjust_entanglement_coupling", coupling])

    def adjust_entanglement_node_angle(self, angle):
        self.worker.execute_task(["adjust_entanglement_node_angle", angle])

    def adjust_node_offset(self, offset):
        self.worker.execute_task(["adjust_node_offset", offset])

    def adjust_noise_suppression(self, suppression):
        self.worker.execute_task(["adjust_noise_suppression", suppression])

    def adjust_filter_bandwidth(self, bandwidth):
        self.worker.execute_task(["adjust_filter_bandwidth", bandwidth])

    def adjust_filter_angle(self, angle):
        self.worker.execute_task(["adjust_filter_angle", angle])

    def adjust_orchestration_latency(self, latency):
        self.worker.execute_task(["adjust_orchestration_latency", latency])

    def adjust_subsystem_sync(self, sync):
        self.worker.execute_task(["adjust_subsystem_sync", sync])

    def adjust_orchestrator_offset(self, offset):
        self.worker.execute_task(["adjust_orchestrator_offset", offset])

    def adjust_telemetry_sampling(self, rate):
        self.worker.execute_task(["adjust_telemetry_sampling", rate])

    def adjust_telemetry_sensor_angle(self, angle):
        self.worker.execute_task(["adjust_telemetry_sensor_angle", angle])

    def adjust_recovery_cycle(self, duration):
        self.worker.execute_task(["adjust_recovery_cycle", duration])

    def adjust_recovery_actuator_position(self, position):
        self.worker.execute_task(["adjust_recovery_actuator_position", position])

    def adjust_vacuum_integrity(self, integrity):
        self.worker.execute_task(["adjust_vacuum_integrity", integrity])

    def adjust_isolation_energy(self, energy):
        self.worker.execute_task(["adjust_isolation_energy", energy])

    def adjust_contamination(self, contamination):
        self.worker.execute_task(["adjust_contamination", contamination])

    def adjust_boundary_curvature(self, curvature):
        self.worker.execute_task(["adjust_boundary_curvature", curvature])

    def adjust_geometric_stability(self, stability):
        self.worker.execute_task(["adjust_geometric_stability", stability])

    def adjust_boundary_panel_angle(self, angle):
        self.worker.execute_task(["adjust_boundary_panel_angle", angle])

    def adjust_boundary_offset(self, offset):
        self.worker.execute_task(["adjust_boundary_offset", offset])

    def adjust_cryogenic_temperature(self, temp):
        self.worker.execute_task(["adjust_cryogenic_temperature", temp])

    def adjust_cryo_coolant_flow(self, flow):
        self.worker.execute_task(["adjust_cryo_coolant_flow", flow])

    def adjust_cryogenic_coil_angle(self, angle):
        self.worker.execute_task(["adjust_cryogenic_coil_angle", angle])

    def adjust_shielding_strength(self, strength):
        self.worker.execute_task(["adjust_shielding_strength", strength])

    def adjust_shielding_coverage(self, coverage):
        self.worker.execute_task(["adjust_shielding_coverage", coverage])

    def adjust_shield_emitter_angle(self, angle):
        self.worker.execute_task(["adjust_shield_emitter_angle", angle])

    def adjust_shield_offset(self, offset):
        self.worker.execute_task(["adjust_shield_offset", offset])

    def adjust_isolation_sync(self, sync):
        self.worker.execute_task(["adjust_isolation_sync", sync])

    def adjust_isolation_orchestrator_angle(self, angle):
        self.worker.execute_task(["adjust_isolation_orchestrator_angle", angle])

    def adjust_power_allocation(self, allocation):
        self.worker.execute_task(["adjust_power_allocation", allocation])

    def adjust_power_conduit_angle(self, angle):
        self.worker.execute_task(["adjust_power_conduit_angle", angle])

    def adjust_suite_activation(self, activation):
        self.worker.execute_task(["adjust_suite_activation", activation])

    def adjust_control_module_position(self, position):
        self.worker.execute_task(["adjust_control_module_position", position])

    def adjust_telemetry_update(self, rate):
        self.worker.execute_task(["adjust_telemetry_update", rate])

    def adjust_telemetry_sensor_angle_vacuum(self, angle):
        self.worker.execute_task(["adjust_telemetry_sensor_angle_vacuum", angle])

    def adjust_thermal_dissipation(self, dissipation):
        self.worker.execute_task(["adjust_thermal_dissipation", dissipation])

    def adjust_heat_sink_angle(self, angle):
        self.worker.execute_task(["adjust_heat_sink_angle", angle])

    def adjust_isolation_chamber_angle(self, angle):
        self.worker.execute_task(["adjust_isolation_chamber_angle", angle])

    def adjust_damping_coefficient(self, coefficient):
        self.worker.execute_task(["adjust_damping_coefficient", coefficient])

    def adjust_vibration_suppression(self, suppression):
        self.worker.execute_task(["adjust_vibration_suppression", suppression])

    def adjust_damper_offset(self, offset):
        self.worker.execute_task(["adjust_damper_offset", offset])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = DaisyEngineeringGUI()
    gui.show()
    sys.exit(app.exec_())
