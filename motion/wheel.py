from PID import PID
from time import ticks_ms, ticks_diff
from machine import Pin, PWM


class Wheel:
    """
        Class that handles the motion control of a single wheel. Uses PID for error correction,
        implements a trapezoidal motion profile for larger moves, triangular for shorter.

        Note: Distance is measured in encoder ticks, velocity in encoder ticks per second, acceleration as ticks/s^2
        TODO: Figure out how many ticks per revolution, and how many ticks per meter!
    """
    def __init__(self, pin_a: Pin, pin_b: Pin):
        """
        :param pin_a: PWM enabled output pin to motor H-bridge
        :param pin_b: PWM enabled output pin to motor H-bridge
        """
        self.d: int = 0
        self.d_target: int = 0

        self.v: float = 0.0
        self.v_target: float = 0.0      # Is this required?

        self.t_ramp: float = 3000.0     # Time to ramp up to maximum velocity, in milliseconds
        self.max_a: float = 0.0         # Fixed acceleration rate, set manually
        self.max_d: int = 0             # Maximum distance travelled during acceleration phase

        self.v_pwm_coeff: float = 1.0   # Scale factor for converting velocity into a PWM value
        self.pwm_offset: int = 0        # Lowest PWM value that wheel starts turning at
        self.pwm: int = 0
        self.pwm_max: int = 1023        # Assuming 10-bit precision here TODO: Check this!
        self.ticks_last = None          # ticks_ms() result for the previous servo loop execution

        self.pin_a: Pin = pin_a         # PWM enabled output pin to motor H-bridge
        self.pin_b: Pin = pin_b         # PWM enabled output pin to motor H-bridge

        # TODO: Need to tune the PID parameters!
        self.pid = PID(Kp=1.0,
                       Ki=0.0,
                       Kd=0.0,
                       setpoint=0.0,
                       scale="ms",
                       error_map=self.v_to_pwm)

    def servo_tick(self, ticks: int) -> float:
        """
        Entry point into the servo control logic, run at a fixed interval
        :param ticks: Number of encoder ticks since the last call
        :return: Returns the error between target velocity and actual, to detect wheel spin / stall
        """
        if self.ticks_last is None:
            self.ticks_last = ticks_ms()
            return 0.0

        # TODO: Should we return immediately if v_target is zero?

        # Get current measurements
        t = ticks_diff(ticks_ms(), self.ticks_last)
        self.v = ticks / t
        self.d = self.d + ticks

        # Set the target velocity
        if self.d < self.max_d:
            # Acceleration phase
            self.v_target = self.v_target + self.max_a
        elif self.d < (self.d - (self.v * self.t_ramp * 0.5)):
            # Constant speed phase
            pass
        elif self.d < self.d_target:
            # Deceleration phase
            self.v_target = self.v_target - self.max_a
        else:
            # Stop and exit
            self.v_target = 0.0
            self.pwm = 0
            return 0.0

        self.pid.setpoint = self.v_target

        # Get the PWM value via the PID
        self.pwm = self.pid(self.v)

        # Update PWM on the pin here

        return self.d_target - self.d

    def v_to_pwm(self, v):
        return v * self.v_pwm_coeff
