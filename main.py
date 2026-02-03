import time
import sys
from config_hackrf import start_generator
from sensor_ads1115 import PowerSensor

# ВАЖЛИВО: Якщо між HackRF і детектором стоїть атенюатор, впишіть його номінал
# Наприклад, якщо атенюатор 30dB, напишіть: ATTENUATOR_DB = 30
ATTENUATOR_DB = 0 

def main():
    try:
        sensor = PowerSensor()
    except Exception as e:
        print(f"Помилка сенсора: {e}")
        return

    hackrf_process = None

    try:
        # ЕТАП 1: Вимір рівня шуму (без HackRF)
        print("\n--- Калібрування шуму (HackRF вимкнено) ---")
        noise_volts = sensor.get_voltage_avg()
        noise_dbm = sensor.calculate_absolute_dbm(noise_volts)
        print(f"Рівень шуму: {noise_volts:.4f} V | {noise_dbm:.2f} dBm")
        print("-" * 50)
        
        # ЕТАП 2: Запуск HackRF
        print("Запуск генератора...")
        hackrf_process = start_generator()
        time.sleep(2) 

        print("\n--- МОНІТОРИНГ ПОТУЖНОСТІ ---")
        print(f"{'НАПРУГА (V)':<12} | {'dBm (SENSOR)':<15} | {'dBm (REAL)':<15} | {'ПОТУЖНІСТЬ (W)':<15}")
        print("-" * 65)

        while True:
            # 1. Отримуємо напругу
            v = sensor.get_voltage_avg()
            
            # 2. Рахуємо dBm на вході сенсора
            dbm_sensor = sensor.calculate_absolute_dbm(v)
            
            # 3. Додаємо поправку на атенюатор (якщо він є)
            dbm_real = dbm_sensor + ATTENUATOR_DB
            
            # 4. Рахуємо Вати (для реального dBm)
            watts = sensor.calculate_watts(dbm_real)
            
            # Форматуємо Вати (якщо менше 1W, показуємо mW)
            if watts < 1.0:
                power_str = f"{watts*1000:.2f} mW" 
            else:
                power_str = f"{watts:.4f} W"

            # Вивід в рядок
            print(f"{v:.4f} V     | {dbm_sensor:.2f} dBm       | {dbm_real:.2f} dBm       | {power_str}")
            
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\nЗупинка...")
    finally:
        if hackrf_process:
            hackrf_process.terminate()

if __name__ == "__main__":
    main()