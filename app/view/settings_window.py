from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QDoubleValidator,QIntValidator
from unicodedata import decimal


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Settings')
        self.setGeometry(300, 300, 500, 500)

        main_layout = QVBoxLayout()

        input_layout = QVBoxLayout()


        aux_layout = QHBoxLayout()
        f_start_label = QLabel('Frequency Start [MHz]')
        self.f_start_text = QLineEdit()

        aux_layout.addWidget(f_start_label)
        aux_layout.addStretch()
        aux_layout.addWidget(self.f_start_text)
        input_layout.addLayout(aux_layout)

        aux_layout = QHBoxLayout()
        f_end_label = QLabel('Frequency End [MHz]')
        self.f_end_text = QLineEdit()
        
        aux_layout.addWidget(f_end_label)
        aux_layout.addStretch()
        aux_layout.addWidget(self.f_end_text)
        input_layout.addLayout(aux_layout)

        aux_layout = QHBoxLayout()
        n_steps_label = QLabel('Number of steps')
        self.n_steps_text = QLineEdit()
        
        aux_layout.addWidget(n_steps_label)
        aux_layout.addStretch()
        aux_layout.addWidget(self.n_steps_text)
        input_layout.addLayout(aux_layout)

        self.f_start_text.setValidator(QDoubleValidator(bottom=0, top=3000.0, decimals= 1))
        self.f_end_text.setValidator(QDoubleValidator(bottom=0, top=3000.0, decimals= 1))
        self.n_steps_text.setValidator(QIntValidator(bottom=0, top=235))


        self.save_button = QPushButton('Save')
        
        main_layout.addLayout(input_layout)
        main_layout.addStretch()
        main_layout.addWidget(self.save_button)
        self.setLayout(main_layout)
