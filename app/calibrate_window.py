import time
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QProgressDialog
from PyQt5.QtCore import Qt, QTimer

from debug_window import DebugWindow
from globals import serial_client


def show_calibrate_window():
    window = CalibrateWindow()
    window.exec_()


class CalibrateWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calibrate Window")
        self.setGeometry(250, 250, 1000, 600)

        main_layout = QVBoxLayout()
        buttons_layout = QGridLayout()

        match_1_btn = QPushButton("Match 1")
        match_1_btn.clicked.connect(lambda: self.run_calib('MTC000001'))
        match_2_btn = QPushButton("Match 2")
        match_2_btn.clicked.connect(self.run_calib)
        open_1_btn = QPushButton("Open 1")
        open_1_btn.clicked.connect(self.run_calib)
        open_2_btn = QPushButton("Open 2")
        open_2_btn.clicked.connect(self.run_calib)
        short_1_btn = QPushButton("Short 1")
        short_1_btn.clicked.connect(self.run_calib)
        short_2_btn = QPushButton("Short 2")
        short_2_btn.clicked.connect(self.run_calib)
        through_btn = QPushButton("Through")
        through_btn.clicked.connect(self.run_calib)

        buttons_layout.addWidget(match_1_btn, 0, 0)
        buttons_layout.addWidget(match_2_btn, 0, 1)
        buttons_layout.addWidget(open_1_btn, 0, 2)
        buttons_layout.addWidget(open_2_btn, 1, 0)
        buttons_layout.addWidget(short_1_btn, 1, 1)
        buttons_layout.addWidget(short_2_btn, 1, 2)
        buttons_layout.addWidget(through_btn, 2, 0)

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    def run_calib(self, cmd: str):
        serial_client.send_cmd(cmd)

        progress_dialog = QProgressDialog("Running task...", "Cancel", 0, 100, self)
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setAutoClose(True)
        progress_dialog.setAutoReset(True)
        progress_dialog.show()

        for i in range(101):
            print('hola')
            time.sleep(0.05)  # Simulate a task taking time
            progress_dialog.setValue(i)
            if progress_dialog.wasCanceled():
                break
