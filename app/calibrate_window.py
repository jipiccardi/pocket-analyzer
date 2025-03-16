
import time

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QPushButton, QProgressBar, QMessageBox, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal

from globals import serial_client, settings
from typing import List
from models import MeasuredValue, save_measured_values_to_csv, Settings
from debug_window import send_frequency_low,send_frequency_high,send_frequency_step


class CalibrateWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress_dialog = None
        self.setWindowTitle("Calibrate Window")
        self.setGeometry(250, 250, 1000, 600)

        # Calib results
        self.match1_data: List[MeasuredValue] = []
        self.match2_data: List[MeasuredValue] = []
        self.open1_data: List[MeasuredValue] = []
        self.open2_data: List[MeasuredValue] = []
        self.short1_data: List[MeasuredValue] = []
        self.short2_data: List[MeasuredValue] = []
        self.thru: List[MeasuredValue] = []

        main_layout = QVBoxLayout()
        buttons_layout = QGridLayout()

        self.match_1_btn = QPushButton('Match 1')
        self.match_1_btn.clicked.connect(lambda: self.calib_button_clicked('MTC1','SM1000000'))

        self.match_2_btn = QPushButton("Match 2")
        self.match_2_btn.clicked.connect(lambda: self.calib_button_clicked('MTC2','SM1000000'))

        self.open_1_btn = QPushButton("Open 1")
        self.open_1_btn.clicked.connect(lambda: self.calib_button_clicked('OP1','SM1000000'))

        self.open_2_btn = QPushButton("Open 2")
        self.open_2_btn.clicked.connect(lambda: self.calib_button_clicked('OP2','SM1000000'))

        self.short_1_btn = QPushButton("Short 1")
        self.short_1_btn.clicked.connect(lambda: self.calib_button_clicked('SH1','SM1000000'))

        self.short_2_btn = QPushButton("Short 2")
        self.short_2_btn.clicked.connect(lambda: self.calib_button_clicked('SH2','SM1000000'))

        self.thru_btn = QPushButton("Thru")
        self.thru_btn.clicked.connect(lambda: self.calib_button_clicked('THR','SM1000000'))

        buttons_layout.addWidget(self.match_1_btn, 0, 0)
        buttons_layout.addWidget(self.match_2_btn, 0, 1)
        buttons_layout.addWidget(self.open_1_btn, 0, 2)
        buttons_layout.addWidget(self.open_2_btn, 1, 0)
        buttons_layout.addWidget(self.short_1_btn, 1, 1)
        buttons_layout.addWidget(self.short_2_btn, 1, 2)
        buttons_layout.addWidget(self.thru_btn, 2, 1)

        main_layout.addLayout(buttons_layout)

        aux_layout = QHBoxLayout()
        aux_layout.addStretch()
        self.apply_button = QPushButton('Apply')

        aux_layout.addWidget(self.apply_button)

        main_layout.addLayout(aux_layout)

        self.setLayout(main_layout)

    def calib_button_clicked(self, calib_mode: str, cmd: str):
        self.progress_dialog = ProgressDialog(self)
        task = CalibThread(calib_mode, cmd)
        self.progress_dialog.set_worker_thread(task)
        task.finished_signal.connect(self.task_completed)
        task.start()

        self.progress_dialog.exec_()

    def task_completed(self, calib_mode: str, result: List[MeasuredValue]):
        self.progress_dialog.accept()  # Close the dialog
        QMessageBox.information(self, "Success", "Task completed successfully!")

        if calib_mode == 'MTC1':
            self.match1_data = result
            for d in self.match1_data:
                d.print_value()
            save_measured_values_to_csv('./data/match1.csv', self.match1_data)
            self.match_1_btn.setStyleSheet("background-color: green")
        elif calib_mode == 'MTC2':
            self.match2_data = result
            for d in self.match2_data:
                d.print_value()
            save_measured_values_to_csv('./data/match2.csv',self.match2_data)
            self.match_2_btn.setStyleSheet("background-color: green")
        elif calib_mode == 'OP1':
            self.open1_data = result
            for d in self.open1_data:
                d.print_value()
            save_measured_values_to_csv('./data/open1.csv',self.open1_data)
            self.open_1_btn.setStyleSheet("background-color: green")
        elif calib_mode == 'OP2':
            self.open2_data = result
            for d in self.open2_data:
                d.print_value()
            save_measured_values_to_csv('./data/open2.csv',self.open2_data)
            self.open_2_btn.setStyleSheet("background-color: green")
        elif calib_mode == 'SH1':
            self.short1_data = result
            for d in self.short1_data:
                d.print_value()
            save_measured_values_to_csv('./data/short1.csv',self.short1_data)
            self.short_1_btn.setStyleSheet("background-color: green")
        elif calib_mode == 'SH2':
            self.short2_data = result
            for d in self.short2_data:
                d.print_value()
            save_measured_values_to_csv('./data/short2.csv',self.short2_data)
            self.short_2_btn.setStyleSheet("background-color: green")
        elif calib_mode == 'THR':
            self.thru = result
            for d in self.thru:
                d.print_value()
            save_measured_values_to_csv('./data/thru.csv',self.thru)
            self.thru_btn.setStyleSheet("background-color: green")


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
    finished_signal = pyqtSignal(str, list)

    def __init__(self, calib_mode: str, cmd: str):
        super(QThread, self).__init__()
        self.cmd = cmd
        self.calib_mode = calib_mode

    def run(self):
        serial_client.send_cmd(self.cmd)
        # send_frequency_low(settings.get_frequency_low())
        # send_frequency_high(settings.get_frequency_high())

        data = []
        eot = False
        v = b""
        print(v)
        while not eot:
            if self.isInterruptionRequested():
                return
            time.sleep(0.00005)
            if self.cmd == 'SM1000000' or self.cmd == 'SM2000000':
                v = serial_client.receive_value(18)
                if v.startswith(b'\x02') and v.endswith(b'\x03'):
                    print(v)
                    measured_value = MeasuredValue(v[4:17])
                    #measured_value.convert_from_voltage()
                    data.append(measured_value)
            #if self.cmd == 'SM3000000':
            #    v = serial_client.receive_value(42)
            #    if v.startswith(b'\x02') and v.endswith(b'\x03'):
            #        data.append(MeasuredValue(v[4:17]))
            if 'END'.encode('UTF-8') in v:
                eot = True

        self.finished_signal.emit(self.calib_mode, data)
