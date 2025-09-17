# subsystems/gui/daisyengineering_gui.py
import sys
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QGridLayout, QPushButton, QHBoxLayout, QProgressBar, QApplication, QGroupBox
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtGui import QPen  # Moved QPen import here
from subsystems.modules.EngineeringSuiteWorker import EngineeringSuiteWorker

class DaisyEngineeringGUI(QWidget):
    def __init__(self, worker, registry, config=None):
        super().__init__()
        self.worker = worker
        self.registry = registry
        self.config = config or {"api_keys": {}, "workers": {}}
        self.time_elapsed = 0
        self.init_ui()
        self.start_sequence()
        self.oldPos = self.pos()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def init_ui(self):
        self.setWindowTitle("Daisy’s Warp Engineering Console")
        layout = QVBoxLayout()

        title_bar = QHBoxLayout()
        title = QLabel("🌀 Daisy’s Warp Engineering Console")
        title.setStyleSheet("""
            color: #00FF00;
            font-size: 24px;
            font-weight: bold;
            background: rgba(0, 255, 0, 0.1);
            padding: 10px;
            border: 2px solid #00FF00;
            border-radius: 10px;
            text-shadow: 0 0 10px #00FF00;
        """)
        title_bar.addWidget(title)
        title_bar.addStretch()
        close_btn = QPushButton("X")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 0, 0, 0.2);
                color: #FF0000;
                border: 2px solid #FF0000;
                border-radius: 10px;
                font-size: 14px;
                text-shadow: 0 0 5px #FF0000;
            }
            QPushButton:hover {
                background: rgba(255, 0, 0, 0.4);
                box-shadow: 0 0 10px #FF0000;
            }
        """)
        close_btn.clicked.connect(self.close)
        title_bar.addWidget(close_btn)
        layout.addLayout(title_bar)

        grid_frame = QGroupBox("Warp Core Controls")
        grid_frame.setStyleSheet("""
            QGroupBox {
                color: #00FF00;
                background: rgba(0, 0, 0, 0.7);
                border: 2px solid #00FF00;
                border-radius: 10px;
                margin-top: 10px;
                box-shadow: 0 0 15px #00FF00;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                color: #00FF00;
                text-shadow: 0 0 10px #00FF00;
            }
        """)
        grid = QGridLayout()

        inj_label = QLabel("Plasma Injector Rate (mg/s)")
        inj_label.setStyleSheet("color: #00FF00; text-shadow: 0 0 5px #00FF00;")
        self.injector_slider = QSlider(Qt.Horizontal)
        self.injector_slider.setRange(10, 50)
        self.injector_slider.setValue(30)
        self.injector_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #00FF00;
                height: 8px;
                background: rgba(0, 255, 0, 0.2);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #00FF00;
                border: 1px solid #00FF00;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
                box-shadow: 0 0 10px #00FF00;
            }
        """)
        self.injector_slider.valueChanged.connect(lambda v: self.adjust_injector(v / 100.0))
        grid.addWidget(inj_label, 0, 0)
        grid.addWidget(self.injector_slider, 0, 1)

        coil_label = QLabel("Coil Pulse Rate (%)")
        coil_label.setStyleSheet("color: #00FF00; text-shadow: 0 0 5px #00FF00;")
        self.coil_slider = QSlider(Qt.Horizontal)
        self.coil_slider.setRange(0, 100)
        self.coil_slider.setValue(50)
        self.coil_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #00FF00;
                height: 8px;
                background: rgba(0, 255, 0, 0.2);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #00FF00;
                border: 1px solid #00FF00;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
                box-shadow: 0 0 10px #00FF00;
            }
        """)
        self.coil_slider.valueChanged.connect(lambda v: self.adjust_coil(v))
        grid.addWidget(coil_label, 1, 0)
        grid.addWidget(self.coil_slider, 1, 1)

        grid_frame.setLayout(grid)
        layout.addWidget(grid_frame)

        self.backup_group = QGroupBox("🛡️ Backup Redundancy Systems")
        self.backup_group.setVisible(False)
        self.backup_group.setStyleSheet("""
            QGroupBox {
                color: #00FF00;
                background: rgba(0, 0, 0, 0.7);
                border: 2px solid #00FF00;
                border-radius: 10px;
                margin-top: 10px;
                box-shadow: 0 0 15px #00FF00;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                color: #00FF00;
                text-shadow: 0 0 10px #00FF00;
            }
        """)
        backup_layout = QVBoxLayout()
        self.backup_injector = QSlider(Qt.Horizontal)
        self.backup_injector.setRange(10, 50)
        self.backup_injector.setValue(30)
        self.backup_injector.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #00FF00;
                height: 8px;
                background: rgba(0, 255, 0, 0.2);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #00FF00;
                border: 1px solid #00FF00;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
                box-shadow: 0 0 10px #00FF00;
            }
        """)
        self.backup_injector.valueChanged.connect(lambda v: self.adjust_backup_injector(v / 100.0))
        backup_layout.addWidget(QLabel("Backup Injector Timing (mg/s)").setStyleSheet("color: #00FF00; text-shadow: 0 0 5px #00FF00;"))
        backup_layout.addWidget(self.backup_injector)
        self.backup_group.setLayout(backup_layout)
        layout.addWidget(self.backup_group)

        self.status_label = QLabel("🌀 Warp Reactor Status: Initializing...")
        self.status_label.setStyleSheet("""
            color: #00FF00;
            font-size: 18px;
            background: rgba(0, 0, 0, 0.7);
            padding: 10px;
            border: 2px solid #00FF00;
            border-radius: 10px;
            text-shadow: 0 0 10px #00FF00;
            box-shadow: 0 0 15px #00FF00;
        """)
        layout.addWidget(self.status_label)

        metrics_frame = QGroupBox("System Metrics")
        metrics_frame.setStyleSheet("""
            QGroupBox {
                color: #00FF00;
                background: rgba(0, 0, 0, 0.7);
                border: 2px solid #00FF00;
                border-radius: 10px;
                margin-top: 10px;
                box-shadow: 0 0 15px #00FF00;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                color: #00FF00;
                text-shadow: 0 0 10px #00FF00;
            }
        """)
        metrics_grid = QGridLayout()
        self.core_temp_bar = self.create_bar("Core Temp (°K)", metrics_grid, 0)
        self.warp_speed_bar = self.create_bar("Warp Speed", metrics_grid, 1)
        self.field_strength_bar = self.create_bar("Field Strength (%)", metrics_grid, 2)
        self.plasma_rate_bar = self.create_bar("Plasma Flow (mg/s)", metrics_grid, 3)
        metrics_frame.setLayout(metrics_grid)
        layout.addWidget(metrics_frame)

        self.warp_series = QLineSeries()
        self.warp_series.setName("Warp Speed")
        self.warp_series.setPen(QPen(Qt.green))
        self.temp_series = QLineSeries()
        self.temp_series.setName("Core Temp (°K)")
        self.temp_series.setPen(QPen(Qt.red))
        self.plasma_series = QLineSeries()
        self.plasma_series.setName("Plasma Flow (mg/s)")
        self.plasma_series.setPen(QPen(Qt.yellow))
        chart = QChart()
        chart.addSeries(self.warp_series)
        chart.addSeries(self.temp_series)
        chart.addSeries(self.plasma_series)
        chart.setTitle("Warp Engine Performance")
        chart.setStyleSheet("""
            background: rgba(0, 0, 0, 0.7);
            border: 2px solid #00FF00;
            border-radius: 10px;
            box-shadow: 0 0 15px #00FF00;
        """)
        axis_x = QValueAxis()
        axis_x.setTitleText("Time (s)")
        axis_x.setRange(0, 60)
        axis_x.setLabelFormat("%i")
        axis_x.setTitleBrush(Qt.green)
        axis_x.setLabelsColor(Qt.green)
        axis_y = QValueAxis()
        axis_y.setTitleText("Value")
        axis_y.setRange(0, 800)
        axis_y.setLabelFormat("%i")
        axis_y.setTitleBrush(Qt.green)
        axis_y.setLabelsColor(Qt.green)
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        self.warp_series.attachAxis(axis_x)
        self.warp_series.attachAxis(axis_y)
        self.temp_series.attachAxis(axis_x)
        self.temp_series.attachAxis(axis_y)
        self.plasma_series.attachAxis(axis_x)
        self.plasma_series.attachAxis(axis_y)
        chart_view = QChartView(chart)
        chart_view.setMinimumHeight(300)
        chart_view.setStyleSheet("border: 2px solid #00FF00; border-radius: 10px; box-shadow: 0 0 15px #00FF00;")
        layout.addWidget(chart_view)

        btn_frame = QGroupBox("Control Panel")
        btn_frame.setStyleSheet("""
            QGroupBox {
                color: #00FF00;
                background: rgba(0, 0, 0, 0.7);
                border: 2px solid #00FF00;
                border-radius: 10px;
                margin-top: 10px;
                box-shadow: 0 0 15px #00FF00;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                color: #00FF00;
                text-shadow: 0 0 10px #00FF00;
            }
        """)
        btn_layout = QHBoxLayout()
        toggle_btn = QPushButton("Toggle Backup Systems")
        toggle_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 255, 0, 0.2);
                color: #00FF00;
                border: 2px solid #00FF00;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                text-shadow: 0 0 5px #00FF00;
            }
            QPushButton:hover {
                background: rgba(0, 255, 0, 0.4);
                box-shadow: 0 0 10px #00FF00;
            }
        """)
        toggle_btn.clicked.connect(self.toggle_backup)
        btn_layout.addWidget(toggle_btn)
        engage_btn = QPushButton("Engage Warp")
        engage_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 255, 0, 0.2);
                color: #00FF00;
                border: 2px solid #00FF00;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                text-shadow: 0 0 5px #00FF00;
            }
            QPushButton:hover {
                background: rgba(0, 255, 0, 0.4);
                box-shadow: 0 0 10px #00FF00;
            }
        """)
        engage_btn.clicked.connect(lambda: self.execute_command("engage_warp", ["5.0"]))
        btn_layout.addWidget(engage_btn)
        stop_btn = QPushButton("Stop Warp")
        stop_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 255, 0, 0.2);
                color: #00FF00;
                border: 2px solid #00FF00;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                text-shadow: 0 0 5px #00FF00;
            }
            QPushButton:hover {
                background: rgba(0, 255, 0, 0.4);
                box-shadow: 0 0 10px #00FF00;
            }
        """)
        stop_btn.clicked.connect(lambda: self.execute_command("engage_warp", ["0.0"]))
        btn_layout.addWidget(stop_btn)
        btn_frame.setLayout(btn_layout)
        layout.addWidget(btn_frame)

        self.setLayout(layout)
        self.setStyleSheet("background: rgba(26, 26, 26, 0.9);")

    def create_bar(self, label_text, layout, row):
        label = QLabel(f"{label_text}:")
        label.setStyleSheet("color: #00FF00; text-shadow: 0 0 5px #00FF00;")
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #00FF00;
                border-radius: 5px;
                background: rgba(0, 0, 0, 0.7);
                text-align: center;
                color: #00FF00;
                text-shadow: 0 0 5px #00FF00;
            }
            QProgressBar::chunk {
                background: #00FF00;
                border-radius: 3px;
                box-shadow: 0 0 10px #00FF00;
            }
        """)
        layout.addWidget(label, row, 0)
        layout.addWidget(bar, row, 1)
        return bar

    def start_sequence(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(1000)

    def adjust_injector(self, value):
        result = self.execute_command("adjust_injectors", [str(value)])
        if "error" in result:
            self.status_label.setText(f"⚠️ Error: {result['error']}")
            self.status_label.setStyleSheet("color: red; font-size: 18px; background: rgba(0, 0, 0, 0.7); padding: 10px; border: 2px solid red; border-radius: 10px; text-shadow: 0 0 10px red; box-shadow: 0 0 15px red;")
            self.log_trouble_code("E101", f"Injector adjustment failed: {result['error']}")
        else:
            self.status_label.setText(f"🔧 Injector adjusted to {value} mg/s")
            self.status_label.setStyleSheet("color: #00FF00; font-size: 18px; background: rgba(0, 0, 0, 0.7); padding: 10px; border: 2px solid #00FF00; border-radius: 10px; text-shadow: 0 0 10px #00FF00; box-shadow: 0 0 15px #00FF00;")
        self.update_metrics()

    def adjust_coil(self, value):
        result = self.execute_command("adjust_coils", [str(value)])
        if "error" in result:
            self.status_label.setText(f"⚠️ Error: {result['error']}")
            self.status_label.setStyleSheet("color: red; font-size: 18px; background: rgba(0, 0, 0, 0.7); padding: 10px; border: 2px solid red; border-radius: 10px; text-shadow: 0 0 10px red; box-shadow: 0 0 15px red;")
            self.log_trouble_code("E102", f"Coil adjustment failed: {result['error']}")
        else:
            self.status_label.setText(f"🔧 Coil adjusted to {value}%")
            self.status_label.setStyleSheet("color: #00FF00; font-size: 18px; background: rgba(0, 0, 0, 0.7); padding: 10px; border: 2px solid #00FF00; border-radius: 10px; text-shadow: 0 0 10px #00FF00; box-shadow: 0 0 15px #00FF00;")
        self.update_metrics()

    def adjust_backup_injector(self, value):
        self.status_label.setText(f"🔧 Backup Injector adjusted to {value} mg/s")
        self.status_label.setStyleSheet("color: #00FF00; font-size: 18px; background: rgba(0, 0, 0, 0.7); padding: 10px; border: 2px solid #00FF00; border-radius: 10px; text-shadow: 0 0 10px #00FF00; box-shadow: 0 0 15px #00FF00;")
        self.update_metrics()

    def execute_command(self, command, args):
        result = self.worker.execute_task([command] + args, None)
        if self.registry.get("shared_data_queue"):
            self.registry["shared_data_queue"].put({
                "type": f"DAISY_ENGINEERING_{command.upper()}",
                "payload": result
            })
        self.update_metrics()
        return result

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def log_trouble_code(self, code, description):
        if hasattr(self.registry, 'add_code'):
            self.registry.add_code("DaisyEngineering", code, description)
            print(f"LOGGED TROUBLE CODE: {code} - {description}")

    def update_metrics(self):
        metrics = self.worker.get_metrics()
        warp_data = metrics["subsystems_data"]["warp_core"]
        plasma_data = metrics["subsystems_data"]["plasma_injectors"]
        propulsion_data = metrics["propulsion_data"]

        self.core_temp_bar.setValue(int(warp_data["core_temperature"]["value"] / 8))
        self.warp_speed_bar.setValue(int(propulsion_data["warp_speed"]["value"] * 10))
        self.field_strength_bar.setValue(int(warp_data["warp_field_strength"]["value"]))
        self.plasma_rate_bar.setValue(int(plasma_data["injection_rate"]["value"] * 200))

        if propulsion_data["warp_speed"]["value"] > 9.0:
            self.status_label.setText("⚠️ DANGER: STRUCTURAL INTEGRITY AT RISK!")
            self.status_label.setStyleSheet("color: red; font-size: 18px; background: rgba(0, 0, 0, 0.7); padding: 10px; border: 2px solid red; border-radius: 10px; text-shadow: 0 0 10px red; box-shadow: 0 0 15px red;")
            self.log_trouble_code("W101", "Warp field exceeding safe structural limits")
        elif warp_data["core_temperature"]["value"] > 700:
            self.status_label.setText("⚠️ DANGER: CORE TEMPERATURE CRITICAL!")
            self.status_label.setStyleSheet("color: red; font-size: 18px; background: rgba(0, 0, 0, 0.7); padding: 10px; border: 2px solid red; border-radius: 10px; text-shadow: 0 0 10px red; box-shadow: 0 0 15px red;")
            self.log_trouble_code("T201", "Warp core temperature approaching critical threshold")
        else:
            self.status_label.setText("🌀 Warp Reactor Status: All Systems Nominal")
            self.status_label.setStyleSheet("color: #00FF00; font-size: 18px; background: rgba(0, 0, 0, 0.7); padding: 10px; border: 2px solid #00FF00; border-radius: 10px; text-shadow: 0 0 10px #00FF00; box-shadow: 0 0 15px #00FF00;")

        self.time_elapsed += 1
        self.warp_series.append(self.time_elapsed, propulsion_data["warp_speed"]["value"])
        self.temp_series.append(self.time_elapsed, warp_data["core_temperature"]["value"])
        self.plasma_series.append(self.time_elapsed, plasma_data["injection_rate"]["value"] * 100)
        if self.time_elapsed > 60:
            self.warp_series.remove(0)
            self.temp_series.remove(0)
            self.plasma_series.remove(0)

    def toggle_backup(self):
        self.backup_group.setVisible(not self.backup_group.isVisible())

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from subsystems.modules.EngineeringSuiteWorker import EngineeringSuiteWorker
    class MockRegistry(dict):
        def add_code(self, worker, code, desc): print(f"MockRegistry: {worker} logged {code}")

    app = QApplication(sys.argv)
    worker = EngineeringSuiteWorker({})
    gui = DaisyEngineeringGUI(worker, MockRegistry())
    gui.show()
    sys.exit(app.exec_())
