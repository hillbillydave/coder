// static/interface.js
let fleetPlot, driftPlot;

function setupCharts() {
    const fleetPlotCtx = document.getElementById('fleetplot').getContext('2d');
    fleetPlot = new Chart(fleetPlotCtx, { type: 'line', data: { labels: [], datasets: [{ label: 'Distance from Sun (AU)', data: [], borderColor: 'cyan', tension: 0.1 }] }, options: { responsive: true, maintainAspectRatio: false } });
    const driftPlotCtx = document.getElementById('fleetdrift').getContext('2d');
    driftPlot = new Chart(driftPlotCtx, { type: 'bar', data: { labels: [], datasets: [{ label: 'Velocity (kps)', data: [], backgroundColor: 'lime' }] }, options: { responsive: true, maintainAspectRatio: false, indexAxis: 'y' } });
}

function updateTelemetry() {
    fetch('/telemetry').then(response => response.json()).then(data => {
        const fleetStatusDiv = document.getElementById('fleetstatus');
        const status = data.fleet_status || {};
        fleetStatusDiv.innerHTML = `<h3>Fleet Status</h3><p>AI Status: <span class="status-ok">${status.ai_status || 'Offline'}</span></p><p>Active Satellites: ${status.active_satellites || 0}</p><p>Tracking NEOs: ${status.tracking_neos || 0}</p>`;
    }).catch(error => console.error('Error fetching telemetry:', error));
}

function updateStudioLog() {
    fetch('/get_studio_log').then(response => response.json()).then(logs => {
        const logList = document.getElementById('studio-log-list');
        if (logList) {
            logList.innerHTML = logs.map(log => `<div class="log-entry"><span class="log-speaker ${log.speaker.toLowerCase()}">${log.speaker}:</span><span class="log-message">${log.message}</span></div>`).join('');
        }
    }).catch(error => console.error('Error fetching studio log:', error));
}

function handleStatusUpdate(message) {
    const statusDiv = document.getElementById('plotStatus');
    if (statusDiv) {
        statusDiv.textContent = message;
        if (message.toLowerCase().includes('error')) {
            statusDiv.style.color = '#ff6b6b';
        } else if (message.toLowerCase().includes('complete') || message.toLowerCase().includes('success') || message.toLowerCase().includes('render')) {
            statusDiv.style.color = '#1dd1a1';
        } else {
            statusDiv.style.color = '#48dbfb';
        }
    }
}
window.handleStatusUpdate = handleStatusUpdate;

document.addEventListener('DOMContentLoaded', () => {
    setupCharts();
    const plotButton = document.getElementById('plotButton');
    if (plotButton) {
        plotButton.addEventListener('click', () => {
            const objectId = document.getElementById('objectIdInput').value;
            if (!objectId) {
                handleStatusUpdate('Error: Please enter an object name.');
                return;
            }
            handleStatusUpdate(`Sending plot request for ${objectId}...`);
            fetch('/plot_object', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: objectId }) })
            .then(response => response.json()).then(data => {
                if (data.status !== 'ok') {
                    handleStatusUpdate(`Error: ${data.message}`);
                }
            }).catch(error => {
                handleStatusUpdate('Error: Could not connect to server.');
            });
        });
    }

    // --- Start all the update loops here ---
    setInterval(updateTelemetry, 3000);
    setInterval(updateStudioLog, 5000);

    // --- THIS IS THE RESTORED ORBITAL DATA LOOP ---
    setInterval(() => {
        fetch('/orbitaldata').then(response => response.json()).then(data => {
            if (window.updateMap) {
                // This calls the function in map3d.js to draw everything
                window.updateMap(data); 
            }
        }).catch(error => console.error('Error fetching orbital data:', error));
    }, 2000); // Check for new orbital data every 2 seconds
    // --- END OF RESTORATION ---
    
    // This is the unified loop for both status updates and final trajectory paths
    setInterval(() => {
        fetch('/get_plotted_path')
            .then(response => response.json())
            .then(data => {
                if (data && data.message) {
                    handleStatusUpdate(data.message);
                } 
                else if (data && data.path) {
                    if (window.updatePlottedPath) {
                        window.updatePlottedPath(data);
                    }
                }
            });
    }, 1000);
});
