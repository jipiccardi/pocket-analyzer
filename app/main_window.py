import os

import serial.tools.list_ports
from PyQt5.QtWidgets import QMainWindow, QWidget, QTextEdit, QHBoxLayout, QVBoxLayout, QPushButton, QListWidget
from PyQt5.QtGui import QIcon
from conn import SerialClient, get_available_ports

serial_client = SerialClient()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        mid_layout = QHBoxLayout()

        # Top Layout
        connect_button = QPushButton("Connect")
        connect_button.clicked.connect(lambda: serial_client.connect('COM6'))
        top_layout.addWidget(connect_button)

        disconnect_button = QPushButton("Disconnect")
        disconnect_button.clicked.connect(serial_client.disconnect)
        top_layout.addWidget(disconnect_button)

        show_ports_button = QPushButton("Show ports")
        show_ports_button.clicked.connect(get_available_ports)
        top_layout.addWidget(show_ports_button)

        for i in range(0, 4):
            # TODO iterate array of already configured buttons

            buttons = QPushButton("...")
            top_layout.addWidget(buttons)
        top_layout.addStretch()

        # Mid Layout
        self.file_list_widget = QListWidget()
        plot = QTextEdit("Plot View")
        file_view = QTextEdit("File View")
        mid_layout.addWidget(self.file_list_widget, 1)
        mid_layout.addWidget(plot, 8)

        self.load_files_from_directory("./data")

        # Main Layout
        main_layout.addLayout(top_layout, 1)
        main_layout.addLayout(mid_layout, 15)

        main_widget.setLayout(main_layout)
        self.setWindowTitle("Pocket Analyzer")

        self.showMaximized()

    def load_files_from_directory(self, directory):
        # Limpiar el QListWidget antes de agregar nuevos archivos
        self.file_list_widget.clear()

        # Obtener la lista de archivos en el directorio
        try:
            files = os.listdir(directory)
            for file in files:
                # Agregar archivo a la lista
                self.file_list_widget.addItem(file)
        except FileNotFoundError:
            self.file_list_widget.addItem("Directory not found")



