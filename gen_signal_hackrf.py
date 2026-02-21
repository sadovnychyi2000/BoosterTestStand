import subprocess
import time

# Створюємо файл один раз
# hackrf_transfer -t /dev/zero -f 2400000000 -s 8000000 -a 1 -x 47
# /dev/zero дасть DC offset (несучу) по центру, але може бути слабким (0).
# Краще згенерувати файл як в минулій відповіді.

def run_cli_mode():
    print("Запуск через CLI (максимальна стабільність)...")
    # Переконайтеся, що файл cw_high_power.bin існує (код був у попередній відповіді)
    # Або використовуйте /dev/urandom для шуму
    
    cmd = [
        "hackrf_transfer",
        "-t", "cw_high_power.bin", # Файл з байтами 127
        "-f", "2400000000",        # 2.4 GHz
        "-s", "8000000",           # 8 Msps
        "-a", "1",                 # AMP ON
        "-x", "47",                # VGA 47dB
        "-R"                       # Repeat (по колу)
    ]
    
    try:
        proc = subprocess.Popen(cmd)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        proc.terminate()

if __name__ == "__main__":
    run_cli_mode()