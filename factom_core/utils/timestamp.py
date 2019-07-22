import datetime


def get_milli_time():
    t = int(datetime.datetime.utcnow().timestamp() * 1000)
    return int.to_bytes(t, 6, "big", signed=False)
