import time
from typing import List

from view.dialogs import MeasureDialog,MessageBoxManager
from models.workers import MeasureThread

from models.data_processing import calculate_dut_coefficients
from models.models import MeasuredValue, save_measured_values_to_csv
from models.data_correct_points import apply_extrapole, apply_phase_correction


class MeasureController():
    def __init__(self, parent=None):
        super().__init__(parent)

        self.dut_data: List[MeasuredValue] = []

        self.progress_dialog = MeasureDialog(self)
        task = MeasureThread()
        self.progress_dialog.set_worker_thread(task)
        task.finished_signal.connect(self.measurement_completed)
        task.start()

        self.progress_dialog.exec_()

    def measurement_completed(self, result: List[MeasuredValue]):
        self.progress_dialog.accept()  # Close the dialog
        MessageBoxManager.open_information_box(self, "Success", "Task completed successfully!")

        self.dut_data = result
        for d in self.dut_data:
            d.print_value()
        save_measured_values_to_csv('./data/dut_med.csv',self.dut_data)
        apply_extrapole(1)
        apply_phase_correction(1)
        calculate_dut_coefficients()