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
constant velocity, constant deceleration.

Use the measured distance to derive the target velocity
Use a PID to compare measured velocity against target velocity and 
produce a PWM value.

## Update 4/12/2022
I finally have the motors working properly. Need to have the "unused" half of the bridge turned on, not off, while PWM 
driving the other half. Also, the PWM value needs to be subtracted from 65525 (16-bit integer maximum). This logic
seems to be the reverse of how the C code worked, so perhaps Micropython is doing something funky. Doesn't matter, works
now thank fuck.

Next steps:
1. Check that commands are queued and handled correctly DONE
2. Get the trapezoidal motion profile working without PID or relative velocity scaling (basically get back to the same level as the old C code)
3. Add velocity scaling
4. Add PID feedback loop

# WARNING!!!! Do NOT use print statements in the loop they slow down the loop polling and fuck up the encoder monitoring
