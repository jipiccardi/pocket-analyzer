from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QCheckBox, QFormLayout, QLineEdit, QGridLayout, \
    QHBoxLayout

from globals import serial_client


def show_debug_window():
    window = DebugWindow()
    window.exec_()


def send_frequency(value: int):
    serial_client.send_cmd(f'FREQ={value}')


def send_power(value: int):
    serial_client.send_cmd(f'PWR={value}')


class DebugWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Debug")
        self.setGeometry(500, 500, 1000, 600)

        main_layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()

        legend_label = QLabel("Manage GPIO")
        main_layout.addWidget(legend_label)

        checkbox_layout = QGridLayout()
        self.checkboxes = {}
        for i in range(1, 15):
            checkbox = GPIOCheckBox(f'GPIO-{i}', i)
            checkbox.stateChanged.connect(self.gpio_status_changed)
            row = (i - 1) // 3
            col = (i - 1) % 3
            checkbox_layout.addWidget(checkbox, row, col)
            self.checkboxes[i] = checkbox

        frequency_layout = QFormLayout()
        self.frequency_input = QLineEdit()
        self.frequency_input.setValidator(QIntValidator(0, 100000))
        frequency_send_button = QPushButton("Send Frequency")
        frequency_send_button.clicked.connect(lambda: send_frequency(self.frequency_input.text()))
        frequency_layout.addRow("Frequency [MHz]:", self.frequency_input)
        frequency_layout.addWidget(frequency_send_button)

        power_layout = QFormLayout()
        self.power_input = QLineEdit()
        self.power_input.setValidator(QIntValidator(0, 100000))
        power_send_button = QPushButton("Send Power")
        power_send_button.clicked.connect(lambda: send_power(self.power_input.text()))
        power_layout.addRow("Power:", self.power_input)
        power_layout.addWidget(power_send_button)

        bottom_layout.addLayout(frequency_layout)
        bottom_layout.addLayout(power_layout)

        top_layout.addLayout(checkbox_layout)
        top_layout.addStretch()

        main_layout.addLayout(top_layout)
        main_layout.addSpacing(100)
        main_layout.addLayout(bottom_layout)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def gpio_status_changed(self, state):
        sender = self.sender()
        if isinstance(sender, GPIOCheckBox):
            print(f"GPIO {sender.gpio_id} state changed to {state}")


class GPIOCheckBox(QCheckBox):
    def __init__(self, text, gpio_id, parent=None):
        super().__init__(text, parent)
        self.gpio_id = gpio_id
