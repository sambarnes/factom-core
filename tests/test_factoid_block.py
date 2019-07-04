import unittest

from factom_core.blocks import FactoidBlock


class TestFactoidBlock(unittest.TestCase):

    test_data = "000000000000000000000000000000000000000000000000000000000000000fa501d7500373bae88158d5e7062ca178528c" \
                "c8d405c31f28352a548e5841e9e8cecedf84a5851a0cd532657bb3074e4efb46a34c504f2f148fd1c312e284a9ab6d58d473" \
                "d967e15458ddb9385fdf67ff1969fa7719f907a74e128083734acd2d000000000000407400030b6f00000000040000033b02" \
                "016bb2d6a7ec00000002016bb2d7cd4f02010081efc484301c895652aa3d9bd485a9efc772450c28f66e4343615023e2112f" \
                "f98fe370decf8d8b64330fd717584445ac866dc2facd8b856e63bdb8b15b5ed46c0b053b2c6c5c5c3f81efc48430330fd717" \
                "584445ac866dc2facd8b856e63bdb8b15b5ed46c0b053b2c6c5c5c3f019c5220a223d5d46ee3f08a29ce38e62f3fd8541893" \
                "b1dddec90dd26dea90313dc4702a1c82b7ecc7805e41a3d247da4c9c878ddfdd71fc6f3aee47b186cb9c7e60404a67acf862" \
                "33ab2f981b4387026cd87b7bb285d87f3734706b9ad43ba701012c94f2bbe49899679c54482eba49bf1d024476845e478f9c" \
                "ce3238f612edd761b3fb48f0c7441605031ddd09cbbdfc6a880194807f4328a7013bbae9a0afae4266ae90e69a456d259ae3" \
                "c34e5c095f5f6b231aacd8053c58741405b98328290302016bb2d7cd7e0201008991b4e605c07d49124e6a6d968a25be0059" \
                "6939e7cb27af821a3119d60e55fd075ab1838e8d8b64330fd717584445ac866dc2facd8b856e63bdb8b15b5ed46c0b053b2c" \
                "6c5c5c3f8991b4e605330fd717584445ac866dc2facd8b856e63bdb8b15b5ed46c0b053b2c6c5c5c3f0117646c5e142a35d2" \
                "b7d6522cb738dfadb3e4057b7027926173de1e514c5f151c92cf5723e76b54a04d42bea61f81c8b7313aabecb5089efcf24d" \
                "0b03b5f77d6473c4142ac021a041b5aed6ab7d224adf9ebe9f8767e4fd5bb3581b2ea62e1102012c94f2bbe49899679c5448" \
                "2eba49bf1d024476845e478f9cce3238f612edd761ef8c41822702b5caa37399d857b8601fc36fe66b451359f4f8764b9f6b" \
                "1bdbcd439fe4f540d31aa7434eb080ccdc59056c14f8d70099a362e00f315cd2e4140700000002016bb2da6b1901010098ef" \
                "b0a55a330fd717584445ac866dc2facd8b856e63bdb8b15b5ed46c0b053b2c6c5c5c3f98efa49a6a13f73852ebed3e60bad8" \
                "40bd44b979f9feeed90d33b9a6fa4b2871e131a854d3012c94f2bbe49899679c54482eba49bf1d024476845e478f9cce3238" \
                "f612edd761f30b32ffa46a5011d395975a56eefae023404f4bfebf47e376080b60d3900f4e79b4e9e6905e01ccc37993760c" \
                "fab2bd2abe9226493a5b5470ca0d707f0eaa0c00000000000000"

    def test_unmarshal(self):
        expected_keymr = "2568dbcd243487097dedc9764f4fa48079455de4bdb95ed844b99e2f9556bf7f"
        expected_body_mr = "a501d7500373bae88158d5e7062ca178528cc8d405c31f28352a548e5841e9e8"
        expected_prev_keymr = "cecedf84a5851a0cd532657bb3074e4efb46a34c504f2f148fd1c312e284a9ab"
        expected_prev_ledger_keymr = "6d58d473d967e15458ddb9385fdf67ff1969fa7719f907a74e128083734acd2d"
        expected_ec_exchange_rate = 16500
        expected_height = 199535
        expected_transaction_count = 4

        block = FactoidBlock.unmarshal(bytes.fromhex(expected_keymr), bytes.fromhex(TestFactoidBlock.test_data))
        assert block.keymr.hex() == expected_keymr
        assert block.header.body_mr.hex() == expected_body_mr
        assert block.header.prev_keymr.hex() == expected_prev_keymr
        assert block.header.prev_ledger_keymr.hex() == expected_prev_ledger_keymr
        assert block.header.ec_exchange_rate == expected_ec_exchange_rate
        assert block.header.height == expected_height
        assert block.header.transaction_count == expected_transaction_count
        transaction_count = 0
        for minute, transactions in block.transactions.items():
            transaction_count += len(transactions)
        assert transaction_count == expected_transaction_count

    def test_marshal(self):
        keymr = "2568dbcd243487097dedc9764f4fa48079455de4bdb95ed844b99e2f9556bf7f"
        block = FactoidBlock.unmarshal(bytes.fromhex(keymr), bytes.fromhex(TestFactoidBlock.test_data))
        assert block.marshal().hex() == TestFactoidBlock.test_data
