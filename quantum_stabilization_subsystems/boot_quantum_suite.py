# boot_quantum_suite.py

from quantum_stabilization_subsystems.entanglement_controller import EntanglementController
from quantum_stabilization_subsystems.quantum_noise_filter import QuantumNoiseFilter
from quantum_stabilization_subsystems.coherence_field_generator import CoherenceFieldGenerator
from quantum_stabilization_subsystems.quantum_telemetry import QuantumTelemetry
from quantum_stabilization_subsystems.quantum_orchestrator import QuantumOrchestrator

from warp_field_subsystems.warp_field_generator import WarpFieldGenerator

from support_systems.subsystem_registry import SubsystemRegistry
from support_systems.recovery_script_library import RecoveryScriptLibrary
from support_systems.commentary_engine import CommentaryEngine

def boot_quantum_suite():
    print("🚀 Booting Quantum Stabilization + Warp Field Suite...\n")

    # Support systems
    registry = SubsystemRegistry()
    recovery = RecoveryScriptLibrary()
    commentary = CommentaryEngine()

    registry.initialize()
    recovery.initialize()
    commentary.initialize()

    # Quantum subsystems
    entangler = EntanglementController()
    noise_filter = QuantumNoiseFilter()
    coherence = CoherenceFieldGenerator()

    # Warp subsystem
    warp_field = WarpFieldGenerator(
        energy_density_Jm3=1e-10,
        bubble_radius_m=10.0,
        velocity_fraction_c=0.5
    )

    # Orchestrator
    orchestrator = QuantumOrchestrator(
        registry=registry,
        recovery_library=recovery,
        commentary_engine=commentary
    )

    # Register subsystems
    orchestrator.register("Entanglement", entangler, role="Quantum Linkage Architect", tone="entangled")
    orchestrator.register("NoiseFilter", noise_filter, role="Signal Guardian", tone="whispering")
    orchestrator.register("CoherenceField", coherence, role="Phase Sculptor", tone="resonant")
    orchestrator.register("WarpField", warp_field, role="Spacetime Sculptor", tone="stoic")

    # Initialize all
    orchestrator.initialize_all()

    # Telemetry
    telemetry = QuantumTelemetry()
    telemetry.register_subsystem("Entanglement", entangler.run_diagnostics)
    telemetry.register_subsystem("NoiseFilter", noise_filter.run_diagnostics)
    telemetry.register_subsystem("CoherenceField", coherence.run_diagnostics)
    telemetry.register_subsystem("WarpField", warp_field.run_diagnostics)

    print("\n📡 Quantum + Warp Telemetry Summary:")
    summary = telemetry.run_summary()
    for subsystem, diagnostics in summary["Telemetry Snapshot"].items():
        print(f"\n🔍 {subsystem} Diagnostics:")
        for key, value in diagnostics.items():
            print(f  "  {key}: {value}")

    print("\n✅ Boot sequence complete. All subsystems online.")

if __name__ == "__main__":
    boot_quantum_suite()

