from PyQt5.QtCore import QThread, pyqtSignal
from .models import MeasuredValue
from globals import *

import time


# * Los Workers son rutinas que se van ejecutar en segundo plano comunmente en un thread


class CalibThread(QThread):
    finished_signal = pyqtSignal(str, list)

    def __init__(self, calib_mode: str, cmd: str):
        super(QThread, self).__init__()
        self.cmd = cmd
        self.calib_mode = calib_mode
        

    def run(self):
        serial_client.send_cmd(self.cmd)
        # send_frequency_low(settings.get_frequency_low())
        # send_frequency_high(settings.get_frequency_high())

        data = []
        eot = False
        v = b""
        print(v)
        while not eot:
            if self.isInterruptionRequested():
                return
            time.sleep(0.00005)
            if self.cmd == 'SM1000000' or self.cmd == 'SM2000000':
                v = serial_client.receive_value(18)
                print(v)
                if v.startswith(b'\x02') and v.endswith(b'\x03'):
                    print(v)
                    measured_value = MeasuredValue(v[4:17])
                    measured_value.convert_from_voltage()
                    data.append(measured_value)
            elif self.cmd == 'SM3000000':
                v = serial_client.receive_value(42)
                print(v)
                if v.startswith(b'\x02') and v.endswith(b'\x03'):
                    #print(v)
                    measured_value = MeasuredValue(v[4:41])
                    measured_value.convert_from_voltage()
                    data.append(measured_value)
            #if self.cmd == 'SM3000000':
            #    v = serial_client.receive_value(42)
            #    if v.startswith(b'\x02') and v.endswith(b'\x03'):
            #        data.append(MeasuredValue(v[4:17]))
            if 'END'.encode('UTF-8') in v:
                eot = True

        self.finished_signal.emit(self.calib_mode, data)