import sys

from PyQt5.QtGui import QFont,QIcon
from PyQt5.QtWidgets import QApplication

from main_window import MainWindow,ICON_PATH
import logging
import ctypes



def main():
    logging.getLogger().setLevel(logging.DEBUG)

    #Esto es solo para sistemas windows para que se vea el icono en la barra de tareas
    app_id = "pocket_analyzer.app"  # Identificador único
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(ICON_PATH))

    font = QFont()
    font.setPointSize(12)
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
