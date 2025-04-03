from view.connect_window import ConnectWindow
import serial.tools.list_ports
from globals import serial_client

class ConnectController():
    def __init__(self,main_window = None):
        self.view = ConnectWindow(main_window)

        self.view.port_list.currentItemChanged.connect(self.update_connect_button_state)
        self.view.connect_button.clicked.connect(self.connect_to_selected_port)
        self.view.fresh_button.clicked.connect(self.refresh_button)

        self.refresh_button()

    def refresh_button(self):
        self.view.port_list.clear()
        ports = serial.tools.list_ports.comports()

        for port in ports:
            self.view.port_list.addItem(port.device)

    def update_connect_button_state(self):
        self.view.connect_button.setEnabled(self.view.port_list.currentItem() is not None)

    def connect_to_selected_port(self):
        if self.view.port_list.currentItem():
            serial_client.connect(self.view.port_list.currentItem().text())
            self.view.connection_established_signal.emit(True)
            self.accept()