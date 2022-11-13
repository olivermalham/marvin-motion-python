import time
from PID import PID
from machine import PWM, Pin


class Wheel:
    pwm_pin_a: PWM
    pwm_pin_b: PWM
    pid: PID
    pwm: int = 0
    distance: int = 0
    target: int = 0
    v_prop: float = 0.0
    encoder_a: Pin
    encoder_b: Pin
    encoder_a_last: int = 0
    last_tick = None
    velocity: float = 0.0
    pwm_offset: int = 0
    FORWARD: int = 1
    REVERSE: int = 0
    encoder_tolerance: int = 50

    def __init__(self,
                 pwm_pin_a: PWM = None,
                 pwm_pin_b: PWM = None,
                 pid: PID = None,
                 pwm: int = 0,
                 distance: int = 0,
                 target: int = 0,
                 v_prop: float = 0.0,
                 encoder_a: Pin = None,
                 encoder_b: Pin = None,
                 wheel_name: str = "Not Set"):
        self.pwm_pin_a = pwm_pin_a
        self.pwm_pin_a.freq(16000)
        self.pwm_pin_a.duty_u16(0)

        self.pwm_pin_b = pwm_pin_b
        self.pwm_pin_b.freq(16000)
        self.pwm_pin_b.duty_u16(0)

        self.pid = pid
        self.pwm = pwm
        self.distance = distance
        self.target = target
        self.v_prop = v_prop
        self.encoder_a = encoder_a
        self.encoder_b = encoder_b
        self.last_tick = time.ticks_us()
        self.velocity = 0.0
        self.pwm_offset = 0
        self.wheel_name = wheel_name

    def moving(self) -> bool:
        return self.pwm > 0

    def update_encoder(self):
        """ Check if the encoder A channel has changed, if so check the encoder B channel to figure out direction
        and update the distance travelled. Update the measured velocity at the same time, used to drive the PID to
        determine the target PWM value for the motor.

        :return:
        """
        if self.encoder_a.value() != self.encoder_a_last:
            self.encoder_a_last = self.encoder_a.value()
            if self.encoder_a.value() and self.encoder_b.value():
                # print(f"Wheel {self.wheel_name} encoder up tick")
                self.distance = self.distance + 1
            elif self.encoder_a.value() and not self.encoder_b.value():
                # print(f"Wheel {self.wheel_name} encoder down tick")
                self.distance = self.distance - 1
            current_ticks = time.ticks_us()

            # We've moved one encoder tick in distance, so this gets the velocity in ticks per millisecond
            self.velocity = 1/time.ticks_diff(current_ticks, self.last_tick)
            self.last_tick = current_ticks

    def update_motor(self):

        if abs(self.distance - self.target) < self.encoder_tolerance:
            self.stop()
            return

        # self.pid.setpoint = self._target_velocity()
        # self.pwm_pin.duty_u16(self._velocity_to_pwm(self.pid(self.velocity)))
        # self.pwm_pin.duty_u16(self._velocity_to_pwm(self.velocity))

        # self.pwm_pin_a.duty_u16(self._velocity_to_pwm(self._target_velocity()))
        # self.pwm_pin_a.duty_u16(60000)
        # self.pwm_pin_b.duty_u16(0)

        if self.distance > self.target:
            self.pwm_pin_a.duty_u16(65000)
            self.pwm_pin_b.duty_u16(0)
        else:
            self.pwm_pin_a.duty_u16(0)
            self.pwm_pin_b.duty_u16(65000)

    def stop(self):
        self.pwm_pin_a.duty_u16(0)
        self.pwm_pin_b.duty_u16(0)

    def _target_velocity(self) -> float:
        """
        Calculate the target velocity as per a trapezoidal profile, derived from the distance travelled (as that is the
        only value measured by the hardware). Assumes that all moves will be at constant acceleration up to maximum
        velocity. V_prop scales maximum velocity and acceleration to permit co-ordinated moves for all wheels together

        :return: target velocity
        """

        if self.v_prop == 0.0:
            return 0.0

        t_ramp: float = 3000.0 * self.v_prop  # Time to ramp up to maximum velocity, in milliseconds
        max_a: float = 100.0 * self.v_prop  # Fixed acceleration rate, set manually
        v_max = max_a * t_ramp

        # Distance travelled during the ramp up / down phase
        d_ramp: float = 0.5 * max_a ** 2 * t_ramp

        # Handle the triangular motion case, where we don't reach the constant velocity phase.
        d_ramp = self.target / 2 if self.target < d_ramp * 2 else d_ramp

        # NOTE: velocity during ramp phases is proportional to distance travelled vs d_ramp
        if self.distance < d_ramp:
            # Acceleration phase
            return v_max * (self.distance / d_ramp)
        elif (self.distance > d_ramp) and (self.distance < self.target - d_ramp):
            # Constant speed phase
            return v_max
        elif (self.target - d_ramp) < self.distance < self.target:
            # Deceleration phase
            return v_max * (1 - (self.distance - (self.target - d_ramp)) / d_ramp)
        else:
            return 0.0

    def _velocity_to_pwm(self, v: float) -> int:
        """ Includes clamping to valid PWM range"""
        pwm = int(v * 60000.0) + self.pwm_offset
        pwm = 60000 if pwm > 60000 else pwm
        pwm = 0 if pwm < 0 else pwm
        return pwm


