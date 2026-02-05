# sensors/hr_sensor.py
import time
from DFRobot_BloodOxygen_S import *

class HRSensor:
    def __init__(self):
        self.sensor = DFRobot_BloodOxygen_S_i2c(1, 0x57)

    def setup(self):
        while not self.sensor.begin():
            time.sleep(1)
        self.sensor.sensor_start_collect()
        time.sleep(2)

    def read(self):
        self.sensor.get_heartbeat_SPO2()
        hr = self.sensor.heartbeat
        spo2 = self.sensor.SPO2

        if hr == -1 or spo2 == -1:
            return None

        return {
            "hr": hr,
            "spo2": spo2
        }