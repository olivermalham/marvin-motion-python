from time import ticks_ms, ticks_diff
from pwm_led import update_led
from tools import run_every

print("Marvin Motion")

loop = 0

while True:
    run_every(1000, lambda: print(f"Marvin Motion {loop}"))
    run_every(20, update_led)
    loop = loop + 1

