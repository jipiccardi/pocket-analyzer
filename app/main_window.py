import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QTextEdit, QHBoxLayout, QVBoxLayout, QPushButton, QListWidget
from PyQt5.QtGui import QIcon
from main_window_dialogs import StartMeasurementWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        mid_layout = QHBoxLayout()

        # Top Layout
        start_button = QPushButton("Start")
        start_button.clicked.connect(self.start_measurement)  # Connect button to the dialog function
        top_layout.addWidget(start_button)
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

    def start_measurement(self):
        popup = StartMeasurementWindow(self)
        popup.exec_()

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



