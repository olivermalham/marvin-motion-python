import time
from machine import Pin, PWM
from marvin import Wheel, config_wheels, servo_loop
from pwm_led import update_led
from tools import run_every
from motion import target_velocity, velocity_to_pwm
import sys
import uselect
import commands

print("Marvin Motion Controller")

# loop = 0
# distance = 1  # Distance travelled in the current move
# target_distance = 800000
# v_prop = 1.0

# Construct PWM object, with LED on Pin(25).
led_pwm = PWM(Pin(25, Pin.OUT))
# Set the PWM frequency.
led_pwm.freq(16000)

wheels = config_wheels()

command_input = ""

while True:
    run_every(10, update_led, led_pwm)
    # loop = loop + 1
    # if distance > target_distance:
    #     break
    #
    # run_every(1000, servo_loop, wheels)

    # On every loop, updated distance travelled by checking encoder inputs
    # TODO: Simulate movement by incrementing d in proportion to velocity

    # Command processing
    result = uselect.select([sys.stdin], [], [], 0)[0]

    if result:
        c = sys.stdin.read(1)
        if c != '\n':
            command_input = command_input + c
            print(f'{c}', end='')
        else:
            if command_input != "":
                print(f'\nCommand: {command_input}\n')
                command_parts = command_input.split()
                try:
                    func = getattr(commands, command_parts[0])
                    func(wheels, *command_parts[1:])
                except:
                    print(f"ERROR '{command_input}' failed!")
                finally:
                    command_input = ""
