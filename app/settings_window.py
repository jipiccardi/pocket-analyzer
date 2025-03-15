from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton, QMessageBox
from globals import settings
from models import Settings


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
        self.f_start_text.setValidator(QIntValidator(bottom=0, top=100000))
        self.f_start_text.setText(settings.get_values()['f_init'])
        aux_layout.addWidget(f_start_label)
        aux_layout.addStretch()
        aux_layout.addWidget(self.f_start_text)
        input_layout.addLayout(aux_layout)

        aux_layout = QHBoxLayout()
        f_end_label = QLabel('Frequency End [MHz]')
        self.f_end_text = QLineEdit()
        self.f_end_text.setValidator(QIntValidator(bottom=0, top=100000))
        self.f_end_text.setText(settings.get_values()['f_end'])
        aux_layout.addWidget(f_end_label)
        aux_layout.addStretch()
        aux_layout.addWidget(self.f_end_text)
        input_layout.addLayout(aux_layout)

        aux_layout = QHBoxLayout()
        n_steps_label = QLabel('Number of steps')
        self.n_steps_text = QLineEdit()
        self.n_steps_text.setValidator(QIntValidator(bottom=0, top=100000))
        self.n_steps_text.setText(settings.get_values()['n_step'])
        aux_layout.addWidget(n_steps_label)
        aux_layout.addStretch()
        aux_layout.addWidget(self.n_steps_text)
        input_layout.addLayout(aux_layout)

        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_button_clicked)

        main_layout.addLayout(input_layout)
        main_layout.addStretch()
        main_layout.addWidget(save_button)
        self.setLayout(main_layout)


    def save_button_clicked(self):
        if self.f_start_text.text() == "" or self.f_end_text.text() == "" or self.n_steps_text.text() == "":
            QMessageBox.warning(self, "Input Error", "All values are mandatory.")
            return

        settings.update_values(self.f_start_text.text(), self.f_end_text.text(), self.n_steps_text.text())
        self.close()