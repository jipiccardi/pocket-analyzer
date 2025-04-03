from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QPushButton, QProgressBar, QMessageBox, QHBoxLayout

class CalibrateWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress_dialog = None
        self.setWindowTitle("Calibrate Window")
        self.setGeometry(250, 250, 1000, 600)

        main_layout = QVBoxLayout()
        buttons_layout = QGridLayout()

        self.match_1_btn = QPushButton('Match 1')
        self.match_2_btn = QPushButton("Match 2")
        self.open_1_btn = QPushButton("Open 1")
        self.open_2_btn = QPushButton("Open 2")
        self.short_1_btn = QPushButton("Short 1")
        self.short_2_btn = QPushButton("Short 2")
        self.thru_btn = QPushButton("Thru")
        
        buttons_layout.addWidget(self.match_1_btn, 0, 0)
        buttons_layout.addWidget(self.match_2_btn, 0, 1)
        buttons_layout.addWidget(self.open_1_btn, 0, 2)
        buttons_layout.addWidget(self.open_2_btn, 1, 0)
        buttons_layout.addWidget(self.short_1_btn, 1, 1)
        buttons_layout.addWidget(self.short_2_btn, 1, 2)
        buttons_layout.addWidget(self.thru_btn, 2, 1)

        main_layout.addLayout(buttons_layout)

        aux_layout = QHBoxLayout()
        aux_layout.addStretch()
        self.apply_button = QPushButton('Apply')

        aux_layout.addWidget(self.apply_button)

        main_layout.addLayout(aux_layout)

        self.setLayout(main_layout)


