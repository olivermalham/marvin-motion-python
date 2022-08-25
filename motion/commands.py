import marvin


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


def stop(wheels, args):
    print("STOP!!!")
    marvin.command_queue = [[(0, 0.0), (0, 0.0), (0, 0.0), (0, 0.0), (0, 0.0), (0, 0.0)]]


def echo(_, arg_list):
    print(f"ECHO: {arg_list}")


# Define a dictionary of functions that handle specific commands
command_list = {"echo": echo,
                "stop": stop}
