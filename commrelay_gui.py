from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
class CommRelayGUI(QWidget):
    def __init__(self, worker, registry):
        super().__init__()
        self.worker = worker
        self.setWindowTitle("Comm Relay")
        layout = QVBoxLayout(); layout.addWidget(QLabel("Link Stable"))
        self.setLayout(layout)
