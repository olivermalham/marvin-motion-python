
# Fade the LED in and out a few times.
duty = 0
direction = 1


def update_led(pwm_pin):
    global duty
    global direction

    duty += direction
    if duty > 255:
        duty = 255
        direction = -1
    elif duty < 0:
        duty = 0
        direction = 1
    pwm_pin.duty_u16(duty * duty)
