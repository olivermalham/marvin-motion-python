from time import ticks_diff, ticks_ms

start_tick = ticks_ms()


def run_every(milliseconds: int, func, *args, **kwargs):
    global start_tick
    if ticks_diff(ticks_ms(), start_tick) % milliseconds == 0:
        return func(*args, **kwargs)
