# subsystems/gui/lifesupport_gui.py
import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QTextEdit, QApplication
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

# This import is needed for the GUI to find its worker
from subsystems.modules.lifesupport_worker import LifeSupportWorker

class LifeSupportGUI(QWidget):
    def __init__(self, worker, registry):
        super().__init__()
        self.worker = worker
        self.registry = registry
        self.o2_data = []
        self.co2_data = []
        self.temp_data = []
        self.init_ui()
        self.init_timer()

    def init_ui(self):
        self.setWindowTitle("Life Support Console")
        layout = QVBoxLayout()
        self.o2_label = QLabel()
        self.co2_label = QLabel()
        self.temp_label = QLabel()
        self.power_label = QLabel()
        self.o2_plot = pg.PlotWidget(title="🌬️ O₂ Level (%)")
        self.o2_plot.setYRange(20, 22)
        self.co2_plot = pg.PlotWidget(title="🫁 CO₂ Level (%)")
        self.co2_plot.setYRange(0, 0.1)
        self.temp_plot = pg.PlotWidget(title="🌡️ Temperature (°C)")
        self.temp_plot.setYRange(20, 24)
        self.trouble_display = QTextEdit(); self.trouble_display.setReadOnly(True)
        layout.addWidget(self.o2_label); layout.addWidget(self.o2_plot)
        layout.addWidget(self.co2_label); layout.addWidget(self.co2_plot)
        layout.addWidget(self.temp_label); layout.addWidget(self.temp_plot)
        layout.addWidget(self.power_label); layout.addWidget(QLabel("⚠️ Trouble Codes"))
        layout.addWidget(self.trouble_display)
        self.setLayout(layout)

    def init_timer(self):
        self.timer = QTimer(); self.timer.timeout.connect(self.update_graphs)
        self.timer.start(1000) # Update once per second

    def update_graphs(self):
        # --- FIX: Get new data from the worker's get_metrics method ---
        metrics = self.worker.get_metrics()
        o2 = metrics['o2_level']; co2 = metrics['co2_level']; temp = metrics['temp']
        
        self.o2_data.append(o2); self.co2_data.append(co2); self.temp_data.append(temp)
        if len(self.o2_data) > 100: self.o2_data.pop(0)
        if len(self.co2_data) > 100: self.co2_data.pop(0)
        if len(self.temp_data) > 100: self.temp_data.pop(0)
        
        self.o2_plot.plot(self.o2_data, clear=True)
        self.co2_plot.plot(self.co2_data, clear=True)
        self.temp_plot.plot(self.temp_data, clear=True)
        
        self.o2_label.setText(f"O₂ Level: {o2:.2f}%")
        self.co2_label.setText(f"CO₂ Level: {co2:.3f}%")
        self.temp_label.setText(f"Temperature: {temp}°C")
        self.power_label.setText(f"Power OK: {metrics['power_ok']}")
