import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import threading
import time
import math
import random

# Simulated AI and Worker Classes
class ExoticParticle:
    def __init__(self, name, phi, theta, vacuum_integrity):
        self.name = name
        self.phi = phi  # Coherence phase drift
        self.theta = theta  # Resonance factor
        self.vacuum_integrity = vacuum_integrity

class WarpEngineWorker:
    def __init__(self):
        self.particles = []
        self.ai_adjusted = False

    def inject_particles(self, particles):
        self.particles = particles

    def simulate(self, phi, theta, vacuum_integrity, current, voltage, mu_r, chi):
        if not self.particles:
            return {}
        p = self.particles[0]
        p.phi = phi
        p.theta = theta
        p.vacuum_integrity = vacuum_integrity
        # AI optimization: Adjust if vacuum integrity drops
        if not self.ai_adjusted and vacuum_integrity < 60.0:
            p.phi = max(0.1, p.phi - 0.1)
            p.theta = min(0.9, p.theta + 0.1)
            self.ai_adjusted = True
        return {
            "phi": p.phi,
            "theta": p.theta,
            "vacuum_integrity": vacuum_integrity + random.uniform(-1, 1),
            "current": current,
            "voltage": voltage,
            "mu_r": mu_r,
            "chi": chi
        }

    def get_narration(self, telemetry):
        if telemetry.get("vacuum_integrity", 54.0) < 50.0:
            return "Warning: Vacuum integrity critical, initiating stabilization."
        return "Reactor operating within nominal parameters."

# Global State
telemetry_store = {}
reactor_count = 3
startup_sequence = [False] * reactor_count
shutdown_sequence = [False] * reactor_count

# Start Simulation Threads
def start_reactor_sim(index):
    worker = WarpEngineWorker()
    particles = [
        ExoticParticle("Tetraquark", 0.6, 0.5, 54.0),
        ExoticParticle("Anyon", 0.3, 0.25, 54.0),
        ExoticParticle("BEC", 0.1, 0.0, 54.0),
        ExoticParticle("Casimir Zone", 0.05, 0.0, 54.0)
    ]
    worker.inject_particles(particles)

    while True:
        # Use global controls for simulation
        global phi_value, theta_value, vacuum_value, current_value, voltage_value, mu_r_value, chi_value
        telemetry = worker.simulate(phi_value, theta_value, vacuum_value, current_value, voltage_value, mu_r_value, chi_value)
        telemetry_store[index] = telemetry
        time.sleep(3)

for i in range(reactor_count):
    threading.Thread(target=start_reactor_sim, args=(i,), daemon=True).start()

# Dash App Setup
app = dash.Dash(__name__)
app.title = "AI-Driven Quantum Warp Reactor"

# Initial Variable Values
phi_value = 0.6
theta_value = 0.5
vacuum_value = 54.0
current_value = 2.1
voltage_value = 12.0
mu_r_value = 1.18
chi_value = -0.993

