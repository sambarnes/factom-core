import unittest
import datetime

from factom_core.block_elements import FactoidTransaction


class TestFactoidTransaction(unittest.TestCase):

    test_data = (
        "02016bb2d7cd7e0201008991b4e605c07d49124e6a6d968a25be00596939e7cb27af821a3119d60e55fd075ab1838e8d8b64"
        "330fd717584445ac866dc2facd8b856e63bdb8b15b5ed46c0b053b2c6c5c5c3f8991b4e605330fd717584445ac866dc2facd"
        "8b856e63bdb8b15b5ed46c0b053b2c6c5c5c3f0117646c5e142a35d2b7d6522cb738dfadb3e4057b7027926173de1e514c5f"
        "151c92cf5723e76b54a04d42bea61f81c8b7313aabecb5089efcf24d0b03b5f77d6473c4142ac021a041b5aed6ab7d224adf"
        "9ebe9f8767e4fd5bb3581b2ea62e1102012c94f2bbe49899679c54482eba49bf1d024476845e478f9cce3238f612edd761ef"
        "8c41822702b5caa37399d857b8601fc36fe66b451359f4f8764b9f6b1bdbcd439fe4f540d31aa7434eb080ccdc59056c14f8"
        "d70099a362e00f315cd2e41407"
    )

    def test_unmarshal(self):
        expected_tx_id = "bf5a4700b56c60e2cd2366094901436ee8e78db68768dbc96705bcf26a964d1a"
        expected_timestamp = 1562073615742
        expected_inputs = [
            {"value": 2452435717, "fct_address": "c07d49124e6a6d968a25be00596939e7cb27af821a3119d60e55fd075ab1838e",},
            {"value": 214500, "fct_address": "330fd717584445ac866dc2facd8b856e63bdb8b15b5ed46c0b053b2c6c5c5c3f",},
        ]
        expected_outputs = [
            {"value": 2452435717, "fct_address": "330fd717584445ac866dc2facd8b856e63bdb8b15b5ed46c0b053b2c6c5c5c3f",}
        ]
        expected_ec_purchases = []  # TODO: use a Factoid block with EC purchases too
        expected_rcds = [
            {
                "fct_public_key": "17646c5e142a35d2b7d6522cb738dfadb3e4057b7027926173de1e514c5f151c",
                "signature": "92cf5723e76b54a04d42bea61f81c8b7313aabecb5089efcf24d0b03b5f77d6473c4142ac021a041b5aed6ab7"
                "d224adf9ebe9f8767e4fd5bb3581b2ea62e1102",
            },
            {
                "fct_public_key": "2c94f2bbe49899679c54482eba49bf1d024476845e478f9cce3238f612edd761",
                "signature": "ef8c41822702b5caa37399d857b8601fc36fe66b451359f4f8764b9f6b1bdbcd439fe4f540d31aa7434eb080c"
                "cdc59056c14f8d70099a362e00f315cd2e41407",
            },
        ]

        tx = FactoidTransaction.unmarshal(bytes.fromhex(TestFactoidTransaction.test_data))
        assert tx.tx_id.hex() == expected_tx_id
        assert tx.timestamp == expected_timestamp
        for n, i in enumerate(tx.inputs):
            assert i.get("value") == expected_inputs[n].get("value")
            assert i.get("fct_address").hex() == expected_inputs[n].get("fct_address")
        for n, o in enumerate(tx.outputs):
            assert o.get("value") == expected_outputs[n].get("value")
            assert o.get("fct_address").hex() == expected_outputs[n].get("fct_address")
        for n, purchase in enumerate(tx.ec_purchases):
            assert purchase.get("value") == expected_ec_purchases[n].get("value")
            assert purchase.get("ec_public_key").hex() == expected_ec_purchases[n].get("ec_public_key")
        for n, rcd in enumerate(tx.rcds):
            assert rcd.public_key.hex() == expected_rcds[n].get("fct_public_key")
            assert rcd.signature.hex() == expected_rcds[n].get("signature")

    def test_marshal(self):
        tx_id = "bf5a4700b56c60e2cd2366094901436ee8e78db68768dbc96705bcf26a964d1a"
        tx = FactoidTransaction.unmarshal(bytes.fromhex(TestFactoidTransaction.test_data))
        assert tx.marshal().hex() == TestFactoidTransaction.test_data
