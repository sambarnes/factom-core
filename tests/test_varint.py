import unittest

from factom_core.utils import varint


class TestVarInt(unittest.TestCase):

    mapping = {
        0: bytes.fromhex("00"),
        3: bytes.fromhex("03"),
        127: bytes.fromhex("7F"),
        128: bytes.fromhex("8100"),
        130: bytes.fromhex("8102"),
        2 ** 16 - 1: bytes.fromhex("83FF7F"),
        2 ** 16: bytes.fromhex("848000"),
        2 ** 32 - 1: bytes.fromhex("8FFFFFFF7F"),
        2 ** 32: bytes.fromhex("9080808000"),
        2 ** 63 - 1: bytes.fromhex("FFFFFFFFFFFFFFFF7F"),
        2 ** 64 - 1: bytes.fromhex("81FFFFFFFFFFFFFFFF7F"),
    }

    def test_encode(self):
        for value_int, expected_varint in TestVarInt.mapping.items():
            observed_varint = varint.encode(value_int)
            assert observed_varint == expected_varint, "{}: 0x{} != 0x{}".format(
                value_int, observed_varint.hex(), expected_varint.hex()
            )

    def test_decode(self):
        for expected_int, value_varint in TestVarInt.mapping.items():
            observed_int, remainder = varint.decode(value_varint)
            assert observed_int == expected_int, "{} != {}".format(
                observed_int, expected_int
            )
            assert len(remainder) == 0
