import time
from config_hackrf import start_generator

# === НАЛАШТУВАННЯ "ВІРТУАЛЬНОГО ЕТАЛОНУ" ===
# Ми кажемо програмі: "Вважай, що при цих налаштуваннях HackRF видає стільки dBm"
# Значення взяті приблизно для 2.4 ГГц. Ви можете підправити їх один раз.

CAL_LOW = {
    "vga": 0,
    "amp": 0,
    "ref_dbm": -35.0  # Опорна точка 1
}

CAL_HIGH = {
    "vga": 25,
    "amp": 0,
    "ref_dbm": -10.0  # Опорна точка 2
}

def auto_calibrate(sensor):
    print("\n>>> АВТОКАЛІБРУВАННЯ СЕНСОРА...")
    
    # 1. ЗАМІР ТОЧКИ LOW
    # print(f"   -> Генерую Low Signal (VGA {CAL_LOW['vga']})...")
    proc = start_generator(CAL_LOW['vga'], CAL_LOW['amp'])
    time.sleep(2) # Стабілізація
    v_low = sensor.get_voltage_avg(samples=50)
    proc.terminate()
    proc.wait()
    
    # 2. ЗАМІР ТОЧКИ HIGH
    # print(f"   -> Генерую High Signal (VGA {CAL_HIGH['vga']})...")
    proc = start_generator(CAL_HIGH['vga'], CAL_HIGH['amp'])
    time.sleep(2)
    v_high = sensor.get_voltage_avg(samples=50)
    proc.terminate()
    proc.wait()

    # 3. МАТЕМАТИКА (Розрахунок Slope та Intercept)
    # Формула: Slope = (Delta V) / (Delta P)
    delta_v = v_high - v_low
    delta_p = CAL_HIGH['ref_dbm'] - CAL_LOW['ref_dbm']
    
    if delta_p == 0:
        print("   [ERROR] Помилка калібрування: Delta P = 0")
        return

    new_slope = delta_v / delta_p
    
    # Формула: Intercept = P - (V / Slope)
    new_intercept = CAL_LOW['ref_dbm'] - (v_low / new_slope)

    # 4. ЗАСТОСУВАННЯ
    sensor.set_coefficients(new_slope, new_intercept)
    print(f"   [OK] Калібрування завершено.")
    print(f"   Slope: {new_slope:.5f} V/dB | Intercept: {new_intercept:.2f} dBm")
    print("-" * 50)