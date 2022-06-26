# Example using PWM to fade an LED.

import time
from machine import Pin, PWM


# Construct PWM object, with LED on Pin(25).
pwm = PWM(Pin(25))

# Set the PWM frequency.
pwm.freq(16000)

# Fade the LED in and out a few times.
duty = 0
direction = 1


def update_led():
    global duty
    global direction

    duty += direction
    if duty > 255:
        duty = 255
        direction = -1
    elif duty < 0:
        duty = 0
        direction = 1
    pwm.duty_u16(duty * duty)

