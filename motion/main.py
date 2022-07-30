from machine import Pin, PWM
from pwm_led import update_led
from tools import run_every
from motion import target_velocity, velocity_to_pwm

print("Marvin Motion")

loop = 0
distance = 1  # Distance travelled in the current move
target_distance = 2000
v_prop = 1.0

# Construct PWM object, with LED on Pin(25).
led_pwm = PWM(Pin(25))
# Set the PWM frequency.
led_pwm.freq(16000)

while True:
    run_every(1000, lambda: print(f"Marvin Motion {loop}"))
#    run_every(200, update_led, led_pwm)
    loop = loop + 1
    if loop > 2000000:
        break

    velocity = run_every(200, target_velocity, distance, target_distance, v_prop)

    if velocity is not None:
        pwm = velocity_to_pwm(velocity, 100)

    # On every loop, updated distance travelled by checking encoder inputs
    # TODO: Simulate movement by incrementing d in proportion to velocity
