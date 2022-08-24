from PID import PID
# from dataclasses import dataclass
# from motion import target_velocity, velocity_to_pwm
from machine import PWM, Pin


class Wheel:
    pwm_pin: PWM
    pid: PID
    pwm: int = 0
    distance: int = 0
    target: int = 0
    v_prop: float = 0.0


# TODO: Need to pass in a list of wheels, not just one
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
    # return [Wheel(pwm_pin=PWM(Pin(10)), pid=PID(scale="ms")),
    #         Wheel(pwm_pin=PWM(Pin(11)), pid=PID(scale="ms"))]
    return []
