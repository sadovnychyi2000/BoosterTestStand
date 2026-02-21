import subprocess

FREQUENCY = 2400000000  
SAMPLE_RATE = 2000000   

def start_generator(tx_vga_gain, amp_enable):
    cmd = [
        'hackrf_transfer',
        '-t', '/dev/zero',        
        '-f', str(FREQUENCY),
        '-s', str(SAMPLE_RATE),
        '-a', str(amp_enable),
        '-x', str(tx_vga_gain)
    ]
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)