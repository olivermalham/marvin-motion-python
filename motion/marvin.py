from PID import PID
from motion import target_velocity, velocity_to_pwm
from machine import PWM, Pin

# List of lists. Each sublist is a distance, v_prop tuple, e.g.
# [
#   [(100,1.0),(100,1.0),(80,0.5),(80,0.5),(100,1.0),(100,1.0)],
#   [(100,1.0),(100,1.0),(80,0.5),(80,0.5),(100,1.0),(100,1.0)],
# ]
command_queue = []


class Wheel:
    pwm_pin: PWM
    pid: PID
    pwm: int = 0
    distance: int = 0
    target: int = 0
    v_prop: float = 0.0

    def __init__(self, pwm_pin: PWM = None,
                 pid: PID = None,
                 pwm: int = 0,
                 distance: int = 0,
                 target: int = 0,
                 v_prop: float = 0.0):
        self.pwm_pin = pwm_pin
        self.pid = pid
        self.pwm = pwm
        self.distance = distance
        self.target = target
        self.v_prop = v_prop


def servo_loop(wheels: [Wheel]) -> [Wheel]:
    """ Generate the PWM value for a wheel, using the trapezoidal motion control along with PID

    :return:
    """
    # for wheel in wheels:
    #     wheel.pwm = velocity_to_pwm()
    pass


def config_wheels() -> [Wheel]:
    """ Configure the wheel data classes

    :return:
    """
    return [Wheel(pwm_pin=PWM(Pin(10)), pid=PID(scale="ms")),
            Wheel(pwm_pin=PWM(Pin(11)), pid=PID(scale="ms")),
            Wheel(pwm_pin=PWM(Pin(12)), pid=PID(scale="ms")),
            Wheel(pwm_pin=PWM(Pin(13)), pid=PID(scale="ms")),
            Wheel(pwm_pin=PWM(Pin(14)), pid=PID(scale="ms")),
            Wheel(pwm_pin=PWM(Pin(15)), pid=PID(scale="ms"))]
