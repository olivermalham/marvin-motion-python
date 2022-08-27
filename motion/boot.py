from machine import Pin, PWM
from marvin import config_wheels, servo_loop
from pwm_led import update_led
from tools import run_every
import sys
import uselect
from commands import process_command, command_list

print("Marvin Motion Controller")

loop = 0

# Construct PWM object, with LED on Pin(25).
led_pwm = PWM(Pin(25, Pin.OUT))
# Set the PWM frequency.
led_pwm.freq(16000)

wheels = config_wheels()

command_input = ""

while True:
    loop = loop + 1

    run_every(10, update_led, led_pwm)
    run_every(50, servo_loop, wheels)

    # Command processing
    if uselect.select([sys.stdin], [], [], 0)[0]:
        c = sys.stdin.read(1)
        command_input = process_command(c, command_input, wheels)

    [wheel.update_encoder() for wheel in wheels]

    # If we've finished moving, remove that command from the buffer and move on to the next
    if not any([wheel.moving() for wheel in wheels]):
        command_list = command_list[1:]
        if command_list:
            new_command = command_list[0]
            for i in range(len(new_command)):
                wheels[i].target, wheels[i].v_prop = new_command[i]
