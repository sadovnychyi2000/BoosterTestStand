import board
import busio
import time
import math
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

class PowerSensor:
    def __init__(self, channel=0):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(self.i2c)
        pin = getattr(ADS, 'P0', 0) if channel == 0 else getattr(ADS, 'P1', 1)
        self.chan = AnalogIn(self.ads, pin)
            
        # Дефолтні значення (будуть перезаписані автокалібруванням)
        self.slope = -0.025
        self.intercept = 20.0 

    def set_coefficients(self, new_slope, new_intercept):
        """Оновлює математичну модель сенсора"""
        self.slope = new_slope
        self.intercept = new_intercept

    def get_voltage_avg(self, samples=50):
        total = 0
        for _ in range(samples):
            total += self.chan.voltage
            time.sleep(0.001) 
        return total / samples

    def get_sensor_input_dbm(self, voltage):
        """Основна формула перерахунку"""
        if self.slope == 0: return 0.0
        return (voltage / self.slope) + self.intercept

    def calculate_watts(self, dbm):
        return (10 ** (dbm / 10)) / 1000.0