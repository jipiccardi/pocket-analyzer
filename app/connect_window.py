import serial.tools.list_ports
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton
from PyQt5.QtCore import pyqtSignal

from globals import serial_client


class ConnectWindow(QDialog):
    connection_established_signal = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(250, 250, 500, 300)

        main_layout = QVBoxLayout()

        self.port_list = QListWidget()
        self.port_list.currentItemChanged.connect(self.update_connect_button_state)

        self.connect_button = QPushButton('Connect')
        self.connect_button.setEnabled(False)
        self.connect_button.clicked.connect(self.connect_to_selected_port)

        refresh_button = QPushButton('Refresh')
        refresh_button.clicked.connect(self.refresh_button)

        main_layout.addWidget(self.port_list)
        main_layout.addWidget(refresh_button)
        main_layout.addWidget(self.connect_button)

        self.setLayout(main_layout)
        self.refresh_button()

    def refresh_button(self):
        self.port_list.clear()
        ports = serial.tools.list_ports.comports()

        for port in ports:
            self.port_list.addItem(port.device)

    def update_connect_button_state(self):
        self.connect_button.setEnabled(self.port_list.currentItem() is not None)

    def connect_to_selected_port(self):
        if self.port_list.currentItem():
            serial_client.connect(self.port_list.currentItem().text())
            self.connection_established_signal.emit(True)
            self.accept()
