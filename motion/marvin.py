import time
from PID import PID
from machine import PWM, Pin
import micropython

MAX_PWM = micropython.const(65535)
MAX_V = 250.0
V_CONVERT = MAX_PWM/MAX_V
SERVO_PERIOD = 10  # Milliseconds per servo loop run


class Wheel:
    pwm_pin_a: PWM
    pwm_pin_b: PWM
    pid: PID
    pwm: int = 0
    distance: int = 0
    last_distance: int = 0
    target: int = 0
    v_prop: float = 0.0
    encoder_a: Pin
    encoder_b: Pin
    encoder_a_last: int = 0
    last_tick = None
    velocity: float = 0.0
    velocity_target: float = 0.0
    pwm_offset: int = 20000
    FORWARD: int = 1
    REVERSE: int = 0
    encoder_tolerance: int = 10
    velocity_buffer: [float] = []

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
        self.pwm_pin_a.freq(1000)
        self.pwm_pin_a.duty_u16(0)

        self.pwm_pin_b = pwm_pin_b
        self.pwm_pin_b.freq(1000)
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
        self.velocity_target = 0.0
        self.pwm_offset = 20000
        self.wheel_name = wheel_name
        self.last_distance = 0

    # @micropython.viper
    def moving(self) -> bool:
        return (self.pwm_pin_a.duty_u16() < MAX_PWM) or (self.pwm_pin_b.duty_u16() < MAX_PWM)

    # @micropython.viper
    def update_encoder(self):
        """ Check if the encoder A channel has changed, if so check the encoder B channel to figure out direction
        and update the distance travelled. Update the measured velocity at the same time, used to drive the PID to
        determine the target PWM value for the motor.

        :return:
        """
        # Only update on a rising edge on encoder A channel
        if self.encoder_a.value() != self.encoder_a_last and self.encoder_a.value():
            if self.encoder_b.value():
                self.distance = self.distance + 1
            else:
                self.distance = self.distance - 1
        self.encoder_a_last = self.encoder_a.value()

    # @micropython.viper
    def update_motor(self):

        if abs(self.distance - self.target) < self.encoder_tolerance:
            self.stop()
            return

        # self.pid.setpoint = self._target_velocity()
        self.pid.setpoint = self.velocity_target
        # self.v_prop = self.velocity_target + self.pid(self.velocity)
        self.v_prop = self.pid(self.velocity)
        self.pwm = self._velocity_to_pwm(self.v_prop)
        # self.pwm = int(MAX_PWM/1)

        if self.distance < self.target:
            self.pwm_pin_a.duty_u16(self.pwm)
            self.pwm_pin_b.duty_u16(0)
        else:
            self.pwm_pin_a.duty_u16(0)
            self.pwm_pin_b.duty_u16(self.pwm)

    # @micropython.viper
    def update_velocity(self):
        # current_ticks = time.ticks_us()
        # velocity = 1000000.0/time.ticks_diff(current_ticks, self.last_tick)
        velocity = (self.distance - self.last_distance)/(SERVO_PERIOD/1000.0)  # Servo loop runs every 20ms
        self.last_distance = self.distance

        # Average the velocity over 10 samples (is this too coarse?)
        self.velocity_buffer.append(velocity)
        if len(self.velocity_buffer) > 10:
            self.velocity_buffer = self.velocity_buffer[:-10]
        self.velocity = sum(self.velocity_buffer) / len(self.velocity_buffer)

    # @micropython.viper
    def stop(self):
        self.pwm_pin_a.duty_u16(MAX_PWM)
        self.pwm_pin_b.duty_u16(MAX_PWM)
        self.target = 0
        self.distance = 0
        self.last_distance = 0

    # @micropython.viper
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

    # @micropython.viper
    def _velocity_to_pwm(self, v: float) -> int:
        """ Includes clamping to valid PWM range"""
        # pwm = int(v * MAX_PWM) + self.pwm_offset
        pwm = int(v * V_CONVERT) + self.pwm_offset
        pwm = MAX_PWM if pwm > MAX_PWM else pwm
        pwm = 0 if pwm < 0 else pwm
        return pwm


# @micropython.viper
def servo_loop(wheels: [Wheel]) -> None:
    """ Update the PWM setting for each motor using encoder feedback and PID control.
    """
    for wheel in wheels:
        wheel.update_velocity()
        wheel.update_motor()


# @micropython.viper
def config_wheels() -> [Wheel]:
    """ Configure the wheel data classes

    :return: List of Wheel objects with all appropriate pins initialised etc.
    """
    return [
            Wheel(wheel_name="1",
                  pwm_pin_a=PWM(Pin(6, Pin.OUT, value=0)),
                  pwm_pin_b=PWM(Pin(7, Pin.OUT, value=0)),
                  encoder_a=Pin(16, Pin.IN), encoder_b=Pin(17, Pin.IN), pid=PID(1, 0.1, 0.05, scale="ms", sample_time=50)),
            Wheel(wheel_name="2",
                  pwm_pin_a=PWM(Pin(0, Pin.OUT, value=0)),
                  pwm_pin_b=PWM(Pin(1, Pin.OUT, value=0)),
                  encoder_a=Pin(22, Pin.IN), encoder_b=Pin(26, Pin.IN), pid=PID(1, 0.1, 0.05, scale="ms", sample_time=50)),
            Wheel(wheel_name="3",
                  pwm_pin_a=PWM(Pin(8, Pin.OUT, value=0)),
                  pwm_pin_b=PWM(Pin(9, Pin.OUT, value=0)),
                  encoder_a=Pin(18, Pin.IN), encoder_b=Pin(19, Pin.IN), pid=PID(1, 0.1, 0.05, scale="ms", sample_time=50)),
            Wheel(wheel_name="4",
                  pwm_pin_a=PWM(Pin(2, Pin.OUT, value=0)),
                  pwm_pin_b=PWM(Pin(3, Pin.OUT, value=0)),
                  encoder_a=Pin(14, Pin.IN), encoder_b=Pin(15, Pin.IN), pid=PID(1, 0.1, 0.05, scale="ms", sample_time=50)),
            Wheel(wheel_name="5",
                  pwm_pin_a=PWM(Pin(10, Pin.OUT, value=0)),
                  pwm_pin_b=PWM(Pin(11, Pin.OUT, value=0)),
                  encoder_a=Pin(20, Pin.IN), encoder_b=Pin(21, Pin.IN), pid=PID(1, 0.1, 0.05, scale="ms", sample_time=50)),
            Wheel(wheel_name="6",
                  pwm_pin_a=PWM(Pin(4, Pin.OUT, value=0)),
                  pwm_pin_b=PWM(Pin(5, Pin.OUT, value=0)),
                  encoder_a=Pin(13, Pin.IN), encoder_b=Pin(12, Pin.IN), pid=PID(1, 0.1, 0.05, scale="ms", sample_time=50)),
            ]
