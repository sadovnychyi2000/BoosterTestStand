import board
import busio
import time
import math
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

class PowerSensor:
    def __init__(self, channel=0):
        print("Ініціалізація I2C...")
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(self.i2c)
        
        # Вибір піна
        if channel == 0:
            pin = getattr(ADS, 'P0', 0) 
            self.chan = AnalogIn(self.ads, pin)
        elif channel == 1:
            pin = getattr(ADS, 'P1', 1)
            self.chan = AnalogIn(self.ads, pin)
            
        # Паспортні дані AD8318 (Типові)
        # Intercept 2.1V відповідає приблизно -65 dBm (рівень шуму/тиші)
        # Але математично у формулі це точка перетину осі Y
        self.intercept_v = 2.1  
        self.slope_v_db = -0.025 

    def get_voltage_avg(self, samples=50):
        """Повертає середнє з 50 вимірів для стабільності"""
        total = 0
        for _ in range(samples):
            total += self.chan.voltage
            time.sleep(0.001) 
        return total / samples

    def calculate_absolute_dbm(self, voltage):
        """
        Розрахунок абсолютної потужності в dBm.
        Формула AD8318: Vout = Slope * (Pin - Intercept)
        Звідси: Pin (dBm) = (Vout - V_intercept) / Slope
        """
        # Якщо напруга вища за Intercept (що неможливо для AD8318 при сигналі),
        # це означає розімкнутий вхід або глибокий шум.
        if voltage > self.intercept_v:
             return -65.0 # Обмежуємо "дном" чутливості
             
        dbm = (voltage - self.intercept_v) / self.slope_v_db
        return dbm

    def calculate_watts(self, dbm):
        """Переводить dBm у Вати"""
        # 1. Спочатку в мілівати: P(mW) = 10 ^ (dBm / 10)
        mw = 10 ** (dbm / 10)
        # 2. Переводимо у Вати
        return mw / 1000.0