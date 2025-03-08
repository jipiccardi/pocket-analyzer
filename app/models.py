class MeasuredValue:
    def __init__(self, cmd: str):
        self.freq = cmd[:5]
        self.mag_1 = cmd[5:9]
        self.ph1 = cmd[9:13]
        self.mag_2 = cmd[13:17]
        self.ph2 = cmd[17:21]

    def print_value(self):
        print(f"freq: {self.freq} mag_1: {self.mag_1} ph1: {self.ph1} mag_2: {self.mag_2} ph2: {self.ph2}")

