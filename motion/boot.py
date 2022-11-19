from machine import Pin, PWM
from marvin import config_wheels, servo_loop
import sys
import uselect
import time
from commands import process_command, command_queue, status


print("Marvin Motion Controller")

loop = 0
start_tick = time.ticks_us()

led = Pin(25, Pin.OUT)
led.high()

wheels = config_wheels()
[wheel.stop() for wheel in wheels]

command_input = ""

while True:
    loop = loop + 1

    # run_every(200, update_led, led_pwm)
    ticks_us = time.ticks_us()

    if time.ticks_diff(ticks_us, start_tick) % 500 == 0:
        servo_loop(wheels)
        status(wheels, True)
        print(command_queue)

    # Command processing
    if uselect.select([sys.stdin], [], [], 0)[0]:
        c = sys.stdin.read(1)
        command_input = process_command(c, command_input, wheels)

    [wheel.update_encoder() for wheel in wheels]

    # If we've finished moving, remove that command from the buffer and move on to the next
    if not any([wheel.moving() for wheel in wheels]):
        if command_queue:
            new_command = command_queue[0]
            print(f"Executing command - {new_command}")
            for i in range(len(new_command)):
                wheels[i].target, wheels[i].v_prop = new_command[i]
            command_queue = command_queue[1:]
