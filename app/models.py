import csv
import json
import os
from typing import List



class Settings:
    def __init__(self, filename='configs.json'):
        self.filename = filename
        self.settings = {}
        try:
            with open(filename, 'r') as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = {
                'f_init': '',
                'f_end': '',
                'n_step': ''
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


class MeasuredValue:
    def __init__(self, cmd: str):
        if isinstance(cmd, bytes):
            cmd = cmd.decode('utf-8')  # Decode bytes to string (if cmd is in bytes)

        self.freq = cmd[:5]
        self.mag_1 = cmd[5:9]
        self.ph1 = cmd[9:13]
        self.mag_2 = cmd[13:17]
        self.ph2 = cmd[17:21]

    def print_value(self):
        print(f"freq: {self.freq} mag_1: {self.mag_1} ph1: {self.ph1} mag_2: {self.mag_2} ph2: {self.ph2}")


def save_measured_values_to_csv(name: str, values: List["MeasuredValue"]):
    """Save an array of MeasuredValue objects to a CSV file."""
    if not values:
        return  # Do nothing if list is empty

    file_exists = False
    try:
        with open(name, 'r', newline='') as f:
            file_exists = True
    except FileNotFoundError:
        pass

    with open(name, 'w', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Frequency", "Magnitude 1", "Phase 1", "Magnitude 2", "Phase 2"])
        for value in values:
            writer.writerow([value.freq, value.mag_1, value.ph1, value.mag_2, value.ph2])