# Layout
app.layout = html.Div(style={"backgroundColor": "#111", "color": "#eee", "padding": "20px"}, children=[
    html.H1("🌀 AI-Driven Quantum Warp Reactor", style={"textAlign": "center"}),
    html.Div([
        html.Div([
            html.H3("Reactor Schematic"),
            html.Img(src="/assets/reactor_schematic.svg", style={"width": "100%", "border": "1px solid #444"}),
            html.Div("Click zones to inspect subsystems", style={"fontSize": "14px", "marginTop": "5px"})
        ], style={"width": "48%", "display": "inline-block", "verticalAlign": "top"}),
        html.Div([
            html.H3("Subsystem Detail Panel"),
            html.Div(id="subsystem-detail", style={"fontSize": "16px", "whiteSpace": "pre-line", "padding": "10px", "border": "1px solid #444"})
        ], style={"width": "48%", "display": "inline-block", "verticalAlign": "top"})
    ]),
    html.Div([
        html.H3("Variable Controls"),
        dcc.Slider(id="phi-slider", min=0.1, max=1.0, step=0.1, value=phi_value, marks={i/10: f"{i/10}" for i in range(1, 11)}),
        dcc.Slider(id="theta-slider", min=0.0, max=1.0, step=0.1, value=theta_value, marks={i/10: f"{i/10}" for i in range(0, 11)}),
        dcc.Slider(id="vacuum-slider", min=0.0, max=100.0, step=1.0, value=vacuum_value, marks={i: f"{i}" for i in range(0, 101, 20)}),
        dcc.Input(id="current-input", type="number", value=current_value, step=0.1),
        dcc.Input(id="voltage-input", type="number", value=voltage_value, step=0.1),
        dcc.Input(id="mu_r-input", type="number", value=mu_r_value, step=0.01),
        dcc.Input(id="chi-input", type="number", value=chi_value, step=0.001),
    ], style={"marginTop": "20px"}),
    html.Div([
        html.H3("Subsystem Metrics"),
        html.Div(id="math-display", style={"fontSize": "18px", "marginBottom": "20px"}),
        html.Div(id="commentary-feed", style={"fontSize": "16px", "whiteSpace": "pre-line"}),
        dcc.Graph(id="gauge-power"),
        dcc.Graph(id="gauge-vacuum"),
        dcc.Graph(id="gauge-resonance"),
        dcc.Graph(id="gauge-shielding")
    ], style={"marginTop": "40px"}),
    html.Div([
        html.H3("Multi-Reactor Orchestration"),
        html.Div(id="orchestration-panel", style={"fontSize": "16px", "marginBottom": "20px"}),
        html.Button("Startup All Reactors", id="startup-button", n_clicks=0, style={"marginRight": "10px"}),
        html.Button("Shutdown All Reactors", id="shutdown-button", n_clicks=0)
    ], style={"marginTop": "40px", "textAlign": "center"}),
    html.Div([
        html.H3("Failsafe Status"),
        html.Div(id="failsafe-status", style={"fontSize": "20px", "color": "#f33"}),
        html.Button("Manual Override", id="override-button", n_clicks=0, style={"marginTop": "10px"})
    ], style={"marginTop": "40px", "textAlign": "center"}),
    dcc.Interval(id="interval-component", interval=3000, n_intervals=0)
])

# Callbacks
@app.callback(
    [Output("phi-value", "data"),
     Output("theta-value", "data"),
     Output("vacuum-value", "data"),
     Output("current-value", "data"),
     Output("voltage-value", "data"),
     Output("mu_r-value", "data"),
     Output("chi-value", "data")],
    [Input("phi-slider", "value"),
     Input("theta-slider", "value"),
     Input("vacuum-slider", "value"),
     Input("current-input", "value"),
     Input("voltage-input", "value"),
     Input("mu_r-input", "value"),
     Input("chi-input", "value")]
)
def update_variables(phi, theta, vacuum, current, voltage, mu_r, chi):
    global phi_value, theta_value, vacuum_value, current_value, voltage_value, mu_r_value, chi_value
    phi_value = phi if phi is not None else phi_value
    theta_value = theta if theta is not None else theta_value
    vacuum_value = vacuum if vacuum is not None else vacuum_value
    current_value = current if current is not None else current_value
    voltage_value = voltage if voltage is not None else voltage_value
    mu_r_value = mu_r if mu_r is not None else mu_r_value
    chi_value = chi if chi is not None else chi_value
    return phi_value, theta_value, vacuum_value, current_value, voltage_value, mu_r_value, chi_value

