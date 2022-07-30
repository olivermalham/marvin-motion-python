
def target_velocity(d: int, d_target: int, v_prop: float) -> float:
    """
    Use the time since the move started and the target distance to travel to calculate what the current velocity
    should be. Assumes that all moves will be at constant acceleration up to maximum velocity. V_prop scales
    maximum velocity and acceleration to permit co-ordinated moves for all wheels together
    :param d: current distance travelled
    :param d_target: target travel distance
    :param v_prop: fraction of maximum velocity to use
    :return: target velocity
    """

    t_ramp: float = 3000.0 * v_prop  # Time to ramp up to maximum velocity, in milliseconds
    max_a: float = 100.0 * v_prop      # Fixed acceleration rate, set manually
    v_max = max_a * t_ramp

    # Distance travelled during the ramp up / down phase
    d_ramp: float = 0.5 * max_a**2 * t_ramp

    # Handle the triangular motion case, where we don't reach the constant velocity phase.
    d_ramp = d_target / 2 if d_target < d_ramp * 2 else d_ramp

    # NOTE: velocity during ramp phases is proportional to distance travelled vs d_ramp
    if d < d_ramp:
        # Acceleration phase
        return v_max * (d / d_ramp)
    elif (d > d_ramp) and (d < d_target - d_ramp):
        # Constant speed phase
        return v_max
    elif (d_target - d_ramp) < d < d_target:
        # Deceleration phase
        return v_max - v_max * ((d_target - d_ramp) / d)  # FIXME! This needs more thought
    else:
        return 0.0


def velocity_to_pwm(v: float, offset: int = 0) -> int:
    """ Includes clamping to valid PWM range"""
    pwm = int(v * 1.0) + offset
    pwm = 1023 if pwm > 1023 else pwm
    pwm = 0 if pwm < 0 else pwm
    return pwm
