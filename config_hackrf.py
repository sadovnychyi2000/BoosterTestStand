import subprocess

# Параметри сигналу
FREQUENCY = 2400000000  # 2.4 GHz
SAMPLE_RATE = 2000000   # 2 MHz
TX_VGA_GAIN = 30        # Посилення (0-47)
AMP_ENABLE = 1          # 1 - увімкнути підсилювач, 0 - вимкнути

def start_generator():
    """Запускає hackrf_transfer як фоновий процес"""
    print(f"Ініціалізація HackRF на частоті {FREQUENCY/1e9} GHz...")
    
    cmd = [
        'hackrf_transfer',
        '-t', '/dev/zero',        
        '-f', str(FREQUENCY),
        '-s', str(SAMPLE_RATE),
        '-a', str(AMP_ENABLE),
        '-x', str(TX_VGA_GAIN)
    ]
    
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)