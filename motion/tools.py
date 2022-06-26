from time import ticks_diff, ticks_ms

start_tick = ticks_ms()
count = 0


def run_every(milliseconds: int, func) -> None:
    global start_tick, count
    if ticks_diff(ticks_ms(), start_tick) % milliseconds == 0:
        func()
        count = count + 1
