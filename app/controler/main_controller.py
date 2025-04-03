from view import main_window,connect_window,debug_window,calibrate_window,settings_window,dialogs
from models.models import DUT
from start_measure import StartMeasureWindow
from .settings_controller import SettingsController
from .connect_controller import ConnectController
from .calibrate_controller import CalibrateController
from .debug_controller import DebugController
from globals import *
from pathlib import Path
import os
from skrf import Network,plotting

class MainController():
    def __init__(self):
        self.view = main_window.MainWindow()
        self.path_sNp_file = None

        self.load_files_from_directory(DATA_PATH)
        self.set_buttons_initial_status()

        self.view.open_button.clicked.connect(self.open_file_dialog)
        self.view.connect_button.clicked.connect(self.show_connect_window)
        self.view.disconnect_button.clicked.connect(self.disconnect_button_clicked)
        self.view.settings_button.clicked.connect(self.show_settings_window)
        self.view.debug_button.clicked.connect(self.show_debug_window)
        self.view.calibrate_button.clicked.connect(self.show_calibrate_window)
        self.view.start_measure.clicked.connect(self.show_start_measure_window)
        self.view.clear_button.clicked.connect(self.clear_screen)
        self.view.plot_button.clicked.connect(self.plot_button_clicked)
        self.view.plot_type.currentIndexChanged.connect(self.on_type_changed)
        self.view.file_list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.view.directory_watcher.directoryChanged.connect(self.on_directory_changed)

    def open_file_dialog(self):
        #Tengo el Path absoluto del archivo
        filename,_ = dialogs.FileDialogManager.get_open_filename(self.view, caption='Select file', filter='S param files (*.csv *.s1p *.s2p)')

        if filename:

            #Si ya hay un archivo seleccionado lo removemos del watcher
            if self.path_sNp_file is not None:
                self.view.file_watcher.removePath(str(self.path_sNp_file))
            
            #Guardamos el path absoluto del archivo seleccionado
            self.path_sNp_file = Path(filename)
            name_string = self.path_sNp_file.name

            #Agregamos el nuevo archivo seleccionado al watcher
            self.view.file_watcher.addPath(str(self.path_sNp_file))
            self.view.file_watcher.fileChanged.connect(self.on_file_changed)

            #Cambiamos el layout de los graficos segun el tipo de archivo seleccionado
            self.plot_smith(str(self.path_sNp_file))

            if self.path_sNp_file.suffix == ".s1p":
                self.view.plot_layout.setCurrentIndex(1)
                self.plot_s1p(str(self.path_sNp_file))
                
            elif self.path_sNp_file.suffix == ".s2p":
                self.view.plot_layout.setCurrentIndex(2)
                self.plot_s2p(str(self.path_sNp_file))

            #Nos fijamos si el archivo está en el directorio de datos, si lo está lo seleccionamos
            if self.path_sNp_file.parent == Path(DATA_PATH):
                print("El archivo seleccionado está en la carpeta de datos")
                for index in range(self.view.file_list_widget.count()):
                    item = self.view.file_list_widget.item(index)
                    if item.text() == name_string and item.isSelected() == False:
                        self.view.file_list_widget.setCurrentItem(item)

            print("Selected file:", self.path_sNp_file.name)
            self.view.task_tab_s1p.setCurrentIndex(0)
            self.view.task_tab_s2p.setCurrentIndex(0)
            self.view.file_name.setText(name_string)

    def show_connect_window(self):
        conn_window = ConnectController(main_window=self.view)
        conn_window.view.connection_established_signal.connect(self.refresh_buttons)
        conn_window.view.exec_()

    def show_debug_window(self):
        deb_window = debug_window.DebugWindow(self.view)
        deb_window.exec_()

    def show_start_measure_window(self):
        meas_window = StartMeasureWindow(self.view)
        meas_window.exec_()

    def show_calibrate_window(self):
        calib_window = DebugController(main_window=self.view)
        calib_window.view.exec_()

    def disconnect_button_clicked(self):
        serial_client.disconnect()
        self.refresh_buttons(False)

    def show_settings_window(self):
        set_window = SettingsController(main_window=self.view)
        set_window.view.exec_()

    def set_buttons_initial_status(self):
        self.view.open_button.setEnabled(True)
        self.view.connect_button.setEnabled(True)
        self.view.disconnect_button.setEnabled(False)
        self.view.debug_button.setEnabled(False)
        self.view.calibrate_button.setEnabled(False)
        self.view.start_measure.setEnabled(False)

    def refresh_buttons(self, is_connected: bool):
        self.view.open_button.setEnabled(True)
        self.view.connect_button.setEnabled(True)
        self.view.disconnect_button.setEnabled(False)
        self.view.debug_button.setEnabled(False)
        self.view.calibrate_button.setEnabled(False)
        self.view.start_measure.setEnabled(False)

        if is_connected:
            self.view.open_button.setEnabled(True)
            self.view.connect_button.setEnabled(False)
            self.view.disconnect_button.setEnabled(True)
            self.view.debug_button.setEnabled(True)
            self.view.calibrate_button.setEnabled(True)
            self.view.start_measure.setEnabled(True)

    def on_directory_changed(self, path):
        self.load_files_from_directory(path)

    def load_files_from_directory(self, directory):
        # Limpiar el QListWidget antes de agregar nuevos archivos
        self.view.file_list_widget.clear()
        # Obtener la lista de archivos en el directorio
        try:
            files = os.listdir(directory)
            for file in files:
                # Agregar archivo a la lista solo si se corresponde con los formatos permitidos
                if file.endswith(".csv") or file.endswith(".s1p") or file.endswith(".s2p"):
                    self.view.file_list_widget.addItem(file)
        except FileNotFoundError:
            self.view.file_list_widget.addItem("Directory not found")

    def on_file_changed(self, archive):
        if not os.path.exists(archive):
            self.clear_screen()

    def clear_screen(self):
        self.view.task_tab_s1p.setCurrentIndex(0)
        self.view.task_tab_s2p.setCurrentIndex(0)
        self.view.file_list_widget.clearSelection()
        self.view.file_name.setText("No file selected")
        self.view.plot_layout.setCurrentIndex(0)
        self.path_sNp_file = None
    
    def on_item_double_clicked(self, item):

        #Si ya hay un archivo seleccionado lo removemos del watcher
        if self.path_sNp_file is not None:
            self.view.file_watcher.removePath(str(self.path_sNp_file))

        self.path_sNp_file = os.path.join(DATA_PATH, item.text())
        self.path_sNp_file = Path( self.path_sNp_file)
        #Agregamos el nuevo archivo seleccionado al watcher
        self.view.file_watcher.addPath(str(self.path_sNp_file))
        self.view.file_watcher.fileChanged.connect(self.on_file_changed)
        
        
        #Cambiamos el layout de los graficos segun el tipo de archivo seleccionado
        self.plot_smith(str(self.path_sNp_file))

        if self.path_sNp_file.suffix == ".s1p":
            self.plot_s1p(str(self.path_sNp_file))
            self.view.plot_layout.setCurrentIndex(1)
        elif self.path_sNp_file.suffix == ".s2p":
            self.plot_s2p(str(self.path_sNp_file))
            self.view.plot_layout.setCurrentIndex(2)
        self.view.task_tab_s1p.setCurrentIndex(0)
        self.view.task_tab_s2p.setCurrentIndex(0)
        #Pongo el nombre del archivo seleccionado en el QLineEdit
        self.view.file_name.setText(item.text())
        print("Selected file:", item.text())

    def on_type_changed(self):
        if not self.view.file_name.text() == "No file selected":
            if self.path_sNp_file.suffix == ".s1p":
                self.plot_s1p(str(self.path_sNp_file))
            elif self.path_sNp_file.suffix == ".s2p":
                self.plot_s2p(str(self.path_sNp_file))

    def plot_s1p(self,archive):
        try:
            dut = DUT()
            dut.read_file(archive)
            df = None

            self.view.plot_s1p_s11_mag.clear()
            self.view.plot_s1p_s11_pha.clear()

            self.view.plot_s1p_s11_pha.showGrid(x=True, y=True, alpha=0.5)
            self.view.plot_s1p_s11_mag.setLabel('bottom', f'Frequency [{dut.freq_units}]', color='black')
            self.view.plot_s1p_s11_mag.showGrid(x=True, y=True, alpha=0.5)
            self.view.plot_s1p_s11_pha.setLabel('bottom', f'Frequency [{dut.freq_units}]', color='black')

            if self.view.plot_type.currentText() == "Polar":
                df = dut.s_polar
                self.view.plot_s1p_s11_mag.setLabel('left', 'Magnitud [dB]', color='black')
                self.view.plot_s1p_s11_pha.setLabel('left', 'Fase [°]', color='black')
                self.view.plot_s1p_s11_mag.setTitle(f"<span style='color: blue; font-size: 12pt;'>S11 Magnitude</span>")
                self.view.plot_s1p_s11_pha.setTitle(f"<span style='color: blue; font-size: 12pt;'>S11 Phase</span>")

            elif self.view.plot_type.currentText() == "Complex":
                df = dut.s_complex
                self.view.plot_s1p_s11_mag.setLabel('left', 'Real [Re]', color='black')
                self.view.plot_s1p_s11_pha.setLabel('left', 'Imaginario [Im]', color='black')
                self.view.plot_s1p_s11_mag.setTitle(f"<span style='color: blue; font-size: 12pt;'>S11 Real</span>")
                self.view.plot_s1p_s11_pha.setTitle(f"<span style='color: blue; font-size: 12pt;'>S11 Imaginary</span>")
            
            self.view.plot_s1p_s11_mag.plot(df[0], df[dict_s2p["S11"]], pen="k")
            self.view.plot_s1p_s11_pha.plot(df[0], df[dict_s2p["S11"]+1], pen="k")
            
        except Exception as e:  # Catch all exceptions
            print(e)
            print("No file available for ploting")
        
    def plot_s2p(self,archive):
        try:
            dut = DUT()
            dut.read_file(archive)
            df = None

            pen = pen_plots

            for key in self.view.dict_plots.keys():

                self.view.dict_plots[key]["Plot 2"].clear()
                self.view.dict_plots[key]["Plot 1"].clear()

                self.view.dict_plots[key]["Plot 1"].setLabel('bottom', f'Frequency [{dut.freq_units}]', color='black')
                self.view.dict_plots[key]["Plot 1"].showGrid(x=True, y=True, alpha=0.5)
                self.view.dict_plots[key]["Plot 2"].setLabel('bottom', f'Frequency [{dut.freq_units}]', color='black')
                self.view.dict_plots[key]["Plot 2"].showGrid(x=True, y=True, alpha=0.5)

                if self.view.plot_type.currentText() == "Polar":
                    df = dut.s_polar
                    self.view.dict_plots[key]["Plot 1"].setLabel('left', 'Magnitud [dB]', color='black')
                    self.view.dict_plots[key]["Plot 2"].setLabel('left', 'Fase [°]', color='black')
                    self.view.dict_plots[key]["Plot 1"].setTitle(f"<span style='color: blue; font-size: 12pt;'>{key} Magnitude</span>")
                    self.view.dict_plots[key]["Plot 2"].setTitle(f"<span style='color: blue; font-size: 12pt;'>{key} Phase</span>")
                elif self.view.plot_type.currentText() == "Complex":
                    df = dut.s_complex
                    self.view.dict_plots[key]["Plot 1"].setLabel('left', 'Real [Re]', color='black')
                    self.view.dict_plots[key]["Plot 2"].setLabel('left', 'Imaginario [Im]', color='black')
                    self.view.dict_plots[key]["Plot 1"].setTitle(f"<span style='color: blue; font-size: 12pt;'>{key} Real</span>")
                    self.view.dict_plots[key]["Plot 2"].setTitle(f"<span style='color: blue; font-size: 12pt;'>{key} Imaginary</span>")

                self.view.dict_plots[key]["Plot 1"].plot(df[0], df[dict_s2p[key]], pen=pen)
                self.view.dict_plots[key]["Plot 2"].plot(df[0], df[dict_s2p[key]+1], pen=pen)    
            
        except Exception as e:  # Catch all exceptions
            print(e)
            print("No file available")
        
    def plot_smith(self,archive):
        dut = Network(archive)
        ax = None
        lines = []
        canva = None

        if dut.nports == 1:
            canva = self.view.plot_smith_s1p
            ax = self.view.plot_smith_s1p.axes
            lines = [{'marker_idx': [1, -1], 'color': 'g', 'm': 0, 'n': 0, 'ntw': dut}]
        elif dut.nports == 2:
            canva = self.view.plot_smith_s2p
            ax = self.view.plot_smith_s2p.axes
            lines = [
                {'marker_idx': [1, -1], 'color': 'g', 'm': 0, 'n': 0, 'ntw': dut},
                {'marker_idx': [1, -1], 'color': 'r', 'm': 1, 'n': 0, 'ntw': dut},
                {'marker_idx': [1, -1], 'color': 'b', 'm': 1, 'n': 1, 'ntw': dut},
                {'marker_idx': [1, -1], 'color': 'm', 'm': 0, 'n': 1, 'ntw': dut},
            ]

        ax.cla() #Eliminamos el grafico anterior
        plotting.smith(ax = ax, draw_labels = True, ref_imm = 50.0, chart_type = 'z')
        # plot data
        row_labels = []
        row_colors = []
        cell_text = []
        for l in lines:
            m = l['m']
            n = l['n']
            l['ntw'].plot_s_smith(m=m, n=n, ax = ax, color=l['color'])
            #plot markers
            for i, k in enumerate(l['marker_idx']):
                x = l['ntw'].s.real[k, m, n]
                y = l['ntw'].s.imag[k, m, n]
                z = l['ntw'].z[k, m, n]
                z = f'{z.real:.4f} + {z.imag:.4f}j ohm'
                f = l['ntw'].frequency.f_scaled[k]
                f_unit = l['ntw'].frequency.unit
                row_labels.append(f'M{i + 1}')
                row_colors.append(l['color'])
                ax.scatter(x, y, marker = 'v', s=20, color=l['color'])
                ax.annotate(row_labels[-1], (x, y), xytext=(-7, 7), textcoords='offset points', color=l['color'])
                cell_text.append([f'{f:.3f} {f_unit}', z])
        leg1 = ax.legend(loc="upper right", fontsize= 6)

        canva.draw()

    def plot_button_clicked(self):
        if self.path_sNp_file is not None:
            if self.path_sNp_file.suffix == ".s1p":
                self.plot_s1p(str(self.path_sNp_file))
            elif self.path_sNp_file.suffix == ".s2p":
                self.plot_s2p(str(self.path_sNp_file))
        else:
            dialogs.MessageBoxManager.open_warning_box(caption="No file selected")
