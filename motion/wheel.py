
def target_velocity(v_max: float, d_target: int, d: int, t: int) -> float:
    """

    :param v_max: target maximum velocity for this move
    :param d_target: target travel distance
    :param d: distance travelled so far
    :param t: milliseconds since the movement started
    :return: target velocity
    """
    t_ramp: float = 3000.0     # Time to ramp up to maximum velocity, in milliseconds
    max_a: float = 0.0         # Fixed acceleration rate, set manually
    max_d: int = d_target / 2 if d_target < 5000 else 5000  # Maximum distance travelled during acceleration phase

    # FIXME: I think these calcs are screwed up!
    # Set the target velocity
    if d < max_d:
        # Acceleration phase
        return max_a * t
    elif d < (d_target - (v_target * t_ramp * 0.5)):
        # Constant speed phase
        return 1.0
    elif d < d_target:
        # Deceleration phase
        return v_target - max_a
    else:
        return 0.0


def velocity_to_pwm(v) -> int:
    """ Includes clamping to valid PWM range"""
    pwm = int(v * 1.0)
    pwm = 1023 if pwm > 1023 else pwm
    pwm = 0 if pwm < 0 else pwm
    return pwm
