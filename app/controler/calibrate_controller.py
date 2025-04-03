from view.calibrate_window import CalibrateWindow
from view.dialogs import MessageBoxManager,ProgressDialog
from typing import List
from models.models import MeasuredValue, save_measured_values_to_csv
from models.workers import CalibThread
from models.data_processing import calculate_error_coefficients
from models.data_correct_points import apply_extrapole, apply_phase_correction
from graphics_generation import graphic_generation

class CalibrateController():
    def __init__(self,main_window = None):

        self.view = CalibrateWindow(main_window)

        # Calib results
        self.match1_data: List[MeasuredValue] = []
        self.match2_data: List[MeasuredValue] = []
        self.open1_data: List[MeasuredValue] = []
        self.open2_data: List[MeasuredValue] = []
        self.short1_data: List[MeasuredValue] = []
        self.short2_data: List[MeasuredValue] = []
        self.thru: List[MeasuredValue] = []

        self.view.match_1_btn.clicked.connect(lambda: self.calib_button_clicked('MTC1','SM1000000'))
        self.view.match_2_btn.clicked.connect(lambda: self.calib_button_clicked('MTC2','SM2000000'))
        self.view.open_1_btn.clicked.connect(lambda: self.calib_button_clicked('OP1','SM1000000'))
        self.view.open_2_btn.clicked.connect(lambda: self.calib_button_clicked('OP2','SM2000000'))
        self.view.short_1_btn.clicked.connect(lambda: self.calib_button_clicked('SH1','SM1000000'))
        self.view.short_2_btn.clicked.connect(lambda: self.calib_button_clicked('SH2','SM2000000'))
        self.view.thru_btn.clicked.connect(lambda: self.calib_button_clicked('THR','SM3000000'))
        self.view.apply_button.clicked.connect(self.apply_button_clicked)
    
    def apply_button_clicked(self):
        
        apply_extrapole()
        apply_phase_correction()
        graphic_generation()
        calculate_error_coefficients()
        MessageBoxManager.open_information_box(title= "Success", caption="Apply completed succesfully!")

    def calib_button_clicked(self, calib_mode: str, cmd: str):
        self.view.progress_dialog = ProgressDialog(self.view)
        task = CalibThread(calib_mode, cmd)
        self.view.progress_dialog.set_worker_thread(task)
        task.finished_signal.connect(self.task_completed)
        task.start()
        self.view.progress_dialog.exec_()

    def task_completed(self, calib_mode: str, result: List[MeasuredValue]):
        self.view.progress_dialog.accept()  # Close the dialog
        MessageBoxManager.open_information_box( title="Success", caption="Task completed successfully!")

        if calib_mode == 'MTC1':
            self.match1_data = result
            for d in self.match1_data:
                d.print_value()
            save_measured_values_to_csv('./data/match1.csv', self.match1_data)
            self.view.match_1_btn.setStyleSheet("background-color: green")
        elif calib_mode == 'MTC2':
            self.match2_data = result
            for d in self.match2_data:
                d.print_value()
            save_measured_values_to_csv('./data/match2.csv',self.match2_data)
            self.view.match_2_btn.setStyleSheet("background-color: green")
        elif calib_mode == 'OP1':
            self.open1_data = result
            for d in self.open1_data:
                d.print_value()
            save_measured_values_to_csv('./data/open1.csv',self.open1_data)
            self.view.open_1_btn.setStyleSheet("background-color: green")
        elif calib_mode == 'OP2':
            self.open2_data = result
            for d in self.open2_data:
                d.print_value()
            save_measured_values_to_csv('./data/open2.csv',self.open2_data)
            self.view.open_2_btn.setStyleSheet("background-color: green")
        elif calib_mode == 'SH1':
            self.short1_data = result
            for d in self.short1_data:
                d.print_value()
            save_measured_values_to_csv('./data/short1.csv',self.short1_data)
            self.view.short_1_btn.setStyleSheet("background-color: green")
        elif calib_mode == 'SH2':
            self.short2_data = result
            for d in self.short2_data:
                d.print_value()
            save_measured_values_to_csv('./data/short2.csv',self.short2_data)
            self.view.short_2_btn.setStyleSheet("background-color: green")
        elif calib_mode == 'THR':
            self.thru = result
            for d in self.thru:
                d.print_value()
            save_measured_values_to_csv('./data/thru.csv',self.thru)
            self.view.thru_btn.setStyleSheet("background-color: green")
