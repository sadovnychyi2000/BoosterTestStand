import time
import sys
import numpy as np
from pyhackrf2 import HackRF

def run_hackrf_cw_generator():
    # Налаштування
    FREQUENCY = 2400e6    # 2.4 GHz
    TX_GAIN = 47          # Початкове підсилення (0-47)
    AMP_ENABLE =  True     # RF підсилювач (+14dB)
    SAMPLE_RATE = 10e6    # 10 Msps
    
    sdr = HackRF()

    try:
        print(f"[INFO] Ініціалізація HackRF на {FREQUENCY/1e9} GHz...")
        sdr.sample_rate = SAMPLE_RATE
        sdr.center_freq = FREQUENCY
        #sdr.txvga_gain = TX_GAIN
        #sdr.amplifier_on = AMP_ENABLE

        # --- ВИПРАВЛЕННЯ ПОМИЛКИ 'buffer' ---
        # Створюємо чистий сигнал (несуча / CW).
        # I = 127 (макс), Q = 0. Це створює постійний вектор.
        # Генеруємо великий шматок даних, щоб не поповнювати його занадто часто
        num_samples = 100_000 
        
        # Формуємо масив: I, Q, I, Q...
        # Використовуємо int8 (signed char), але Python bytes працює як unsigned char (0-255).
        # Для HackRF 127 (0x7F) це макс.
        iq_pairs = np.zeros(num_samples * 2, dtype=np.int8)
        iq_pairs[0::2] = 127  # I component
        iq_pairs[1::2] = 127    # Q component
        
        # Конвертуємо в bytes, бо саме це очікує sdr.buffer
        tx_chunk = iq_pairs.tobytes()

        # Ініціалізуємо буфер ПЕРЕД запуском (фікс AttributeError)
        sdr.buffer = bytearray(tx_chunk)

        print(f"[INFO] Початок передачі. Gain: {TX_GAIN}dB, Amp: {AMP_ENABLE}")
        sdr.start_tx()
        sdr.amplifier_on = AMP_ENABLE
        sdr.txvga_gain = TX_GAIN
        

        
        sdr.txvga_gain = TX_GAIN
        # Головний цикл: підтримуємо буфер заповненим
        # pyhackrf2 "з'їдає" дані з початку sdr.buffer. Ми повинні доливати в кінець.
        while True:
            # Якщо в буфері залишилось мало даних (менше ніж 1 шматок)
            if len(sdr.buffer) < len(tx_chunk):
                sdr.buffer += tx_chunk
            
            # Невелика пауза, щоб не вантажити процесор на 100%
            # Але не занадто велика, щоб буфер не спорожнів (при 10Msps це критично)
            time.sleep(0.001) 

            # Тут можна додати логіку зміни потужності, якщо потрібно
            # Наприклад, читання з файлу або зміна за часом
            
    except KeyboardInterrupt:
        print("\n[INFO] Зупинка передачі...")
    except Exception as e:
        print(f"\n[ERROR] Виникла помилка: {e}")
    finally:
        # Безпечне вимкнення
        try:
            sdr.stop_tx()
        except:
            pass
        sdr.close()
        print("[INFO] HackRF закрито.")

if __name__ == "__main__":
    run_hackrf_cw_generator()