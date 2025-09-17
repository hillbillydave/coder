# starship_suite.py

import tkinter as tk
from tkinter import ttk

# Import all subsystems
from vacuum_isolation_subsystem import VacuumIsolationModule
from cryogenic_control_subsystem import CryogenicControl
from vibration_damping_subsystem import VibrationDampingBase
from magnetic_shielding_subsystem import MagneticShieldMonitor
from boundary_geometry_subsystem import BoundaryGeometryController
from telemetry_aggregator import TelemetryAggregator
from orchestrator import SubsystemOrchestrator
from power_distribution_subsystem import PowerDistributionMonitor
from thermal_feedback_subsystem import ThermalFeedbackLoop
from fault_recovery_subsystem import FaultRecoveryEngine
from subsystem_registry import SubsystemRegistry

# ┌────────────────────────────────────────────┐
# │ Boot Sequence                              │
# └────────────────────────────────────────────┘

def boot_starship_suite():
    # Instantiate subsystems
    vacuum = VacuumIsolationModule(5.0, 50.0, 28.0, 1000.0, 20.0)
    cryo = CryogenicControl(2.0, 0.0005, 400, 1.0, 0.05, 3.0, 20.0)
    damping = VibrationDampingBase(2.0, 100.0, 28.3)
    shield = MagneticShieldMonitor(80000, 2.0, 10.0, 0.5)
    geometry = BoundaryGeometryController(0.5, 0.3, 0.2, 1e9)
    telemetry = TelemetryAggregator()
    power = PowerDistributionMonitor()
    thermal = ThermalFeedbackLoop()
    recovery = FaultRecoveryEngine()
    registry = SubsystemRegistry()
    orchestrator = SubsystemOrchestrator()

    # Register subsystems
    orchestrator.register("VacuumIsolation", vacuum)
    orchestrator.register("CryogenicControl", cryo)
    orchestrator.register("VibrationDamping", damping)
    orchestrator.register("MagneticShielding", shield)
    orchestrator.register("BoundaryGeometry", geometry)
    orchestrator.register("TelemetryAggregator", telemetry)

    power.register_subsystem("VacuumIsolation", 8.0)
    power.register_subsystem("CryogenicControl", 15.0)
    power.register_subsystem("MagneticShielding", 5.0)

    thermal.register_subsystem("VacuumIsolation", 20.0)
    thermal.register_subsystem("CryogenicControl", 3.0)
    thermal.register_subsystem("MagneticShielding", 18.5)

    recovery.register_recovery_script("CryogenicControl", lambda: print("[CryogenicControl] Rebooting cooling loop..."))

    registry.register("VacuumIsolation", role="Quantum Silence Generator", tone="stoic")
    registry.register("CryogenicControl", role="Entropy Suppressor", tone="whispering")
    registry.register("MagneticShielding", role="Field Guardian", tone="vigilant")

    # Initialize everything
    orchestrator.initialize()
    power.initialize()
    thermal.initialize()
    recovery.initialize()
    registry.initialize()
    vacuum.initialize()

    return orchestrator, power, thermal, recovery, registry, vacuum

# ┌────────────────────────────────────────────┐
# │ GUI Overlay                                │
# └────────────────────────────────────────────┘

def launch_gui(orchestrator, power, thermal, recovery, vacuum):
    root = tk.Tk()
    root.title("Starship Engineering Suite")
    root.geometry("900x600")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

    tabs = {}

    def add_tab(title, data_func):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=title)
        tree = ttk.Treeview(frame, columns=("Key", "Value"), show="headings")
        tree.heading("Key", text="Metric")
        tree.heading("Value", text="Value")
        tree.pack(expand=True, fill="both")
        tabs[title] = (tree, data_func)

    add_tab("Subsystem Diagnostics", orchestrator.collect_ensemble_diagnostics)
    add_tab("Power Grid", power.run_diagnostics)
    add_tab("Thermal Map", thermal.run_diagnostics)
    add_tab("Fault Log", lambda: {
        f["subsystem"]: {"Fault": f["description"]} for f in recovery.get_fault_log()
    })

    def refresh():
        vacuum.monitor_faults(recovery)
        for title, (tree, data_func) in tabs.items():
            tree.delete(*tree.get_children())
            data = data_func()
            for subsystem, metrics in data.items():
                for k, v in metrics.items():
                    tree.insert("", "end", values=(f"{subsystem} - {k}", v))
        root.after(2000, refresh)

    refresh()
    root.mainloop()

# ┌────────────────────────────────────────────┐
# │ CLI Fallback                               │
# └────────────────────────────────────────────┘

def cli_dashboard(orchestrator, power, thermal, recovery):
    print("\n🧠 Ensemble Diagnostics Snapshot:")
    for name, data in orchestrator.collect_ensemble_diagnostics().items():
        print(f"\nSubsystem: {name}")
        for k, v in data.items():
            print(f"  {k}: {v}")

    print("\n🔌 Power Grid Snapshot:")
    for name, data in power.run_diagnostics().items():
        print(f"\nSubsystem: {name}")
        for k, v in data.items():
            print(f"  {k}: {v}")

    print("\n🌡️ Thermal Stability Snapshot:")
    thermal_diag = thermal.run_diagnostics()
    for k, v in thermal_diag.items():
        print(f"{k}: {v}")

    print("\n🛠 Fault Log Snapshot:")
    for fault in recovery.get_fault_log():
        print(fault)

# ┌────────────────────────────────────────────┐
# │ Main Entry Point                           │
# └────────────────────────────────────────────┘

if __name__ == "__main__":
    orchestrator, power, thermal, recovery, registry, vacuum = boot_starship_suite()

    try:
        launch_gui(orchestrator, power, thermal, recovery, vacuum)
    except Exception as e:
        print(f"\n⚠️ GUI failed: {e}")
        print("Falling back to CLI dashboard...\n")
        cli_dashboard(orchestrator, power, thermal, recovery)

