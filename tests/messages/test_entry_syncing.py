import unittest

import factom_core.block_elements
from factom_core.messages.entry_syncing import MissingDataRequest, MissingDataResponse


class TestMissingDataRequest(unittest.TestCase):

    test_data = "11deadbeef00000000000000000000000000000000000000000000000000000000000000000000"

    def test_unmarshal(self):
        msg = MissingDataRequest.unmarshal(bytes.fromhex(self.test_data))
        assert msg.timestamp.hex() == "deadbeef0000"
        assert msg.request_hash == bytes(32)

    def test_marshal(self):
        msg = MissingDataRequest(timestamp=bytes.fromhex("deadbeef0000"), request_hash=bytes(32))
        assert msg.marshal() == bytes.fromhex(self.test_data)


class TestMissingDataResponse(unittest.TestCase):
    test_data = (
        "1200006e4540d08d5ac6a1a394e982fb6a2ab8b516ee751c37420055141b94fe070bfe001b0019466163746f6d4574686572"
        "65756d416e63686f72436861696e546869732069732074686520466163746f6d20457468657265756d20616e63686f722063"
        "6861696e2c207768696368207265636f7264732074686520616e63686f727320466163746f6d2070757473206f6e20746865"
        "20457468657265756d206e6574776f726b2e0a"
    )

    def test_unmarshal(self):
        msg = MissingDataResponse.unmarshal(bytes.fromhex(self.test_data))
        assert isinstance(msg.requested_object, factom_core.block_elements.Entry)

    def test_marshal(self):
        msg = MissingDataResponse.unmarshal(bytes.fromhex(self.test_data))
        assert msg.marshal().hex() == self.test_data
