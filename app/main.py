import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from main_window import MainWindow
import logging


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    app = QApplication(sys.argv)

    font = QFont()
    font.setPointSize(12)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
