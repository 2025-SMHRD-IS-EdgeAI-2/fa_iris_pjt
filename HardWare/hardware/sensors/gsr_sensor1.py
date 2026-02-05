import time
from smbus2 import SMBus
from collections import deque

ADS1115_ADDR = 0x48
REG_CONVERT = 0x00
REG_CONFIG  = 0x01

class GSRSensor:
    def __init__(self):
        self.bus = SMBus(1)
        self.baseline = None
        self.window = deque(maxlen=8)
        self.prev_smoothed = None

    def _ads_single_shot(self):
        config = 0xC583
        self.bus.write_i2c_block_data(
            ADS1115_ADDR,
            REG_CONFIG,
            [(config >> 8) & 0xFF, config & 0xFF]
        )

    def _read_adc(self):
        data = self.bus.read_i2c_block_data(ADS1115_ADDR, REG_CONVERT, 2)
        raw = (data[0] << 8) | data[1]
        if raw & 0x8000:
            raw -= 1 << 16
        voltage = raw * 2.048 / 32768.0
        return voltage

    def calibrate(self, duration=5):
        samples = []
        for _ in range(int(duration / 0.2)):
            self._ads_single_shot()
            time.sleep(0.03)
            v = self._read_adc()
            if 0.05 < v < 2.0:
                samples.append(v)
            time.sleep(0.2)

        self.baseline = sum(samples) / len(samples) if samples else 0.5
        self.prev_smoothed = self.baseline
        return self.baseline

    def read(self):
        self._ads_single_shot()
        time.sleep(0.03)
        v = self._read_adc()

        if not (0.15 < v < 1.9):
            return None

        self.window.append(v)
        smoothed = sum(self.window) / len(self.window)

        delta = smoothed - self.baseline
        slope = smoothed - self.prev_smoothed
        self.prev_smoothed = smoothed

        return {
            "gsr": smoothed,
            "delta": delta,
            "slope": slope
        }