def servo_loop(wheels: [Wheel]) -> None:
    """ Update the PWM setting for each motor using encoder feedback and PID control.
    """
    for wheel in wheels:
        wheel.update_motor()
        # pass


def config_wheels() -> [Wheel]:
    """ Configure the wheel data classes

    :return: List of Wheel objects with all appropriate pins initialised etc.
    """
    return [
            Wheel(wheel_name="1",
                  pwm_pin_a=PWM(Pin(6, Pin.OUT, value=0)),
                  pwm_pin_b=PWM(Pin(7, Pin.OUT, value=0)),
                  encoder_a=Pin(16, Pin.IN), encoder_b=Pin(17, Pin.IN), pid=PID(scale="ms")),
            Wheel(wheel_name="2",
                  pwm_pin_a=PWM(Pin(0, Pin.OUT, value=0)),
                  pwm_pin_b=PWM(Pin(1, Pin.OUT, value=0)),
                  encoder_a=Pin(22, Pin.IN), encoder_b=Pin(26, Pin.IN), pid=PID(scale="ms")),
            Wheel(wheel_name="3",
                  pwm_pin_a=PWM(Pin(8, Pin.OUT, value=0)),
                  pwm_pin_b=PWM(Pin(9, Pin.OUT, value=0)),
                  encoder_a=Pin(19, Pin.IN), encoder_b=Pin(18, Pin.IN), pid=PID(scale="ms")),
            Wheel(wheel_name="4",
                  pwm_pin_a=PWM(Pin(2, Pin.OUT, value=0)),
                  pwm_pin_b=PWM(Pin(3, Pin.OUT, value=0)),
                  encoder_a=Pin(14, Pin.IN), encoder_b=Pin(15, Pin.IN), pid=PID(scale="ms")),
            Wheel(wheel_name="5",
                  pwm_pin_a=PWM(Pin(10, Pin.OUT, value=0)),
                  pwm_pin_b=PWM(Pin(11, Pin.OUT, value=0)),
                  encoder_a=Pin(20, Pin.IN), encoder_b=Pin(21, Pin.IN), pid=PID(scale="ms")),
            Wheel(wheel_name="6",
                  pwm_pin_a=PWM(Pin(4, Pin.OUT, value=0)),
                  pwm_pin_b=PWM(Pin(5, Pin.OUT, value=0)),
                  encoder_a=Pin(13, Pin.IN), encoder_b=Pin(12, Pin.IN), pid=PID(scale="ms")),
            ]