@app.callback(
    Output("subsystem-detail", "children"),
    Output("orchestration-panel", "children"),
    Output("math-display", "children"),
    Output("commentary-feed", "children"),
    Output("gauge-power", "figure"),
    Output("gauge-vacuum", "figure"),
    Output("gauge-resonance", "figure"),
    Output("gauge-shielding", "figure"),
    Output("failsafe-status", "children"),
    Input("interval-component", "n_intervals"),
    Input("startup-button", "n_clicks"),
    Input("shutdown-button", "n_clicks"),
    Input("override-button", "n_clicks")
)
def update_dashboard(n, startup_clicks, shutdown_clicks, override_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return ("", "", "", "", {}, {}, {}, {}, "✅ Reactor Stable")

    worker = WarpEngineWorker()
    t = telemetry_store.get(0, {})
    phi = t.get("phi", phi_value)
    G_phi = 1 - phi
    current = t.get("current", current_value)
    voltage = t.get("voltage", voltage_value)
    power = current * voltage
    theta = t.get("theta", theta_value)
    resonance = theta ** 2 * math.exp(-0.5 / 1.2)
    mu_r = t.get("mu_r", mu_r_value)
    chi = t.get("chi", chi_value)
    vacuum_integrity = t.get("vacuum_integrity", vacuum_value)

    # Commentary with AI narration
    commentary = f"""
Quantum Lage-Hon Amouity: G_phi={G_phi:.3f} | Phase drift={phi:.3f}
Recovence Chartum: Resonance={resonance:.2f}
Monitoring Node: Power={power:.2f}W | V={voltage:.1f}V
Vacuum Isolation: Integrity={vacuum_integrity:.1f}%
{worker.get_narration(t)}
"""

    # Math Display
    math_display = html.Div([
        html.Div(f"G\u03d5 = 1 - \u03d5 → {G_phi:.3f}"),
        html.Div(f"Resonance ∝ \u03b8² e^(-t/τ) → {resonance:.2f}"),
        html.Div(f"P = IV → {power:.2f} W"),
        html.Div(f"Vacuum Integrity → {vacuum_integrity:.1f}%")
    ])

    # Gauges
    def make_gauge(title, value, max_val):
        return go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={"text": title},
            gauge={"axis": {"range": [None, max_val]}, "bar": {"color": "#00ff99"}},
            number={"font": {"color": "#eee"}}
        )).update_layout(paper_bgcolor="#222", font={"color": "#eee"})

    failsafe_reason = None
    if G_phi < 0.85:
        failsafe_reason = "Coherence Collapse"
    elif resonance > 5.0:
        failsafe_reason = "Resonance Overload"
    elif power > 50.0:
        failsafe_reason = "Power Surge"
    elif chi < -0.98:
        failsafe_reason = "Shielding Failure"
    elif vacuum_integrity < 50.0:
        failsafe_reason = "Vacuum Breach"
    elif override_clicks > 0:
        failsafe_reason = "Manual Override"

    failsafe_status = f"⚠️ FAILSAFE TRIGGERED: {failsafe_reason}" if failsafe_reason else "✅ Reactor Stable"

    # Orchestration Panel
    orchestration = ""
    for i in range(reactor_count):
        t = telemetry_store.get(i, {})
        phi = t.get("phi", phi_value)
        G_phi = 1 - phi
        current = t.get("current", current_value)
        voltage = t.get("voltage", voltage_value)
        power = current * voltage
        theta = t.get("theta", theta_value)
        resonance = theta ** 2 * math.exp(-0.5 / 1.2)
        mu_r = t.get("mu_r", mu_r_value)
        chi = t.get("chi", chi_value)
        vacuum_integrity = t.get("vacuum_integrity", vacuum_value)

        failsafe = None
        if G_phi < 0.85:
            failsafe = "Coherence Collapse"
        elif resonance > 5.0:
            failsafe = "Resonance Overload"
        elif power > 50.0:
            failsafe = "Power Surge"
        elif chi < -0.98:
            failsafe = "Shielding Failure"
        elif vacuum_integrity < 50.0:
            failsafe = "Vacuum Breach"

        orchestration += f"""
🔷 Reactor-{i}
  G_phi: {G_phi:.3f}
  Resonance: {resonance:.2f}
  Power: {power:.2f} W
  Vacuum: {vacuum_integrity:.1f}%
  Status: {"⚠️ " + failsafe if failsafe else "✅ Stable"}
"""

    # Subsystem Detail
    detail = f"""
Subsystem: Quantum Lage-Hon Amouity
Equation: G_phi = 1 - phi
Current Value: G_phi = {G_phi:.3f}
Status: {"⚠️ Unstable" if G_phi < 0.85 else "Stable"}
"""

    return (
        detail,
        orchestration,
        math_display,
        commentary,
        make_gauge("Power Draw (W)", power, 60),
        make_gauge("Vacuum Integrity (%)", vacuum_integrity, 100),
        make_gauge("Resonance Output", resonance, 6),
        make_gauge("Shielding χ", chi, 0),
        failsafe_status
    )

if __name__ == "__main__":
    app.run_server(debug=True)
