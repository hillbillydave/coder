# workers/map_worker.py
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import requests
import time

from workers.worker_base import WorkerBase

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live
    from rich.layout import Layout
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

REFRESH_INTERVAL_SECONDS = 6 * 60 * 60 # 6 hours

class MapWorker(WorkerBase):
    def __init__(self, config: dict):
        super().__init__(config)
        # The name/command/persona will be set by the WorkerBase using the config
        
        # --- THIS IS THE FIX ---
        # The worker now explicitly asks for the NEO key from the global config.
        # It's accessing self.global_config which was set by the WorkerBase.
        self.api_key = self.global_config.get("api_keys", {}).get("NASA_NEO_KEY", "DEMO_KEY")
        
        self.settings_manager = self.global_config.get('settings_manager')
        self.console = Console() if RICH_AVAILABLE else type('fallback', (), {'print': print})()

    def _log(self, message: str, style: str = "cyan"):
        # We now use the speak() method from the base class for persona-driven output
        self.speak(message)

    def _fetch_neos(self) -> Optional[List[Dict]]:
        # ... (This function is unchanged)
        today_str = datetime.now().strftime('%Y-%m-%d')
        url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={today_str}&end_date={today_str}&api_key={self.api_key}"
        try:
            r = requests.get(url, timeout=15); r.raise_for_status()
            return r.json().get("near_earth_objects", {}).get(today_str, [])
        except requests.exceptions.RequestException as e:
            self.speak(f"Connection to NASA fizzled out... Error: {e}")
            return None

    def _send_data_to_fleetbridge(self, neos: List[Dict]):
        # ... (This function is unchanged)
        if not neos: payload = {"status": "Skies are clear!"}
        else:
            payload = {"object_count": len(neos), "closest_approach": {}, "most_hazardous": {}}
            closest_neo = min(neos, key=lambda x: float(x['close_approach_data'][0]['miss_distance']['kilometers']))
            hazardous_neos = [n for n in neos if n['is_potentially_hazardous_asteroid']]
            payload["closest_approach"] = {"name": closest_neo['name'], "miss_km": f"{float(closest_neo['close_approach_data'][0]['miss_distance']['kilometers']):,.0f}"}
            if hazardous_neos:
                fastest_hazard = max(hazardous_neos, key=lambda x: float(x['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']))
                payload["most_hazardous"] = {"name": fastest_hazard['name'], "velocity_kph": f"{float(fastest_hazard['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']):,.0f}"}
        gui_payload = {"source": self.name, "payload": payload, "is_alert": any(neo['is_potentially_hazardous_asteroid'] for neo in neos)}
        if gui_payload["is_alert"]:
            alert_count = len(hazardous_neos) if hazardous_neos else 0
            gui_payload["alert_message"] = f"{alert_count} potentially hazardous object(s) detected on approach."
        try:
            requests.post("http://127.0.0.1:5555/update", json=gui_payload, timeout=2)
        except requests.exceptions.RequestException: pass

    def _generate_rich_layout(self, neos: Optional[List[Dict]]):
        # ... (This function is unchanged)
        if neos is None: return Panel("[bold red]Connection to NASA fizzled out...[/bold red]")
        map_str = "[dim]... Celestial Map Rendering ...[/dim]"
        map_panel = Panel(map_str, box=box.HEAVY, border_style="yellow", height=15)
        report_table = Table(title=f"Mission Briefing ({datetime.now().strftime('%H:%M:%S')})", border_style="cyan", show_header=True, header_style="bold cyan")
        report_table.add_column("Name", style="magenta", width=30); report_table.add_column("Miss (km)", style="yellow", justify="right"); report_table.add_column("Hazardous?", style="red")
        if not neos: report_table.add_row("[green]Skies are clear![/green]", "", "")
        else:
            for neo in sorted(neos, key=lambda x: float(x['close_approach_data'][0]['miss_distance']['kilometers']))[:10]:
                report_table.add_row(neo['name'], f"{float(neo['close_approach_data'][0]['miss_distance']['kilometers']):,.0f}", "YES 🚨" if neo['is_potentially_hazardous_asteroid'] else "No")
        layout = Layout(); layout.split(Layout(map_panel, name="main"), Layout(report_table, name="footer", size=min(12, len(neos) + 4 if neos else 5)));
        return Panel(layout, title="[bold blue]🚀 Grand Tour of the Solar System (Live)[/bold blue]", subtitle="[dim]*NEO report also sent to FleetBridge GUI[/dim]", border_style="green")

    def execute_task(self, args: List[str], stop_event: threading.Event):
        # ... (This function is unchanged)
        if not RICH_AVAILABLE: self.speak("This command needs 'rich' to draw its map, sweety."); return
        if "DEMO_KEY" in self.api_key or "PASTE_YOUR" in self.api_key: self.speak("I can't check the skies without a NASA API key, sweety."); return
        try:
            initial_neos = self._fetch_neos()
            with Live(self._generate_rich_layout(initial_neos), screen=False, redirect_stderr=False, refresh_per_second=1) as live:
                if initial_neos is not None: self._send_data_to_fleetbridge(initial_neos)
                while not stop_event.is_set():
                    current_refresh_seconds = self.settings_manager.get('map_refresh_seconds', REFRESH_INTERVAL_SECONDS)
                    self.speak(f"Next NEO update in {current_refresh_seconds / 60:.0f} minutes.")
                    stop_event.wait(current_refresh_seconds)
                    if stop_event.is_set(): break
                    neos = self._fetch_neos()
                    if neos is not None: live.update(self._generate_rich_layout(neos)); self._send_data_to_fleetbridge(neos)
        except Exception as e: self.speak(f"Oh, drat. My console had a little hiccup. Error: {e}")
        finally: self.speak("Performance complete. The stage is yours again, sweety! 💋")

def create_worker(config: dict) -> MapWorker:
    return MapWorker(config)
