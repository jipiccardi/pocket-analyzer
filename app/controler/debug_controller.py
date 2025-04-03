from view.debug_window import DebugWindow,GPIOCheckBox
from globals import *
import logging


class DebugController():
    def __init__(self,main_window = None):
        self.view = DebugWindow(main_window)

        for i in range(1, 15):
            self.view.checkboxes[i].stateChanged.connect(self.gpio_status_changed)

        self.view.power_send_button.clicked.connect(lambda: self.send_power(self.view.power_input.text()))
        self.view.frequency_send_button.clicked.connect(lambda: self.send_frequency(self.view.frequency_input.text()))
    
    def gpio_status_changed(self, state):
        sender = self.view.sender()
        if isinstance(sender, GPIOCheckBox):
            print(f"GPIO {sender.gpio_id} state changed to {state}")
            if state > 0:   state = 1 #Por algun motivo el state pulsado vale 2 en vez de 1
            aux = str(f'{state}{sender.gpio_id}')
            aux = aux.rjust(6,'0')    #Relleno con ceros para llegar a los 6 caracteres
            aux = "GIO" + aux
            print("GPIO activado = ",aux)

            if serial_client.is_connected:
                serial_client.send_cmd(str(aux))
            else:
                logging.warning('Device is not connected')
    
    def send_frequency(value: float):
    
        aux = str(f'{value}')
        aux = aux.replace(".","") #Quito el punto del string
        aux = aux.rjust(6,'0')    #Relleno con ceros para llegar a los 6 caracteres
        print("data de 6 caracteres:",aux)
        aux = "FRQ" + aux
        print("Frecuencia enviada = ",aux)
        
        #serial_client.send_cmd('FRQ{value}')
        if serial_client.is_connected:
            serial_client.send_cmd(str(aux))
        else:
            logging.warning('Device is not connected')

    def send_frequency_low(value: float):
        aux = str(f'{value}')
        aux = aux.replace(".","") #Quito el punto del string
        aux = aux.rjust(6,'0')    #Relleno con ceros para llegar a los 6 caracteres
        print("data de 6 caracteres:",aux)
        aux = "FRL" + aux
        print("Frecuencia enviada = ",aux)
        
        if serial_client.is_connected:
            serial_client.send_cmd(str(aux))
        else:
            logging.warning('Device is not connected')

    def send_frequency_high(value: float):
        aux = str(f'{value}')
        aux = aux.replace(".","") #Quito el punto del string
        aux = aux.rjust(6,'0')    #Relleno con ceros para llegar a los 6 caracteres
        print("data de 6 caracteres:",aux)
        aux = "FRH" + aux
        print("Frecuencia enviada = ",aux)
        
        #serial_client.send_cmd('FRQ{value}')
        if serial_client.is_connected:
            serial_client.send_cmd(str(aux))
        else:
            logging.warning('Device is not connected')

    def send_frequency_step(value: int):
        aux = str(f'{value}')
        aux = aux.replace(".","") #Quito el punto del string
        aux = aux.rjust(6,'0')    #Relleno con ceros para llegar a los 6 caracteres
        print("data de 6 caracteres:",aux)
        aux = "FRS" + aux
        print("Frecuencia enviada = ",aux)
        
        #serial_client.send_cmd('FRQ{value}')
        if serial_client.is_connected:
            serial_client.send_cmd(str(aux))
        else:
            logging.warning('Device is not connected')

    def send_power(value: int):
        serial_client.send_cmd(f'PWR{1000000+value}')