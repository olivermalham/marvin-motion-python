import machine

start_tick = machine.ticks_ms()

# Ugly, but required to ensure functions are only triggered once when the millisecond time matches,
# rather than multiple times during that millisecond
run_every_tracker = {}


def run_every(milliseconds: int, func, *args, **kwargs):
    global start_tick, run_every_tracker
    ticks_ms = machine.ticks_ms()
    if hash(func) not in run_every_tracker:
        run_every_tracker[hash(func)] = 0
    if machine.ticks_diff(ticks_ms, start_tick) % milliseconds == 0 and \
            run_every_tracker[hash(func)] != ticks_ms:
        run_every_tracker[hash(func)] = ticks_ms
        print(f"Run every {ticks_ms}")
        return func(*args, **kwargs)
    return None

