import subprocess
import numpy as np
import time
import sys
from io import BytesIO

# --- КОНФІГУРАЦІЯ ---
FREQUENCY = 2400000000    # 2.4 GHz
SAMPLE_RATE = 8000000     # 8 Msps
TX_VGA_GAIN = 47          # 0-47 dB (IF Gain)
AMP_ENABLE = 1            # 0 = Off, 1 = On (+14 dB RF Amp)

def run_hackrf_stream():
    # 1. ГЕНЕРАЦІЯ IQ ДАНИХ У ПАМ'ЯТІ
    print("[INIT] Генерація масиву IQ у пам'яті...")
    
    # Генеруємо буфер на ~0.5 секунди роботи (4 млн семплів)
    # Це оптимальний розмір: не забиває RAM, але зменшує кількість викликів write()
    num_samples = 4_000_000
    
    # I = 127, Q = 0 (Максимальна потужність)
    iq_data = np.zeros(num_samples * 2, dtype=np.int8)
    iq_data[0::2] = 127 
    iq_data[1::2] = 0
    
    # Конвертуємо в байти один раз
    tx_bytes = iq_data.tobytes()
    print(f"[READY] Дані підготовлено ({len(tx_bytes)/1024/1024:.1f} MB у RAM).")

    # 2. ЗАПУСК HACKRF ЧЕРЕЗ PIPE
    cmd = [
        "hackrf_transfer",
        "-t", '-',             # <--- Читати з STDIN (без файлу)
        "-f", str(FREQUENCY),
        "-s", str(SAMPLE_RATE),
        "-a", str(AMP_ENABLE),
        "-x", str(TX_VGA_GAIN)
        # Прапорець -R (repeat) тут не потрібен, бо ми самі крутимо цикл
    ]
    
    print("-" * 40)
    print(f"[START] Запуск передачі...")
    print(f" -> Команда: {' '.join(cmd)}")
    
    process = None
    try:
        # Відкриваємо процес і отримуємо доступ до його 'stdin' (вводу)
        process = subprocess.Popen(
            cmd, 
            stdin=subprocess.PIPE,  # Відкриваємо трубу для запису
            stdout=subprocess.DEVNULL, # Ігноруємо сміття в консолі
            stderr=subprocess.PIPE  # Помилки хочемо бачити
        )
        
        print("[RUNNING] Трансляція з RAM. Ctrl+C для зупинки.")

        # 3. ЦИКЛ ПЕРЕДАЧІ
        while True:
            try:
                # Записуємо шматок байтів у HackRF
                # OS сама призупинить цей виклик, якщо буфер HackRF заповнений,
                # тому sleep() тут не потрібен — це працює максимально швидко.
                process.stdin.write(tx_bytes)
                process.stdin.flush()
                
                # Перевірка, чи не вмер процес
                if process.poll() is not None:
                    print("\n[ERROR] HackRF процес зупинився.")
                    stderr = process.stderr.read().decode()
                    print(f"Log: {stderr}")
                    break
                    
            except BrokenPipeError:
                print("\n[ERROR] Зв'язок з HackRF втрачено.")
                break

    except KeyboardInterrupt:
        print("\n[STOP] Зупинка користувачем...")
    finally:
        if process:
            process.terminate()
            process.wait(10000)
        print("[EXIT] Готово.")

if __name__ == "__main__":
    run_hackrf_stream()