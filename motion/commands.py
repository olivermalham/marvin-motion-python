
# List of lists. Each sublist is a distance, v_prop tuple, e.g.
# [
#   [(100,1.0),(100,1.0),(80,0.5),(80,0.5),(100,1.0),(100,1.0)],
#   [(100,1.0),(100,1.0),(80,0.5),(80,0.5),(100,1.0),(100,1.0)],
# ]
command_queue = []


def process_command(c, command_input, wheels):
    print(f'{c}', end='')
    if c != '\n':
        command_input = command_input + c
    else:
        if command_input != "":
            print(f'\nCommand: {command_input}\n')
            command_parts = command_input.split()
            try:
                func = command_list[command_parts[0]]
                func(wheels, command_parts[1:])
            except:
                print(f"ERROR '{command_input}' failed!")
            finally:
                command_input = ""
    return command_input


def move(_, args):
    """
        move wheel1_dist,wheel1_v_prop wheel2_dist,wheel2_v_prop ....

    Example command:
        move 1000,1.0 1000,1.0 800,0.8 800,0.8 950,0.95 950,0.95
        move 1000,1.0 1000,1.0 1000,1.0 1000,1.0 1000,1.0 1000,1.0

        move 4000,1.0 0,0.0 0,0.0 0,0.0 0,0.0 0,0.0
        move 0,0.0 4000,1.0 0,0.0 0,0.0 0,0.0 0,0.0
        move 0,0.0 0,0.0 4000,1.0 0,0.0 0,0.0 0,0.0
        move 0,0.0 0,0.0 0,0.0 40000,1.0 0,0.0 0,0.0
        move 0,0.0 0,0.0 0,0.0 0,0.0 4000,1.0 0,0.0
        move 0,0.0 0,0.0 0,0.0 0,0.0 0,0.0 4000,1.0

    """
    global command_queue
    new_command = []

    for pair in args:
        target, v_prop = pair.split(",")
        new_command.append((int(target), float(v_prop)))
    command_queue.append(new_command)


def stop(wheels, _):
    """ Emergency stop, commands all wheels to zero power and flushes the command queue """
    print("STOP!!!")
    global command_queue
    command_queue = [[(0, 0.0), (0, 0.0), (0, 0.0), (0, 0.0), (0, 0.0), (0, 0.0)]]
    [wheel.stop() for wheel in wheels]


def echo(_, arg_list):
    """ Echo input to output, mainly for testing connection """
    print(f"ECHO: {arg_list}")


def list_commands(_, arg_list):
    """ List help for all supported commands """
    print(f"Commands available:")
    [print(f"\t{command}") for command in command_list.keys()]


def status(wheels, _):
    """ List out all the distances and PWM settings for the motors """
    i = 0
    for wheel in wheels:
        print(f"{wheel.wheel_name} - D:{wheel.distance}\t\t Target:{wheel.target}\t V_target:{wheel.velocity}\t A:{wheel.pwm_pin_a.duty_u16()}\t B:{wheel.pwm_pin_b.duty_u16()}")
        i = i + 1
    print("\n")


# Define a dictionary of functions that handle specific commands
command_list = {"echo": echo,
                "stop": stop,
                "move": move,
                "help": list_commands,
                "status": status}
