from logging import exception

import os
from os import listdir,path
from pathlib import Path

import pyqtgraph as pg
from PyQt5.QtCore import QFileSystemWatcher
from PyQt5.QtWidgets import QMainWindow, QWidget, QTextEdit, QHBoxLayout, QVBoxLayout, QPushButton, QListWidget, \
    QApplication, QStyle, QMessageBox, QGridLayout, QFileDialog,QLineEdit,QStackedLayout, QLabel, QTabWidget
from PyQt5.QtGui import QIcon
from globals import serial_client, dict_s2p,stylesheet_tabs
from debug_window import DebugWindow
from connect_window import ConnectWindow
from calibrate_window import CalibrateWindow
from settings_window import SettingsWindow
from start_measure import StartMeasureWindow
import pandas as pd

#Path absoluto del file para tener el relativo 
basedir = path.dirname(__file__)
DATA_PATH = path.join(basedir, "./data")
ICON_PATH = path.join(basedir, "./images/icono.png")

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

        print("El datadir es:",DATA_PATH)

        # Top Layout
        self.open_button = QPushButton("Open")
        self.open_button.clicked.connect(self.open_file_dialog)
        top_layout.addWidget(self.open_button)
        self.path_sNp_file = None

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.show_connect_window)
        top_layout.addWidget(self.connect_button)

        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.clicked.connect(self.disconnect_button_clicked)
        top_layout.addWidget(self.disconnect_button)

        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.show_settings_window)
        top_layout.addWidget(self.settings_button)

        self.debug_button = QPushButton("Debug")
        self.debug_button.clicked.connect(self.show_debug_window)
        top_layout.addWidget(self.debug_button)

        self.calibrate_button = QPushButton("Calibrate")
        self.calibrate_button.clicked.connect(self.show_calibrate_window)
        top_layout.addWidget(self.calibrate_button)

        self.start_measure = QPushButton("Start Measure")
        self.start_measure.clicked.connect(self.show_start_measure_window)
        top_layout.addWidget(self.start_measure)

        self.plot_button = QPushButton()
        default_icon = QApplication.style().standardIcon(QStyle.SP_MediaPlay)
        self.plot_button.setIcon(default_icon)
        self.plot_button.clicked.connect(self.plot_button_clicked)

        top_layout.addStretch()
        top_layout.addWidget(self.plot_button)

        # Mid Layout
        file_name_label = QLabel("File:")
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_screen)

        #Archivo seleccionado
        self.file_name = QLineEdit()
        self.file_name.setReadOnly(True)
        self.file_name.setText("No file selected")

        aux_Hlayout = QHBoxLayout()
        aux_Hlayout.addWidget(file_name_label)
        aux_Hlayout.addWidget(self.file_name)

        #Lista de archivos del directorio por defecto ./data
        self.file_list_widget = QListWidget()
        self.load_files_from_directory(DATA_PATH)
        self.file_list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)

        # Instancia QFileSystemWatcher para actualizar la lista de archivos cuando se agregue o elimine un archivo
        self.directory_watcher = QFileSystemWatcher()
        self.file_watcher = QFileSystemWatcher()
        self.directory_watcher.addPath(DATA_PATH)
        self.directory_watcher.directoryChanged.connect(self.on_directory_changed)
        
        self.plot_layout = QStackedLayout()
        self.plot_layout.setCurrentIndex(0)
        self.plot_layout.addWidget(QTextEdit("No file selected"))

        #Graficos que se van a mostrar segun el archivo seleccionado sea .s1p o .s2p
        self.task_tab_s1p = QTabWidget()
        self.task_tab_s2p = QTabWidget()

        self.task_tab_s1p.setStyleSheet(stylesheet_tabs)
        self.task_tab_s2p.setStyleSheet(stylesheet_tabs)

        #Agrego el grafico de S11 para el caso de archivos .s1p
        self.plot_s1p_s11 = pg.GraphicsLayoutWidget()
        self.plot_s1p_s11.setBackground('w')

        self.plot_s1p_s11_mag = self.plot_s1p_s11.addPlot(title="S11 Magnitude",row=0,col=0,color='black')
        self.plot_s1p_s11_mag.setLabel('left', 'Magnitud [dB]', color='black')
        self.plot_s1p_s11_mag.setLabel('bottom', 'Frecuencia [MHz]',color='black')
        self.plot_s1p_s11_pha = self.plot_s1p_s11.addPlot(title="S11 Phase",row=1,col=0)
        self.plot_s1p_s11_pha.setLabel('left', 'Fase [°]', color='black')
        self.plot_s1p_s11_pha.setLabel('bottom', 'Frecuencia [MHz]',color='black')
        self.task_tab_s1p.addTab(self.plot_s1p_s11, "S11")

        self.plot_layout.setCurrentIndex(1)
        self.plot_layout.addWidget(self.task_tab_s1p)
        
        #Agrego los graficos de S11, S21, S12 y S22 para el caso de archivos .s2p
        self.dict_plots = {}
        
        for key in dict_s2p.keys():
            self.dict_plots[key] = {"Layout":pg.GraphicsLayoutWidget(),"Magnitude":None,"Phase":None}

        for key in self.dict_plots.keys():
            self.dict_plots[key]["Layout"].setBackground('w')

            self.dict_plots[key]["Magnitude"] = self.dict_plots[key]["Layout"].addPlot(
                title=f"<span style='color: #80b85b; font-size: 12pt;'>{key} Magnitude</span>"
                ,row=0
                ,col=0)
            self.dict_plots[key]["Magnitude"].setLabel('left', 'Magnitud [dB]', color='black')
            self.dict_plots[key]["Magnitude"].setLabel('bottom', 'Frecuencia [MHz]',color='black')
            self.dict_plots[key]["Magnitude"].showGrid(x=True, y=True, alpha=0.5)
            self.dict_plots[key]["Phase"] = self.dict_plots[key]["Layout"].addPlot(
                title=f"<span style='color: #80b85b; font-size: 12pt;'>{key} Phase</span>",
                row=1,
                col=0)
            self.dict_plots[key]["Phase"].setLabel('left', 'Fase [°]', color='black')
            self.dict_plots[key]["Phase"].setLabel('bottom', 'Frecuencia [MHz]',color='black')
            self.dict_plots[key]["Phase"].showGrid(x=True, y=True, alpha=0.5)
            self.task_tab_s2p.addTab(self.dict_plots[key]["Layout"], key)

        self.plot_layout.setCurrentIndex(2)
        self.plot_layout.addWidget(self.task_tab_s2p)

        self.plot_layout.setCurrentIndex(0)

        self.mid_layout.addLayout(aux_Hlayout, 0,0,1,3)
        self.mid_layout.addWidget(self.file_list_widget, 1, 0, 9, 3)
        self.mid_layout.addWidget(self.clear_button, 10, 1, 1, 1)
        self.mid_layout.addLayout(self.plot_layout, 0, 4, 11, 14)

        # Main Layout
        main_layout.addLayout(top_layout)
        main_layout.addLayout(self.mid_layout)
        #main_layout.addStretch()

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.set_buttons_initial_status()

        self.showMaximized()

    def open_file_dialog(self):
        #Tengo el Path absoluto del archivo
        filename,_ = QFileDialog.getOpenFileName(self, caption='Select file', filter='S param files (*.csv *.s1p *.s2p)')

        if filename:

            #Si ya hay un archivo seleccionado lo removemos del watcher
            if self.path_sNp_file is not None:
                self.file_watcher.removePath(str(self.path_sNp_file))
            
            #Guardamos el path absoluto del archivo seleccionado
            self.path_sNp_file = Path(filename)
            name_string = self.path_sNp_file.name

            #Agregamos el nuevo archivo seleccionado al watcher
            self.file_watcher.addPath(str(self.path_sNp_file))
            self.file_watcher.fileChanged.connect(self.on_file_changed)

            #Cambiamos el layout de los graficos segun el tipo de archivo seleccionado
            if self.path_sNp_file.suffix == ".s1p":
                self.plot_layout.setCurrentIndex(1)
            elif self.path_sNp_file.suffix == ".s2p":
                self.plot_layout.setCurrentIndex(2)
                self.plot_s2p(str(self.path_sNp_file))

            #Nos fijamos si el archivo está en el directorio de datos, si lo está lo seleccionamos
            if self.path_sNp_file.parent == Path(DATA_PATH):
                print("El archivo seleccionado está en la carpeta de datos")
                for index in range(self.file_list_widget.count()):
                    item = self.file_list_widget.item(index)
                    if item.text() == name_string and item.isSelected() == False:
                        self.file_list_widget.setCurrentItem(item)

            print("Selected file:", self.path_sNp_file.name)
            self.file_name.setText(name_string)

    def show_connect_window(self):
        connect_window = ConnectWindow(self)
        connect_window.connection_established_signal.connect(self.refresh_buttons)
        connect_window.exec_()

    def show_debug_window(self):
        debug_window = DebugWindow(self)
        debug_window.exec_()

    def show_start_measure_window(self):
        measure_window = StartMeasureWindow(self)
        measure_window.exec_()

    def show_calibrate_window(self):
        calib_window = CalibrateWindow(self)
        calib_window.exec_()

    def show_settings_window(self):
        settings_window = SettingsWindow(self)
        settings_window.exec_()

    def set_buttons_initial_status(self):
        self.open_button.setEnabled(True)
        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
        self.debug_button.setEnabled(False)
        self.calibrate_button.setEnabled(False)
        self.start_measure.setEnabled(False)

    def refresh_buttons(self, is_connected: bool):
        self.open_button.setEnabled(True)
        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
        self.debug_button.setEnabled(False)
        self.calibrate_button.setEnabled(False)
        self.start_measure.setEnabled(False)

        if is_connected:
            self.open_button.setEnabled(True)
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
            self.debug_button.setEnabled(True)
            self.calibrate_button.setEnabled(True)
            self.start_measure.setEnabled(True)

    def disconnect_button_clicked(self):
        serial_client.disconnect()
        self.refresh_buttons(False)

    def on_directory_changed(self, path):
        self.load_files_from_directory(path)

    def load_files_from_directory(self, directory):
        # Limpiar el QListWidget antes de agregar nuevos archivos
        self.file_list_widget.clear()
        # Obtener la lista de archivos en el directorio
        try:
            files = listdir(directory)
            for file in files:
                # Agregar archivo a la lista solo si se corresponde con los formatos permitidos
                if file.endswith(".csv") or file.endswith(".s1p") or file.endswith(".s2p"):
                    self.file_list_widget.addItem(file)
        except FileNotFoundError:
            self.file_list_widget.addItem("Directory not found")

    def on_item_double_clicked(self, item):

        #Si ya hay un archivo seleccionado lo removemos del watcher
        if self.path_sNp_file is not None:
            self.file_watcher.removePath(str(self.path_sNp_file))

        self.path_sNp_file = path.join(DATA_PATH, item.text())
        self.path_sNp_file = Path( self.path_sNp_file)
        #Agregamos el nuevo archivo seleccionado al watcher
        self.file_watcher.addPath(str(self.path_sNp_file))
        self.file_watcher.fileChanged.connect(self.on_file_changed)
        #Pongo el nombre del archivo seleccionado en el QLineEdit
        self.file_name.setText(item.text())
        print("Selected file:", item.text())
        #Cambiamos el layout de los graficos segun el tipo de archivo seleccionado
        if self.path_sNp_file.suffix == ".s1p":
            self.plot_s1p(str(self.path_sNp_file))
            self.plot_layout.setCurrentIndex(1)
        elif self.path_sNp_file.suffix == ".s2p":
            self.plot_s2p(str(self.path_sNp_file))
            self.plot_layout.setCurrentIndex(2)
    
    def plot_s1p(self,archive):
        try:
            print("Archivo seleccionado:",archive)
            df = pd.read_csv(archive,comment="#",delimiter="\t",header=None)
            self.plot_s1p_s11_mag.plot(df[0], df[dict_s2p["S11"]], pen="k")
            self.plot_s1p_s11_pha.plot(df[0], df[dict_s2p["S11"]+1], pen="k")
            
        except Exception as e:  # Catch all exceptions
            print(e)
            print("No file available")
        
    def plot_s2p(self,archive):
        try:
            print("Archivo seleccionado:",archive)
            df = pd.read_csv(archive,comment="#",delimiter="\t",header=None)
    
            for key in self.dict_plots.keys():
                self.dict_plots[key]["Magnitude"].plot(df[0], df[dict_s2p[key]], pen="k")
                self.dict_plots[key]["Phase"].plot(df[0], df[dict_s2p[key]+1], pen="k")
            
        except Exception as e:  # Catch all exceptions
            print(e)
            print("No file available")
        
    def plot_button_clicked(self):
        if self.path_sNp_file is not None:
            if self.path_sNp_file.suffix == ".s1p":
                self.plot_s1p(str(self.path_sNp_file))
            elif self.path_sNp_file.suffix == ".s2p":
                self.plot_s2p(str(self.path_sNp_file))
        else:
            QMessageBox.warning(self, "Warning", "No file selected", QMessageBox.Ok)

    def on_file_changed(self, archive):
        if not os.path.exists(archive):
            self.clear_screen()


    def clear_screen(self):
        self.file_list_widget.clearSelection()
        self.file_name.setText("No file selected")
        self.plot_layout.setCurrentIndex(0)
        self.path_sNp_file = None
    

