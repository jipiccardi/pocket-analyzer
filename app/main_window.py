from logging import exception

import pyqtgraph as pg
from PyQt5.QtWidgets import QMainWindow, QWidget, QTextEdit, QHBoxLayout, QVBoxLayout, QPushButton, QListWidget, \
    QApplication, QStyle, QMessageBox, QGridLayout
from globals import serial_client
from debug_window import DebugWindow
from connect_window import ConnectWindow
from calibrate_window import CalibrateWindow
from settings_window import SettingsWindow
from start_measure import StartMeasureWindow
import pandas as pd

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        self.mid_layout = QGridLayout()


        # Top Layout
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.show_connect_window)
        top_layout.addWidget(self.connect_button)

        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.clicked.connect(self.disconnect_button_clicked)
        top_layout.addWidget(self.disconnect_button)

        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.show_settings_window)
        top_layout.addWidget(self.settings_button)

        self.debug_button = QPushButton("Debug")
        self.debug_button.clicked.connect(self.show_debug_window)
        top_layout.addWidget(self.debug_button)

        self.calibrate_button = QPushButton("Calibrate")
        self.calibrate_button.clicked.connect(self.show_calibrate_window)
        top_layout.addWidget(self.calibrate_button)

        self.start_measure = QPushButton("Start Measure")
        self.start_measure.clicked.connect(self.show_start_measure_window)
        top_layout.addWidget(self.start_measure)

        self.plot_button = QPushButton()
        default_icon = QApplication.style().standardIcon(QStyle.SP_MediaPlay)
        self.plot_button.setIcon(default_icon)
        self.plot_button.clicked.connect(self.plot_button_clicked)

        top_layout.addStretch()
        top_layout.addWidget(self.plot_button)

        # Mid Layout

        # Main Layout
        main_layout.addLayout(top_layout)
        main_layout.addLayout(self.mid_layout)
        main_layout.addStretch()

        main_widget.setLayout(main_layout)
        self.setWindowTitle("Pocket Analyzer")

        self.set_buttons_initial_status()

        self.showMaximized()

    def show_connect_window(self):
        connect_window = ConnectWindow(self)
        connect_window.connection_established_signal.connect(self.refresh_buttons)
        connect_window.exec_()

    def show_debug_window(self):
        debug_window = DebugWindow(self)
        debug_window.exec_()

    def show_start_measure_window(self):
        measure_window = StartMeasureWindow(self)
        measure_window.exec_()

    def show_calibrate_window(self):
        calib_window = CalibrateWindow(self)
        calib_window.exec_()

    def show_settings_window(self):
        settings_window = SettingsWindow(self)
        settings_window.exec_()

    def set_buttons_initial_status(self):
        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
        self.debug_button.setEnabled(False)
        self.calibrate_button.setEnabled(False)
        self.start_measure.setEnabled(False)

    def refresh_buttons(self, is_connected: bool):
        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
        self.debug_button.setEnabled(False)
        self.calibrate_button.setEnabled(False)
        self.start_measure.setEnabled(False)

        if is_connected:
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
            self.debug_button.setEnabled(True)
            self.calibrate_button.setEnabled(True)
            self.start_measure.setEnabled(True)

    def disconnect_button_clicked(self):
        serial_client.disconnect()
        self.refresh_buttons(False)

    def plot_button_clicked(self):
        try:
            df = pd.read_csv("./data/dut_c.csv")

            # Define the columns to plot
            columns = ["s11_mag", "s11_pha", "s21_mag", "s21_pha",
                       "s22_mag", "s22_pha", "s12_mag", "s12_pha"]

            # Create plots in a 4x2 grid
            for i, col in enumerate(columns):
                plot_widget = pg.PlotWidget()
                plot_widget.setBackground('white')

                plot_widget.plot(df["freq"], df[col], pen="k", name=col)
                plot_widget.setLabel("left", col)
                plot_widget.setLabel("bottom", "Frequency")
                self.mid_layout.addWidget(plot_widget, i // 2, i % 2)

        except Exception as e:  # Catch all exceptions
            QMessageBox.warning(self, "Warning", "No file available")

