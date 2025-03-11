
import time

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QPushButton, QProgressBar, QMessageBox
from PyQt5.QtCore import Qt,QThread,pyqtSignal

from globals import serial_client
from typing import List
from models import MeasuredValue,save_measured_values_to_csv


class CalibrateWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress_dialog = None
        self.setWindowTitle("Calibrate Window")
        self.setGeometry(250, 250, 1000, 600)

        # Calib results
        self.match1_data: List[MeasuredValue] = []

        main_layout = QVBoxLayout()
        buttons_layout = QGridLayout()

        match_1_btn = QPushButton('Match 1')
        match_1_btn.clicked.connect(lambda: self.calib_button_clicked('MTC000001'))

        match_2_btn = QPushButton("Match 2")
        match_2_btn.setEnabled(False)
        match_2_btn.clicked.connect(self.calib_button_clicked)

        open_1_btn = QPushButton("Open 1")
        open_1_btn.setEnabled(False)
        open_1_btn.clicked.connect(self.calib_button_clicked)

        open_2_btn = QPushButton("Open 2")
        open_2_btn.setEnabled(False)
        open_2_btn.clicked.connect(self.calib_button_clicked)

        short_1_btn = QPushButton("Short 1")
        short_1_btn.setEnabled(False)
        short_1_btn.clicked.connect(self.calib_button_clicked)

        short_2_btn = QPushButton("Short 2")
        short_2_btn.setEnabled(False)
        short_2_btn.clicked.connect(self.calib_button_clicked)

        through_btn = QPushButton("Through")
        through_btn.setEnabled(False)
        through_btn.clicked.connect(self.calib_button_clicked)

        buttons_layout.addWidget(match_1_btn, 0, 0)
        buttons_layout.addWidget(match_2_btn, 0, 1)
        buttons_layout.addWidget(open_1_btn, 0, 2)
        buttons_layout.addWidget(open_2_btn, 1, 0)
        buttons_layout.addWidget(short_1_btn, 1, 1)
        buttons_layout.addWidget(short_2_btn, 1, 2)
        buttons_layout.addWidget(through_btn, 2, 0)

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    def calib_button_clicked(self, cmd: str):
        self.progress_dialog = ProgressDialog(self)
        task = CalibThread(cmd)
        self.progress_dialog.set_worker_thread(task)
        task.finished_signal.connect(self.task_completed)
        task.start()

        self.progress_dialog.exec_()

    def task_completed(self, result: List[MeasuredValue]):
        self.progress_dialog.accept()  # Close the dialog
        QMessageBox.information(self, "Success", "Task completed successfully!")

        self.match1_data = result
        for d in self.match1_data:
            d.print_value()
        save_measured_values_to_csv('./data/match1.csv', self.match1_data)


class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker_thread = None
        self.setWindowTitle("Processing")
        self.setModal(True)
        self.setFixedSize(300, 200)

        self.layout = QVBoxLayout()
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # Infinite progress
        self.layout.addWidget(self.progress_bar)

        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.cancel_task)
        self.layout.addWidget(self.cancel_button)

        self.setLayout(self.layout)

    def set_worker_thread(self, thread):
        self.worker_thread = thread

    def cancel_task(self):
        if self.worker_thread:
            self.worker_thread.requestInterruption()  # Gracefully stop the thread
        self.reject()  # Close dialog


class CalibThread(QThread):
    finished_signal = pyqtSignal(list)

    def __init__(self, cmd: str, parent=None):
        super(QThread, self).__init__()
        self.cmd = cmd

    def run(self):
        serial_client.send_cmd(self.cmd)

        data = []
        eot = False
        while not eot:
        #for _ in range(1000):
            if self.isInterruptionRequested():
                return
            time.sleep(0.00005)
            v = serial_client.receive_value()
            #v = b'\x02fffff2222333344445555\x03'
            if v.startswith(b'\x02') and v.endswith(b'\x03'):
                print(v)
                data.append(MeasuredValue(v[4:25]))
            if 'Termine'.encode('UTF-8') in v:
                eot = True

        self.finished_signal.emit(data)
