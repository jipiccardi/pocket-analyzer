import time

import serial
import logging

import serial.tools
import serial.tools.list_ports

#Definicion ascii de los caracteres de inicio y fin de texto
STX = "\u0002"
ETX = "\u0003"    


class SerialClient:
    def __init__(self):
        self.conn = None
        self.is_connected = False
        self.port = None
        self.baud_rate = None

    def connect(self, port: str, baud_rate: int = 9600, timeout: int = 1):
        logging.info("Connecting to port: " + port)
        if self.is_connected:
            logging.warning('Device already connected')
            return
        try:
            self.conn = serial.Serial(port, baud_rate, timeout=timeout)
            self.port = port
            self.baud_rate = baud_rate
            self.is_connected = True
            logging.debug('Connected successfully')
        except Exception as e:
            logging.error(f'Error trying to connect to {port}: {e}')

    def disconnect(self):
        if not self.is_connected:
            logging.warning('No active connection to disconnect from')
            return
        try:
            self.conn.flush()
            self.conn.close()
            self.is_connected = False
            self.conn = None
            logging.debug('Disconnect successfully')
        except Exception as e:
            logging.error(f'Error trying to disconnect: {e}')

    def send_cmd(self, cmd: str):
        try:
            logging.debug(f'{STX}{cmd}{ETX}'.encode())
            aux = len(f'{STX}{cmd}{ETX}')
            logging.debug(f'Longitud del string enviado = {aux}')
            self.conn.write(f'{STX}{cmd}{ETX}'.encode())
            self.conn.flush() # TODO validate
        except Exception as e:
            logging.error(f'Error trying to send {cmd}: {e}')
            self.conn.flush()

        # TODO handle response

    def receive_value(self):
        return self.conn.read(26)


def get_available_ports():
    ports = serial.tools.list_ports.comports()
    port_names = [port.device for port in ports]

    logging.debug(f'Available ports: {port_names}')
    return port_names
