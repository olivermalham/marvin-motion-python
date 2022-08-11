import time
from PID import PID
from dataclasses import dataclass


class Pin:

    def __init__(self, pin_no: int):
        self.pin = pin_no


class PWM:

    def __init__(self, pin: Pin):
        self.pin = pin
        self.frequency: int = 0
        self.duty_cycle: int = 0

    def freq(self, freq: int):
        self.frequency = freq
        print(f"Pin {self.pin} Frequency set to {self.frequency}")

    def duty_u16(self, duty: int):
        self.duty_cycle = duty
        print(f"Pin {self.pin.pin} Duty cycle {self.duty_cycle}")


def ticks_ms() -> int:
    return int(time.clock_gettime_ns(time.CLOCK_MONOTONIC) / 1000000)


def ticks_diff(lower: int, upper: int) -> int:
    return upper - lower


@dataclass
class Wheel:
    pwm_pin: PWM
    pid: PID
    pwm: int = 0
    distance: int = 0
    target: int = 0
    v_prop: float = 0.0


def servo_loop(wheel: Wheel) -> Wheel:
    """ Generate the PWM value for a wheel, using the trapezoidal motion control along with PID

    :return:
    """
    pass


def config_wheels() -> [Wheel]:
    """ Configure the wheel data classes

    :return:
    """
    return [Wheel(pwm_pin=PWM(Pin(10)), pid=PID(scale="ms")),
            Wheel(pwm_pin=PWM(Pin(11)), pid=PID(scale="ms"))]
