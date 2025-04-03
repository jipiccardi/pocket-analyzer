from logging import exception

import pyqtgraph as pg
from PyQt5.QtCore import QFileSystemWatcher, Qt, QFile
from PyQt5.QtWidgets import QMainWindow, QWidget, QTextEdit, QHBoxLayout, QVBoxLayout, QPushButton, QListWidget, \
    QApplication, QStyle, QGridLayout,QLineEdit,QStackedLayout, QLabel, QTabWidget, QComboBox, QSizePolicy
from PyQt5.QtGui import QIcon
from globals import *
from .matplotlib_canvas import smith_chart_canvas


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pocket Analyzer")
        self.setWindowIcon(QIcon(ICON_PATH)) #Seteo icono de la aplicacion

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        self.mid_layout = QGridLayout()

        #Es para probar los estilos
        self.load_stylesheet(basedir+"/view/styles.qss")
        print("El datadir es:",DATA_PATH)

        # Top Layout
        top_widget = QWidget()
        top_widget.setObjectName("topWidget")
        poli = QSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding,QSizePolicy.ControlType.Frame)
        top_widget.setSizePolicy(poli)
        top_widget.setMinimumWidth(self.width())

        self.open_button = QPushButton("Open")
        top_layout.addWidget(self.open_button)
        self.path_sNp_file = None

        self.connect_button = QPushButton("Connect")
        top_layout.addWidget(self.connect_button)

        self.disconnect_button = QPushButton("Disconnect")
        top_layout.addWidget(self.disconnect_button)

        self.settings_button = QPushButton("Settings")
        top_layout.addWidget(self.settings_button)

        self.debug_button = QPushButton("Debug")
        top_layout.addWidget(self.debug_button)

        self.calibrate_button = QPushButton("Calibrate")
        top_layout.addWidget(self.calibrate_button)

        self.start_measure = QPushButton("Start Measure")
        top_layout.addWidget(self.start_measure)

        self.plot_button = QPushButton()
        default_icon = QApplication.style().standardIcon(QStyle.SP_MediaPlay)
        self.plot_button.setIcon(default_icon)
        self.plot_button.setObjectName("plotButton")

        top_layout.addStretch()
        top_layout.addWidget(self.plot_button)

        top_widget.setLayout(top_layout)

        # Mid Layout
        self.plot_type = QComboBox()
        self.plot_type.addItems(["Polar","Complex"])
        

        file_name_label = QLabel("File:")
        self.clear_button = QPushButton("Clear")
        self.clear_button.setObjectName("clearButton")

        #Archivo seleccionado
        self.file_name = QLineEdit()
        self.file_name.setReadOnly(True)
        self.file_name.setText("No file selected")

        aux_Hlayout = QHBoxLayout()
        aux_Hlayout.addWidget(file_name_label)
        aux_Hlayout.addWidget(self.file_name)
        

        #Lista de archivos del directorio por defecto ./data
        self.file_list_widget = QListWidget()

        # Instancia QFileSystemWatcher para actualizar la lista de archivos cuando se agregue o elimine un archivo
        self.directory_watcher = QFileSystemWatcher()
        self.file_watcher = QFileSystemWatcher()
        self.directory_watcher.addPath(DATA_PATH)
        
        self.plot_layout = QStackedLayout()
        self.plot_layout.setCurrentIndex(0)
        self.plot_layout.addWidget(QTextEdit("No file selected"))

        #Graficos que se van a mostrar segun el archivo seleccionado sea .s1p o .s2p
        self.task_tab_s1p = QTabWidget()
        self.task_tab_s2p = QTabWidget()

        #Agrego el grafico de S11 para el caso de archivos .s1p
        self.plot_smith_s1p = smith_chart_canvas()
    
        self.plot_s1p_s11 = pg.GraphicsLayoutWidget()
        self.plot_s1p_s11.setBackground('w')

        self.plot_s1p_s11_mag = self.plot_s1p_s11.addPlot(title="S11 Magnitude",row=0,col=0,color='black')
        self.plot_s1p_s11_mag.setLabel('left', 'Magnitud [dB]', color='black')
        self.plot_s1p_s11_mag.setLabel('bottom', 'Frecuencia [MHz]',color='black')
        self.plot_s1p_s11_pha = self.plot_s1p_s11.addPlot(title="S11 Phase",row=1,col=0)
        self.plot_s1p_s11_pha.setLabel('left', 'Fase [°]', color='black')
        self.plot_s1p_s11_pha.setLabel('bottom', 'Frecuencia [MHz]',color='black')
        self.task_tab_s1p.addTab(self.plot_s1p_s11, "S11")
        self.task_tab_s1p.addTab(self.plot_smith_s1p, "Smith Chart")

        self.plot_layout.setCurrentIndex(1)
        self.plot_layout.addWidget(self.task_tab_s1p)
        
        #Agrego los graficos de S11, S21, S12 y S22 para el caso de archivos .s2p
        self.dict_plots = {}

        self.plot_smith_s2p = smith_chart_canvas()
        
        for key in dict_s2p.keys():
            self.dict_plots[key] = {"Layout":pg.GraphicsLayoutWidget(),"Plot 1":None,"Plot 2":None}

        for key in self.dict_plots.keys():
            self.dict_plots[key]["Layout"].setBackground('w')

            self.dict_plots[key]["Plot 1"] = self.dict_plots[key]["Layout"].addPlot(
                title=f"<span style='color: #80b85b; font-size: 12pt;'>{key} Magnitude</span>"
                ,row=0
                ,col=0)
            
            self.dict_plots[key]["Plot 2"] = self.dict_plots[key]["Layout"].addPlot(
                title=f"<span style='color: #80b85b; font-size: 12pt;'>{key} Phase</span>",
                row=1,
                col=0)
            
            self.task_tab_s2p.addTab(self.dict_plots[key]["Layout"], key)

        self.task_tab_s2p.addTab(self.plot_smith_s2p, "Smith Chart")
        self.plot_layout.setCurrentIndex(2)
        self.plot_layout.addWidget(self.task_tab_s2p)

        self.plot_layout.setCurrentIndex(0)

        self.mid_layout.addLayout(aux_Hlayout, 0,0,1,3)
        self.mid_layout.addWidget(self.plot_type, 0, 4, 1, 1)
        self.mid_layout.addWidget(self.file_list_widget, 1, 0, 10, 3)
        self.mid_layout.addWidget(self.clear_button, 11, 1, 1, 1)
        self.mid_layout.addLayout(self.plot_layout, 1, 4, 11, 14)

        # Main Layout
        main_layout.addWidget(top_widget,0)
        main_layout.addLayout(self.mid_layout,10)

        main_widget.setLayout(main_layout)
        self.mid_layout.setContentsMargins(10,1,10,10)
        main_layout.setContentsMargins(0,0,0,0)
        self.setCentralWidget(main_widget)

        self.showMaximized()
        

    def load_stylesheet(self, filename):
        file = QFile(filename)
        if file.open(QFile.ReadOnly | QFile.Text):
            stylesheet = file.readAll().data().decode("utf-8")
            self.setStyleSheet(stylesheet)