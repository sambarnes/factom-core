import unittest

from factom_core.blocks import EntryBlock


class TestEntryBlock(unittest.TestCase):

    test_data = "b312a0401879366b3d72a1844b3ca0da1009545ffa8e4038f80da1528cb572abb787ef87fcb569ce117c1667a0eaadf0797c" \
                "249e6a1e9a2fca5b039fbf180a73fdadf8de663a045e4e5927bd71f16718cd036429cc4e64f194116a50fd44adf54843fa0c" \
                "a18bff6d6b5c935f18344d1cddeb67f294e1f067aa26a738a92e0cbf00000af700030b240000000f1503d1d8b8d8036ad7cb" \
                "270321996c0b1f050b4ebaea79ab48d007071cf370f27046dad9d0da9ffb27f9634e0665280f7f46bfe1f8e3a194f168718c" \
                "bdd28e26b056456d9176e6c80a67a89e471a75c164bf19bdf0e0550af4e66943fad8e6c820a51dae748935ca3f52ee7f8921" \
                "21290c12fa5fb71815271a9dc35947dc4cd8b2491a8b8b8bb8395fc20f9abd6779e90aaa22a38c0508c685e944082f779176" \
                "23c29da73f7de3ee42a111fab451c376f3cadb7e12923fa05bc01a2150ff349db088d1744550627b82b3a9159c6acb0e3676" \
                "cdb21d70cba5144aac1c6ce1a231a181dd737eedc079eaf16181f6468273210036db00669b405db6958aa711cbf264a2d4bf" \
                "a2b1c7e1093b9ae88ac8efb305f50798cfa8c07bf3699cab0aef3983170b3dc2def10bda963be05699ecd6ac8f4692573f4a" \
                "8dd36b4a17392db70ff7dc9e6f420e3b7e7f08e7d144cfe03cbc40f35abd27821a4769bccfa054e44b005dd03aea8dcb5763" \
                "a43f8e0fe6fd16c09d4f573d2b2f1df1e5fff8be372259bb2159e8322a02a299812ca3170eef0c6ca90ef847bc69d4e5a663" \
                "57735fb18993563030a164e795050947415f0f4970b076ca74ecf491aecf1e8e714481ccd7d8000000000000000000000000" \
                "000000000000000000000000000000000000000a"

    def test_unmarshal(self):
        expected_chain_id = "b312a0401879366b3d72a1844b3ca0da1009545ffa8e4038f80da1528cb572ab"
        expected_body_mr = "b787ef87fcb569ce117c1667a0eaadf0797c249e6a1e9a2fca5b039fbf180a73"
        expected_prev_keymr = "fdadf8de663a045e4e5927bd71f16718cd036429cc4e64f194116a50fd44adf5"
        expected_prev_full_hash = "4843fa0ca18bff6d6b5c935f18344d1cddeb67f294e1f067aa26a738a92e0cbf"
        expected_sequence = 2807
        expected_height = 199460
        expected_entry_hashes = {
            10: [
                "1503d1d8b8d8036ad7cb270321996c0b1f050b4ebaea79ab48d007071cf370f2",
                "7046dad9d0da9ffb27f9634e0665280f7f46bfe1f8e3a194f168718cbdd28e26",
                "b056456d9176e6c80a67a89e471a75c164bf19bdf0e0550af4e66943fad8e6c8",
                "20a51dae748935ca3f52ee7f892121290c12fa5fb71815271a9dc35947dc4cd8",
                "b2491a8b8b8bb8395fc20f9abd6779e90aaa22a38c0508c685e944082f779176",
                "23c29da73f7de3ee42a111fab451c376f3cadb7e12923fa05bc01a2150ff349d",
                "b088d1744550627b82b3a9159c6acb0e3676cdb21d70cba5144aac1c6ce1a231",
                "a181dd737eedc079eaf16181f6468273210036db00669b405db6958aa711cbf2",
                "64a2d4bfa2b1c7e1093b9ae88ac8efb305f50798cfa8c07bf3699cab0aef3983",
                "170b3dc2def10bda963be05699ecd6ac8f4692573f4a8dd36b4a17392db70ff7",
                "dc9e6f420e3b7e7f08e7d144cfe03cbc40f35abd27821a4769bccfa054e44b00",
                "5dd03aea8dcb5763a43f8e0fe6fd16c09d4f573d2b2f1df1e5fff8be372259bb",
                "2159e8322a02a299812ca3170eef0c6ca90ef847bc69d4e5a66357735fb18993",
                "563030a164e795050947415f0f4970b076ca74ecf491aecf1e8e714481ccd7d8",
            ]
        }

        block = EntryBlock.unmarshal(bytes.fromhex(TestEntryBlock.test_data))
        assert block.header.chain_id.hex() == expected_chain_id
        assert block.header.body_mr.hex() == expected_body_mr
        assert block.header.prev_keymr.hex() == expected_prev_keymr
        assert block.header.prev_full_hash.hex() == expected_prev_full_hash
        assert block.header.sequence == expected_sequence
        assert block.header.height == expected_height
        for minute, entry_hashes in block.entry_hashes.items():
            for i, entry_hash in enumerate(entry_hashes):
                assert entry_hash.hex() == expected_entry_hashes[minute][i]

    def test_marshal(self):
        block = EntryBlock.unmarshal(bytes.fromhex(TestEntryBlock.test_data))
        assert block.marshal().hex() == TestEntryBlock.test_data

    def test_keymr(self):
        expected_keymr = "09df02abdb74f44ddf1762bf578790219ff012b5786813b51229770a343724d8"
        block = EntryBlock.unmarshal(bytes.fromhex(TestEntryBlock.test_data))
        assert block.keymr.hex() == expected_keymr

    def test_body_mr(self):
        expected_body_mr = "b787ef87fcb569ce117c1667a0eaadf0797c249e6a1e9a2fca5b039fbf180a73"
        block = EntryBlock.unmarshal(bytes.fromhex(TestEntryBlock.test_data))
        assert block.body_mr.hex() == block.header.body_mr.hex() == expected_body_mr
