from PyQt5.QtWidgets import QMainWindow, QWidget, QTextEdit, QHBoxLayout, QVBoxLayout, QPushButton, QListWidget
from globals import serial_client
from debug_window import DebugWindow
from connect_window import ConnectWindow
from calibrate_window import CalibrateWindow
from settings_window import SettingsWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        mid_layout = QHBoxLayout()

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

        top_layout.addStretch()

        # Mid Layout
        self.file_list_widget = QListWidget()
        plot = QTextEdit("Plot View")
        plot.setEnabled(False)
        mid_layout.addWidget(self.file_list_widget, 1)
        mid_layout.addWidget(plot, 8)

        # Main Layout
        main_layout.addLayout(top_layout, 1)
        main_layout.addLayout(mid_layout, 15)

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

    def refresh_buttons(self, is_connected: bool):
        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
        self.debug_button.setEnabled(False)
        self.calibrate_button.setEnabled(False)

        if is_connected:
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
            self.debug_button.setEnabled(True)
            self.calibrate_button.setEnabled(True)

    def disconnect_button_clicked(self):
        serial_client.disconnect()
        self.refresh_buttons(False)
