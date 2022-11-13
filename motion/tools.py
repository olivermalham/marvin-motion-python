# import mock_machine
import time

start_tick = time.ticks_us()

# Ugly, but required to ensure functions are only triggered once when the millisecond time matches,
# rather than multiple times during that millisecond
run_every_tracker = {}


def run_every(milliseconds: int, func, *args, **kwargs):
    global start_tick, run_every_tracker
    ticks_us = time.ticks_us()
    if hash(func) not in run_every_tracker:
        run_every_tracker[hash(func)] = 0
    if time.ticks_diff(ticks_us, start_tick) % milliseconds == 0 and \
            run_every_tracker[hash(func)] != ticks_us:
        run_every_tracker[hash(func)] = ticks_us
        # print(f"Run every {ticks_ms}")
        return func(*args, **kwargs)
    return None
