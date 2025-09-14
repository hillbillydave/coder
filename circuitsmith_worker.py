# workers/circuitsmith_worker.py
import threading
from typing import List, Dict, Any
import requests
import time

from workers.worker_base import WorkerBase

try:
    from rich.console import Console
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

COMPONENT_SYMBOLS = {
    "power": {"symbol": "( +5V )", "resistance": 0, "desc": "DC Power Source"},
    "resistor": {"symbol": "---[ R ]---", "resistance": 100, "desc": "100Ω Resistor"},
    "led": {"symbol": "---|>|---", "resistance": 20, "desc": "Light Emitting Diode"},
    "capacitor": {"symbol": "---||----", "resistance": 0, "desc": "Capacitor"},
    "switch": {"symbol": "---/ ----", "resistance": 0, "desc": "Manual Switch"},
    "ground": {"symbol": "---GND---", "resistance": 0, "desc": "Ground"},
}

class CircuitSmithWorker(WorkerBase):
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "CircuitSmith"
        self.command = "circuitsmith"
        self.console = Console() if RICH_AVAILABLE else type('fallback', (), {'print': print})()

    def _log(self, message: str, style: str = "cyan"):
        prefix = f"[{self.name}]"
        if RICH_AVAILABLE: self.console.print(f"{prefix} {message}", style=style)
        else: print(f"{prefix} {message}")

    def _generate_schematic(self, components: List[str]) -> str:
        # ... (This function is unchanged)
        if not components: return "[dim]No components specified.[/dim]"
        power_source = COMPONENT_SYMBOLS['power']['symbol']
        gnd = COMPONENT_SYMBOLS['ground']['symbol']
        component_parts = [c for c in components if c not in ['power', 'ground']]
        part_symbols = [COMPONENT_SYMBOLS[c]['symbol'] for c in component_parts]
        center_line = power_source + "".join(part_symbols) + gnd
        schematic = [
            "." + "-" * (len(center_line) + 2) + ".",
            "| " + " " * len(center_line) + " |",
            "+- " + center_line + " -+",
            "| " + " " * len(center_line) + " |",
            "'" + "-" * (len(center_line) + 2) + "'"
        ]
        return "\n".join(schematic)

    def _send_report_to_fleetbridge(self, components: List[str]):
        # ... (This function is unchanged)
        if not components: return
        total_resistance = sum(COMPONENT_SYMBOLS[c]['resistance'] for c in components if c in COMPONENT_SYMBOLS)
        voltage = 5.0
        current_ma = (voltage / total_resistance) * 1000 if total_resistance > 0 else float('inf')
        is_alert = "led" in components and total_resistance <= 20
        payload = {
            "Status": "Alert: High Current!" if is_alert else "Nominal",
            "Voltage": f"{voltage:.1f}V", "Total Resistance": f"{total_resistance}Ω",
            "Calculated Current": f"{current_ma:.2f} mA",
            "Bill of Materials": [COMPONENT_SYMBOLS[c]['desc'] for c in components if c in COMPONENT_SYMBOLS]
        }
        gui_payload = { "source": self.name, "payload": payload, "is_alert": is_alert, "alert_message": "High current detected! LED may be at risk." if is_alert else "" }
        try:
            requests.post("http://127.0.0.1:5555/update", json=gui_payload, timeout=2)
            self._log("Circuit analysis sent to FleetBridge.", style="dim")
        except requests.exceptions.RequestException: pass

    def _show_help(self):
        # ... (This function is unchanged)
        help_panel = Panel("[bold]Designs a simple series circuit.[/bold]\n\n[bold cyan]Usage:[/bold cyan] [green]circuitsmith <component1> ...[/green]\n\n[bold cyan]Example:[/bold cyan] [green]circuitsmith power resistor led ground[/green]", title="[bold blue]CircuitSmith Help[/bold blue]", border_style="green")
        self.console.print(help_panel)

    # --- THIS IS THE FIX ---
    # It now correctly accepts both 'args' and the 'stop_event' from the CEO.
    def execute_task(self, args: List[str], stop_event: threading.Event):
        """The main entry point called by the AI."""
        if not args or 'help' in args:
            self._show_help()
            return

        valid_components = [c for c in args if c in COMPONENT_SYMBOLS]
        unknown_components = [c for c in args if c not in COMPONENT_SYMBOLS]

        if unknown_components:
            self._log(f"I don't recognize these parts: {', '.join(unknown_components)}", style="yellow")
        
        if not valid_components:
            self._log("You haven't given me any valid components to work with.", style="red")
            return
            
        self._log("Generating schematic...", style="green")
        time.sleep(1)

        schematic = self._generate_schematic(valid_components)
        schematic_panel = Panel(schematic, title="[bold magenta]Circuit Schematic[/bold magenta]", border_style="magenta")
        self.console.print(schematic_panel)
        self._send_report_to_fleetbridge(valid_components)

def create_worker(config: dict) -> CircuitSmithWorker:
    return CircuitSmithWorker(config)
