console.log("interface.js loaded");
window.startDataFetchingLoops = function() {
    console.log("Starting data fetch loops...");
    setInterval(() => {
        fetch('/daisy_engineering_metrics')
            .then(response => response.json())
            .then(data => {
                console.log("Daisy Metrics:", data);
                document.getElementById('warp-speed').innerText = `Warp: ${data.propulsion_data.warp_speed.value}`;
                document.getElementById('core-temp').innerText = `Core Temp: ${data.subsystems_data.warp_core.core_temperature.value}°K`;
                document.getElementById('plasma-rate').innerText = `Plasma: ${data.subsystems_data.plasma_injectors.injection_rate.value} mg/s`;
                document.getElementById('field-strength').innerText = `Field Strength: ${data.subsystems_data.warp_core.warp_field_strength.value}%`;
                if (data.propulsion_data.warp_speed.value > 9.0 || data.subsystems_data.warp_core.core_temperature.value > 700) {
                    document.getElementById('status').style.color = 'red';
                    document.getElementById('status').style.borderColor = 'red';
                    document.getElementById('status').style.textShadow = '0 0 10px red';
                    document.getElementById('status').style.boxShadow = '0 0 15px red';
                    document.getElementById('status').innerText = data.propulsion_data.warp_speed.value > 9.0 ?
                        'DANGER: Structural Integrity at Risk!' : 'DANGER: Core Temperature Critical!';
                } else {
                    document.getElementById('status').style.color = '#00FF00';
                    document.getElementById('status').style.borderColor = '#00FF00';
                    document.getElementById('status').style.textShadow = '0 0 10px #00FF00';
                    document.getElementById('status').style.boxShadow = '0 0 15px #00FF00';
                    document.getElementById('status').innerText = 'Systems Nominal';
                }
            })
            .catch(err => console.error("Metrics error:", err));
    }, 1000);
};

function sendDaisyCommand(command, args = []) {
    fetch('/daisy_engineering_command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command, args })
    })
    .then(response => response.json())
    .then(data => console.log("Command Result:", data))
    .catch(err => console.error("Command error:", err));
}

window.startDataFetchingLoops();
