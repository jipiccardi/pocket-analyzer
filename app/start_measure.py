import time
from typing import List

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QPushButton, QMessageBox

from data_processing import calculate_dut_coefficients
from globals import serial_client
from models import MeasuredValue, save_measured_values_to_csv


class StartMeasureWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.dut_data: List[MeasuredValue] = []

        self.progress_dialog = MeasureProgressDialog(self)
        task = StartMeasureThread()
        self.progress_dialog.set_worker_thread(task)
        task.finished_signal.connect(self.task_completed)
        task.start()

        self.progress_dialog.exec_()

    def task_completed(self, result: List[MeasuredValue]):
        self.progress_dialog.accept()  # Close the dialog
        QMessageBox.information(self, "Success", "Task completed successfully!")

        self.dut_data = result
        for d in self.dut_data:
            d.print_value()
        save_measured_values_to_csv('./data/dut_med.csv',self.dut_data)
        calculate_dut_coefficients()


class MeasureProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker_thread = None
        self.setWindowTitle("Processing")
        self.setModal(True)
        self.setFixedSize(300, 200)

        self.layout = QVBoxLayout()
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)
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


class StartMeasureThread(QThread):
    finished_signal = pyqtSignal(list)

    def __init__(self):
        super(QThread, self).__init__()

    def run(self):
        serial_client.send_cmd('SM3000000')

        data = []
        eot = False
        while not eot:
            if self.isInterruptionRequested():
                return
            time.sleep(0.00005)

            v = serial_client.receive_value(42)
            # print(v)
            if v.startswith(b'\x02') and v.endswith(b'\x03'):
                print(v)
                measured_value = MeasuredValue(v[4:41])
                measured_value.convert_from_voltage()
                data.append(measured_value)
            if 'END'.encode('UTF-8') in v:
                eot = True
        self.finished_signal.emit(data)




