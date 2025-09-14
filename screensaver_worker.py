# workers/screensaver_worker.py
import threading
import time
import random
import math
from typing import List

# This is the key for integration
from workers.worker_base import WorkerBase

try:
    from rich.console import Console
    from rich.live import Live
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# --- Configuration ---
WIDTH = 110
HEIGHT = 30
NUM_STARS = 150
GALAXY_CENTER_X = WIDTH // 2
GALAXY_CENTER_Y = HEIGHT // 2
GALAXY_ARM_COUNT = 4
GALAXY_TIGHTNESS = 0.15

class ScreenSaverWorker(WorkerBase):
    """
    A purely aesthetic worker that generates a beautiful, animated
    ASCII galaxy screensaver in the terminal.
    """
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "Dream Sequencer"
        self.command = "screensaver"
        self.console = Console() if RICH_AVAILABLE else type('fallback', (), {'print': print})()
        
        self.stars = [
            {
                "angle": random.uniform(0, 2 * math.pi * GALAXY_ARM_COUNT),
                "distance": random.uniform(0, 1) ** 2,
                "char": random.choice(['.', '*', '+']),
                "brightness": random.uniform(0.3, 1.0)
            }
            for _ in range(NUM_STARS)
        ]

    def _log(self, message: str, style: str = "cyan"):
        prefix = f"[{self.name}]"
        if RICH_AVAILABLE:
            self.console.print(f"{prefix} {message}", style=style)
        else:
            print(f"{prefix} {message}")
            
    def _generate_frame(self, t: float) -> str:
        """Generates a single frame of the galaxy animation."""
        grid = [[' ' for _ in range(WIDTH)] for _ in range(HEIGHT)]

        for star in self.stars:
            # Calculate the spiral arm position
            arm_angle = star['angle']
            spiral_angle = GALAXY_TIGHTNESS * star['distance'] * 2 * math.pi
            
            # Rotation
            rotation_speed = 0.05
            rotated_angle = arm_angle + (star['distance'] * rotation_speed) + t

            # Convert polar coordinates to Cartesian
            dist_from_center = star['distance'] * GALAXY_CENTER_X
            x = GALAXY_CENTER_X + int(dist_from_center * math.cos(rotated_angle))
            y = GALAXY_CENTER_Y + int(dist_from_center * 0.5 * math.sin(rotated_angle)) # 0.5 makes it elliptical

            if 0 <= y < HEIGHT and 0 <= x < WIDTH:
                # Dim stars that are further away
                if star['brightness'] < 0.5:
                    grid[y][x] = f"[dim]{star['char']}[/dim]"
                else:
                    grid[y][x] = star['char']
        
        # Add a central glow
        grid[GALAXY_CENTER_Y][GALAXY_CENTER_X] = "[bold yellow]@[/bold yellow]"

        return "\n".join("".join(row) for row in grid)

    # --- THE SIGNATURE IS CORRECT ---
    def execute_task(self, args: List[str], stop_event: threading.Event):
        """
        The main task loop. Runs the screensaver animation until stopped by the CEO.
        """
        if not RICH_AVAILABLE:
            self._log("This command needs the 'rich' library to work its magic, sweety.", style="red")
            return
        
        self._log("Initializing dream sequence. Press 'stop screensaver' to return.", style="magenta")
        time.sleep(2)
        
        try:
            with Live(self._generate_frame(0), screen=True, refresh_per_second=10) as live:
                start_time = time.time()
                # The animation loop runs until the 'stop screensaver' command is issued
                while not stop_event.is_set():
                    elapsed_time = time.time() - start_time
                    live.update(self._generate_frame(elapsed_time))
                    # A short sleep to prevent high CPU usage, but the refresh_per_second handles most of it
                    time.sleep(0.05)
        except Exception as e:
            self._log(f"Oh dear, the dream sequence flickered out. Error: {e}", style="bold red")
        finally:
            self.console.clear()
            self._log("Dream sequence complete. Welcome back, starlight. ✨", style="magenta")

def create_worker(config: dict) -> ScreenSaverWorker:
    """Standard entry point for the AI to 'hire' this worker."""
    return ScreenSaverWorker(config)
