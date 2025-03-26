import csv
import json
import logging
import os
from typing import List
import numpy as np
import pandas as pd
import io


class Settings:
    def __init__(self, filename='configs.json'):
        self.filename = filename
        self.settings = {}
        try:
            with open(filename, 'r') as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = {
                'f_init': '23.5',
                'f_end': '3000',
                'n_step': '100'
            }

        with open(filename, "w") as json_file:
            json.dump(self.settings, json_file, indent=4)

    def update_values(self, f_init, f_end, n_step):
        self.settings = {
                'f_init': f_init,
                'f_end': f_end,
                'n_step': n_step,
            }
        with open(self.filename, "w") as json_file:
            json.dump(self.settings, json_file, indent=4)

    def get_values(self):
        return self.settings

    def get_frequency_high(self):
        try:
            return self.settings['f_end']
        except Exception as e:
            logging.error(e)
            return ""

    def get_frequency_low(self):
        try:
            return self.settings['f_init']
        except Exception as e:
            logging.error(e)
            return ""

class MeasuredValue:
    def __init__(self, cmd: str):
        if isinstance(cmd, bytes):
            cmd = cmd.decode('utf-8')  # Decode bytes to string (if cmd is in bytes)

        self.freq = ""
        self.mag_1 = ""
        self.ph1 = ""
        self.mag_2 = ""
        self.ph2 = ""
        self.mag_3 = ""
        self.ph3 = ""
        self.mag_4 = ""
        self.ph4 = ""

        self.freq = cmd[:5]
        self.mag_1 = cmd[5:9]
        self.ph1 = cmd[9:13]

        if len(cmd) == 37:
            self.mag_2 = cmd[13:17]
            self.ph2 = cmd[17:21]
            self.mag_3 = cmd[21:25]
            self.ph3 = cmd[25:29]
            self.mag_4 = cmd[29:33]
            self.ph4 = cmd[33:37]

    def print_value(self):
        print(f"freq: {self.freq} mag_1: {self.mag_1} ph1: {self.ph1} mag_2: {self.mag_2} ph2: {self.ph2},"
              f" mag_3: {self.mag_3}, ph3: {self.ph3} mag_4: {self.mag_4}, ph4: {self.ph4}")

    def convert_from_voltage(self):
        try:
            self.mag_1 = ((1/30)*float(self.mag_1)) - 30
            self.mag_1 = np.power(10, self.mag_1 / 20)
            if self.mag_2 != "":
                self.mag_2 = ((1/30)*float(self.mag_2)) - 30
                self.mag_2 = np.power(10, self.mag_2 / 20)
            if self.mag_3 != "":
                self.mag_3 = ((1/30)*float(self.mag_3)) - 30
                self.mag_3 = np.power(10, self.mag_3 / 20)
            if self.mag_4 != "":
                self.mag_4 = ((1/30)*float(self.mag_4)) - 30
                self.mag_4 = np.power(10, self.mag_4 / 20)

            self.ph1 = (1/10)*float(self.ph1) - 180
            if self.ph2 != "":
                self.ph2 = (1/10)*float(self.ph2) - 180
            if self.ph3 != "":
                self.ph3 = (1/10)*float(self.ph3) - 180
            if self.ph4 != "":
                self.ph4 = (1/10)*float(self.ph4) - 180
        except Exception as e:
            print(e)

    #def values_from_voltage(self):
    #    self.mag_1 = ((-1/30)*float(self.mag_1)) + 30
    #    #self.mag_2 = ((-1/30) * float(self.mag_2)) + 30
    #    self.ph1 = (-1/10) * float(self.ph1) + 180
    #    #self.ph2 = (-1 /10) * float(self.ph2) + 180


def save_measured_values_to_csv(name: str, values: List["MeasuredValue"]):
    """Save an array of MeasuredValue objects to a CSV file."""
    if not values:
        return

    with open(name, 'w', newline='') as f:
        writer = csv.writer(f)
        #if not file_exists:
        writer.writerow(["Frequency", "Magnitude 1", "Phase 1", "Magnitude 2", "Phase 2", "Magnitude 3",
                         "Phase 3", "Magnitude 4", "Phase 4"])

        for value in values:
            writer.writerow([value.freq, value.mag_1, value.ph1, value.mag_2, value.ph2, value.mag_3,
                             value.ph3, value.mag_4, value.ph4])
            
class DUT:
    def __init__(self):
        self.filename = None
        self.freq_units = ""
        self.s_units = ""
        self.port_mode = ""
        self.s_polar = None
        self.s_complex = None
        self.freq = []
        


    def read_file(self,filename):
        dict_s2p = {"S11":1,"S21":3,"S22":5,"S12":7 }
        dict_s1p = {"S11":1}

        self.filename = filename
        with open(self.filename, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line.startswith("#"):
                    config = line.strip()

        data_lines = [line for line in lines if not line.startswith(("!", "#"))]

        config = config.split(" ")
        self.freq_units = config[1]
        self.s_units = config[3]

        self.s_polar = pd.read_csv(io.StringIO(''.join(data_lines)), sep=None,engine='python', header=None)
        self.s_complex = pd.read_csv(io.StringIO(''.join(data_lines)), sep=None,engine='python', header=None)

        if self.s_polar.shape[1] > 4:
            self.port_mode = "2 Port"
            dict = dict_s2p
        else:
            self.port_mode = "1 Port"
            dict = dict_s1p

        if self.s_units == "DB":
            for i in dict.values():
                p = self.s_polar[i]
                theta = self.s_polar[i+1]
                self.s_complex[i] = np.power(10, p / 20) * np.cos(np.radians(theta))
                self.s_complex[i+1] = np.power(10, p / 20) * np.sin(np.radians(theta))

        elif self.s_units == "RI":
            for i in dict.values():
                x = self.s_complex[i]
                y = self.s_complex[i+1]
                self.s_polar[i] = 20*np.log10(np.abs(x + 1j*y))
                self.s_polar[i+1] = np.degrees(np.arctan2(x,y))

        
            
        
    
        



                


