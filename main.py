import time
import sys
from config_hackrf import start_generator
from sensor_ads1115 import PowerSensor
from calibration import auto_calibrate  # Імпортуємо нашу нову функцію

# КОНФІГУРАЦІЯ СТЕНДУ
# Атенюатор, який фізично стоїть перед сенсором
ATTENUATOR_VAL = 0.0  
CABLE_LOSS = 0.5 

def main():
    # 1. Ініціалізація
    try:
        sensor = PowerSensor()
    except Exception as e:
        print(f"Помилка: {e}")
        return

    # 2. АВТОМАТИЧНЕ КАЛІБРУВАННЯ
    # Система сама увімкне HackRF, поміряє рівні і налаштує формулу.
    auto_calibrate(sensor)

    # 3. ОСНОВНИЙ ТЕСТ
    print("Готовність до тестування підсилювача.")
    print("Підключіть [DUT -> Attenuator] у розрив, якщо потрібно.")
    input("Натисніть Enter для старту моніторингу...")

    # Запуск HackRF для тесту (Робочий режим)
    # Наприклад, VGA 35 для входу підсилювача
    hackrf_process = start_generator(tx_vga_gain=35, amp_enable=1)
    time.sleep(2)

    print(f"\n{'V_sensor':<10} | {'Sensor Input':<15} | {'DUT OUTPUT (dBm)':<18} | {'DUT OUTPUT (W)':<15}")
    print("=" * 70)

    try:
        while True:
            # Отримуємо дані
            v_avg = sensor.get_voltage_avg()
            pin_sensor = sensor.get_sensor_input_dbm(v_avg)
            
            # Додаємо зовнішні фактори (Атенюатор + Кабель)
            dut_output_dbm = pin_sensor + ATTENUATOR_VAL + CABLE_LOSS
            watts = sensor.calculate_watts(dut_output_dbm)
            
            if watts < 1.0:
                p_str = f"{watts*1000:.1f} mW"
            else:
                p_str = f"{watts:.4f} W"

            sys.stdout.write(f"\r{v_avg:.4f} V   | {pin_sensor:.2f} dBm      | {dut_output_dbm:.2f} dBm         | {p_str:<10}")
            sys.stdout.flush()
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\nСтоп.")
    finally:
        if hackrf_process: hackrf_process.terminate()

if __name__ == "__main__":
    main()