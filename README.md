# marvin-motion-python
Micropython rewrite of the marvin-motion motor control firmware

TODO:

1. Trapezoid target velocity function
2. Map velocity to PWM
3. Use PID to generate PWM value from measured and target velocity

Trapezoid - should this be keyed to time or distance? I think distance 
is better as that is a directly measured parameter. So how?


# Brain-check
Need to get straight in my head how this is supposed to work.
Only one measurement available - distance travelled.
Want to follow a trapezoidal movement profile, so constant acceleration, 
constant velocity, constant decelleration.

Use the measured distance to derive the target velocity
Use a PID to compare measured velocity against target velocity and 
produce a PWM value.

