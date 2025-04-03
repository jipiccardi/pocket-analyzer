from models.conn import SerialClient
from models.models import Settings
from os import path
import pyqtgraph as pg
from PyQt5.QtCore import Qt

#Path absoluto del file para tener el relativo 
basedir = path.dirname(__file__)
DATA_PATH = path.join(basedir, "./data")
ICON_PATH = path.join(basedir, "./images/Logo Pocket VNA.png")

serial_client = SerialClient()
settings = Settings()

pen_plots = pg.mkPen(color='black', width=1, style=Qt.SolidLine,cosmetic = True)

dict_s2p = {
                "S11":1,
                "S21":3,
                "S22":5,
                "S12":7 
            }

#80b85b
