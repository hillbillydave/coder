# Coder
AI-assisted Python diagnostic platform for automotive, EV, and aerospace systems, built by David Blackwell (KF5WCM), a self-taught auto tech grinding out of necessity. Features OBD-II monitoring, M18 battery integration, FleetBridge networking, and early avionics/radar diagnostics.

## About
*Coder* (HAA Core Alpha v0.4, Vespera's Modular Studio) is my work-in-progress answer to pro scan tools like Snap-on Zeus, built with Python and AI to automate diagnostics for cars, EVs, big rigs, monster trucks, and maybe aircraft. I’m a B-level auto tech with 10+ years of experience, learning Python, Linux, and ham radio (KF5WCM) to escape the daily grind. It’s got a Tkinter GUI, CLI interface, Milwaukee M18 battery hacks, FleetBridge for network pairing, and early avionics/radar code. I’m pivoting to diagnostic coding or radar/avionics tech, hungry to learn more.

## Features
- **Diagnostics**: OBD-II monitoring, ECU tuning, VATS reprogramming for cars, EVs, big rigs, monster trucks.
- **Power Systems**: Milwaukee M18 battery integration for affordable EV repairs.
- **Comms**: WiFi router repurposing via FleetBridge (KF5WCM skills).
- **Aerospace Potential**: Early avionics diagnostics (e.g., ARINC 429) and radar calibration.
- **Interfaces**: Tkinter GUI (`main_app.py`) and CLI (`app.py`) for work orders and diagnostics.
- **Work in Progress**: Adding radar/avionics templates, learning fast.

## Setup
1. Clone: `git clone https://github.com/yourusername/Coder.git`
2. Activate virtual environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
3. Install: `pip install -r requirements.txt`
4. Run: `python app.py` for CLI, `python main_app.py` for GUI, or `python demo.py` for demo

## Demo
Run `demo.py` to see M18 battery integration, OBD-II scan, and WiFi diagnostics:  
[Watch Demo Video](https://youtube.com/your-unlisted-link) *(replace with your YouTube link)*

## Files
- `app.py`: CLI interface for worker management and LLM interactions.
- `main_app.py`: Tkinter GUI for work orders and diagnostics.
- `workers/shop_code_worker.py`: Core diagnostic logic.
- `workers/connectivity_worker.py`: FleetBridge networking and pairing.
- `database.py`: SQLite database for work orders and reports.
- `connector.py`: Mock OBD-II/ECU connectors (ELM327, J2534).
- `workers/config.json`: Worker configs and diagnostic task templates.
- `demo.py`: Demo script for employers.

## Requirements
See `requirements.txt`:
psutil
pyusb
pynvml
tkinter
pyttsx3
pygame
requests


## Author
David Blackwell, B-level Auto Tech, Ham Radio Operator (KF5WCM)  
Contact: vx96hmm258@privaterelay.appleid.com  
LinkedIn: [your-linkedin-url] *(add if you have one)*

## Note
Built out of necessity with AI help, *Coder* is a work in progress. I’m grinding to apply it to automotive coding and aerospace. Feedback welcome!


