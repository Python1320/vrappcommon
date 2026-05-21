import traceback


def queue_bad():
    raise ValueError("queue full")


def handler():
    raise ValueError("queue full in some handler function")


try:
    # queue_bad()
    handler()
except ValueError as e:
    tb = e.__traceback__
    ok = True
    for frame, _ in traceback.walk_tb(tb):
        if frame.f_code.co_name == handler.__name__:
            ok = False
            break
    if not ok:
        raise
