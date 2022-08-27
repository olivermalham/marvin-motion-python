
# List of lists. Each sublist is a distance, v_prop tuple, e.g.
# [
#   [(100,1.0),(100,1.0),(80,0.5),(80,0.5),(100,1.0),(100,1.0)],
#   [(100,1.0),(100,1.0),(80,0.5),(80,0.5),(100,1.0),(100,1.0)],
# ]
command_queue = []


def process_command(c, command_input, wheels):
    if c != '\n':
        command_input = command_input + c
        print(f'{c}', end='')
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
        move 10000,1.0 10000,1.0 8000,0.8 8000.8 9500,0.95 9500,0.95

    """
    global command_queue
    new_command = []
    pairs = args.split()
    for pair in pairs:
        target, v_prop = pair.split(",")
        new_command.append((int(target), float(v_prop)))
    command_queue.append(new_command)


def stop(wheels, _):
    print("STOP!!!")
    global command_queue
    command_queue = [[(0, 0.0), (0, 0.0), (0, 0.0), (0, 0.0), (0, 0.0), (0, 0.0)]]
    [wheel.stop() for wheel in wheels]


def echo(_, arg_list):
    print(f"ECHO: {arg_list}")


# Define a dictionary of functions that handle specific commands
command_list = {"echo": echo,
                "stop": stop,
                "move": move}
