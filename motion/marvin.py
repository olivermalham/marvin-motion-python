import time
from PID import PID
from machine import PWM, Pin


class Wheel:
    pwm_pin: PWM
    dir_pin: Pin
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

    def __init__(self,
                 pwm_pin: PWM = None,
                 dir_pin: Pin = None,
                 pid: PID = None,
                 pwm: int = 0,
                 distance: int = 0,
                 target: int = 0,
                 v_prop: float = 0.0,
                 encoder_a: Pin = None,
                 encoder_b: Pin = None):
        self.pwm_pin = pwm_pin
        self.dir_pin = dir_pin
        self.pid = pid
        self.pwm = pwm
        self.distance = distance
        self.target = target
        self.v_prop = v_prop
        self.encoder_a = encoder_a
        self.encoder_b = encoder_b
        self.last_tick = time.ticks_ms()
        self.velocity = 0.0
        self.pwm_offset = 0

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
            if self.encoder_b.value():
                self.distance = self.distance + 1
            else:
                self.distance = self.distance - 1
            current_ticks = time.ticks_ms()

            # We've moved one encoder tick in distance, so this gets the velocity in ticks per second
            self.velocity = 1/time.ticks_diff(current_ticks, self.last_tick)
            self.last_tick = current_ticks

    def update_motor(self):
        self.dir_pin.high() if self.distance > self.target else self.dir_pin.low()
        self.pid.setpoint = self._target_velocity()
        self.pwm_pin.duty_u16(self._velocity_to_pwm(self.pid(self.velocity)))

    def stop(self):
        self.pwm_pin.duty_u16(0)

    def _target_velocity(self) -> float:
        """
        Calcualate the target velocity as per a trapezoidal profile, derived from the distance travelled (as that is the
        only value measured by the hardware. Assumes that all moves will be at constant acceleration up to maximum
        velocity. V_prop scales maximum velocity and acceleration to permit co-ordinated moves for all wheels together

        :return: target velocity
        """
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
        pwm = int(v * 1.0) + self.pwm_offset
        pwm = 1023 if pwm > 1023 else pwm
        pwm = 0 if pwm < 0 else pwm
        return pwm


def servo_loop(wheels: [Wheel]) -> None:
    """ Update the PWM setting for each motor using encoder feedback and PID control.
    """
    for wheel in wheels:
        # wheel.update_motor()
        pass


def config_wheels() -> [Wheel]:
    """ Configure the wheel data classes

    :return: List of Wheel objects with all appropriate pins initialised etc.
    """
    return [Wheel(pwm_pin=PWM(Pin(10)), pid=PID(scale="ms")),
            Wheel(pwm_pin=PWM(Pin(11)), pid=PID(scale="ms")),
            Wheel(pwm_pin=PWM(Pin(12)), pid=PID(scale="ms")),
            Wheel(pwm_pin=PWM(Pin(13)), pid=PID(scale="ms")),
            Wheel(pwm_pin=PWM(Pin(14)), pid=PID(scale="ms")),
            Wheel(pwm_pin=PWM(Pin(15)), pid=PID(scale="ms"))]
