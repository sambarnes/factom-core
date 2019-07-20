import struct


def encode(number: int):
    """Pack `number` into varint bytes"""
    buf = bytearray()
    if number == 0:
        buf.append(0x00)

    h = number
    start = False
    if 0x8000000000000000 & h != 0:
        buf.append(0x81)
        start = True

    for i in range(9):
        b = h >> 56
        if b != 0 or start:
            start = True
            b = b | 0x80 if i != 8 else b & 0x7F
            b = b if b < 256 else struct.pack(">Q", b)[-1]
            buf.append(b)

        h = h << 7

    return bytes(buf)


def decode(raw: bytes):
    """Read a varint from `raw` bytes, return the remainder"""
    if raw is None or len(raw) == 0:
        return 0
    result = 0
    data = raw
    while True:
        i, data = ord(data[:1]), data[1:]
        result = result << 7
        result += i & 0x7F
        if i < 0x80:
            break

    return result, data
