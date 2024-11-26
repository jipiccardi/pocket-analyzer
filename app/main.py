import sys

from PyQt5.QtWidgets import QApplication

from conn import SerialClient
from main_window import MainWindow
import logging


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
