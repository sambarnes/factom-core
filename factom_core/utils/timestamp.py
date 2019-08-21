import datetime


def get_milli_time(delta: int = 0):
    t = int((datetime.datetime.now().timestamp() + delta) * 1000)
    return int.to_bytes(t, 6, "big", signed=False)


def datetime_from_milli_time(timestamp: bytes):
    t = int.from_bytes(timestamp, "big", signed=False) / 1000
    return datetime.datetime.fromtimestamp(t)
