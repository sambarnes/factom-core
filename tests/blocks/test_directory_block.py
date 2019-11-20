import unittest

from factom_core.blocks import DirectoryBlock


class TestDirectoryBlock(unittest.TestCase):

    test_data = (
        "00fa92e5a268621e0e173b9615f6f154b2a8db4fbe02f8e960bcdf52b380404afa2d2ea96e06a775ece14fb21e14fd3df37c"
        "5e51c039789206d9c8402ed9ff9d9ca903ac246c3390e0d8e4238a431499056bba94cffb56ddad0a3a6c3a559e28bd5671ad"
        "bf018d3e9100030b240000000d000000000000000000000000000000000000000000000000000000000000000af493fe8bcf"
        "b9625c59387f1542e04ed06fd7beaf436daceb79de8651c62d19940000000000000000000000000000000000000000000000"
        "00000000000000000c95dcfe56875b826336c09059d1259401082042cdc99e9b7f41b2b6deadb5e26b000000000000000000"
        "000000000000000000000000000000000000000000000fff57136cc4967ac4e626bc7ab588cb8212863c61f91d3a594fa0cf"
        "dbab4e84d70f47c100669876d0c4692de4d1a4b6f69634da4abce161827d21af79dcddcd6b5f8ef24d68f2480580c5b99be8"
        "8f8bd4c858c7f4bc494cf2bd61dcfa868d189516dada470ad7b7755892cba35202f6e0b353ae57bed88282c95527ff295b08"
        "9ccc4b5eb4255b8cc130e4d8ea68181b6bef719df4f1e6426ea61d0c94f3fb5564187158d359a646dda403efb7ac94828245"
        "85cb8e351a9cf3fd05c4f083308d625bace4ac53e46f7a4ea373ed79b6b32b6d6d95447c72e48e9682bf444031fe0d2828d2"
        "c5f58d869ee142b6bdb1a1d868712e3fa471e3b378cd8622a915ab46a4e39d579398bc7e1c5be3b47a479049671c6006435e"
        "d6c8f808fef99e3ebbbcf94a35522c834022a4153c4ac92f61f22fad640647f91a21a65cf632f73871796651a38541e56c3b"
        "c10f957c88cbc55f2097c600d39a078b1636e589e503632d185f23f3f40383497f3d7a7c86ba067c4f14e792950ed748fce5"
        "9be27991bfc954fcdc22ee23a0bc05820479da7df89562cabb71ec61e2d5aa7b48af0da6e97a606e4540d08d5ac6a1a394e9"
        "82fb6a2ab8b516ee751c37420055141b94fe070bfe40f99b78c9f92c20262afa5671a021be07846388dbdef1251daa1d1089"
        "c98f499b5c6dbec96faef4f855182fa8d1475427eed27fc18f4c8deec588d1c252b7f8b805d0521d0e99686dd471f472d52b"
        "8fcba06f675413f5664c376ebb527cc54cb312a0401879366b3d72a1844b3ca0da1009545ffa8e4038f80da1528cb572ab09"
        "df02abdb74f44ddf1762bf578790219ff012b5786813b51229770a343724d8c9facbecd7f5b2aaea4c6040d0d312b0c663f8"
        "ffbd34e82056cf285abfabfbef230928d8a86de42c768fd1b312302a56a4a5e4329826f7eec7ce8e445e479553"
    )

    def test_unmarshal(self):
        expected_network_id = "fa92e5a2"
        expected_body_mr = "68621e0e173b9615f6f154b2a8db4fbe02f8e960bcdf52b380404afa2d2ea96e"
        expected_prev_keymr = "06a775ece14fb21e14fd3df37c5e51c039789206d9c8402ed9ff9d9ca903ac24"
        expected_prev_full_hash = "6c3390e0d8e4238a431499056bba94cffb56ddad0a3a6c3a559e28bd5671adbf"
        expected_timestamp = 26033809 * 60
        expected_height = 199460
        expected_admin_block_lookup_hash = "f493fe8bcfb9625c59387f1542e04ed06fd7beaf436daceb79de8651c62d1994"
        expected_entry_credit_block_header_hash = "95dcfe56875b826336c09059d1259401082042cdc99e9b7f41b2b6deadb5e26b"
        expected_factoid_block_keymr = "ff57136cc4967ac4e626bc7ab588cb8212863c61f91d3a594fa0cfdbab4e84d7"
        expected_entry_blocks = [
            {
                "chain_id": "0f47c100669876d0c4692de4d1a4b6f69634da4abce161827d21af79dcddcd6b",
                "keymr": "5f8ef24d68f2480580c5b99be88f8bd4c858c7f4bc494cf2bd61dcfa868d1895",
            },
            {
                "chain_id": "16dada470ad7b7755892cba35202f6e0b353ae57bed88282c95527ff295b089c",
                "keymr": "cc4b5eb4255b8cc130e4d8ea68181b6bef719df4f1e6426ea61d0c94f3fb5564",
            },
            {
                "chain_id": "187158d359a646dda403efb7ac9482824585cb8e351a9cf3fd05c4f083308d62",
                "keymr": "5bace4ac53e46f7a4ea373ed79b6b32b6d6d95447c72e48e9682bf444031fe0d",
            },
            {
                "chain_id": "2828d2c5f58d869ee142b6bdb1a1d868712e3fa471e3b378cd8622a915ab46a4",
                "keymr": "e39d579398bc7e1c5be3b47a479049671c6006435ed6c8f808fef99e3ebbbcf9",
            },
            {
                "chain_id": "4a35522c834022a4153c4ac92f61f22fad640647f91a21a65cf632f738717966",
                "keymr": "51a38541e56c3bc10f957c88cbc55f2097c600d39a078b1636e589e503632d18",
            },
            {
                "chain_id": "5f23f3f40383497f3d7a7c86ba067c4f14e792950ed748fce59be27991bfc954",
                "keymr": "fcdc22ee23a0bc05820479da7df89562cabb71ec61e2d5aa7b48af0da6e97a60",
            },
            {
                "chain_id": "6e4540d08d5ac6a1a394e982fb6a2ab8b516ee751c37420055141b94fe070bfe",
                "keymr": "40f99b78c9f92c20262afa5671a021be07846388dbdef1251daa1d1089c98f49",
            },
            {
                "chain_id": "9b5c6dbec96faef4f855182fa8d1475427eed27fc18f4c8deec588d1c252b7f8",
                "keymr": "b805d0521d0e99686dd471f472d52b8fcba06f675413f5664c376ebb527cc54c",
            },
            {
                "chain_id": "b312a0401879366b3d72a1844b3ca0da1009545ffa8e4038f80da1528cb572ab",
                "keymr": "09df02abdb74f44ddf1762bf578790219ff012b5786813b51229770a343724d8",
            },
            {
                "chain_id": "c9facbecd7f5b2aaea4c6040d0d312b0c663f8ffbd34e82056cf285abfabfbef",
                "keymr": "230928d8a86de42c768fd1b312302a56a4a5e4329826f7eec7ce8e445e479553",
            },
        ]
        block = DirectoryBlock.unmarshal(bytes.fromhex(TestDirectoryBlock.test_data))
        assert block.header.network_id.hex() == expected_network_id
        assert block.header.body_mr.hex() == expected_body_mr
        assert block.header.prev_keymr.hex() == expected_prev_keymr
        assert block.header.prev_full_hash.hex() == expected_prev_full_hash
        assert block.header.timestamp == expected_timestamp
        assert block.header.height == expected_height
        assert block.body.admin_block_lookup_hash.hex() == expected_admin_block_lookup_hash
        assert block.body.entry_credit_block_header_hash.hex() == expected_entry_credit_block_header_hash
        assert block.body.factoid_block_keymr.hex() == expected_factoid_block_keymr
        assert len(block.body.entry_blocks) == len(expected_entry_blocks)
        for i, entry_block in enumerate(block.body.entry_blocks):
            assert entry_block.get("chain_id").hex() == expected_entry_blocks[i].get("chain_id")
            assert entry_block.get("keymr").hex() == expected_entry_blocks[i].get("keymr")

    def test_marshal(self):
        block = DirectoryBlock.unmarshal(bytes.fromhex(TestDirectoryBlock.test_data))
        assert block.marshal().hex() == TestDirectoryBlock.test_data

    def test_keymr(self):
        expected_keymr = "aed3e8a8a3e9515a60eee86e176dc07e503f5a5481a4aad52d344d6f6c8e9613"
        block = DirectoryBlock.unmarshal(bytes.fromhex(TestDirectoryBlock.test_data))
        assert block.keymr.hex() == expected_keymr, "{} != {}".format(block.keymr.hex(), expected_keymr)

    def test_body_mr(self):
        expected_body_mr = "68621e0e173b9615f6f154b2a8db4fbe02f8e960bcdf52b380404afa2d2ea96e"
        block = DirectoryBlock.unmarshal(bytes.fromhex(TestDirectoryBlock.test_data))
        assert block.body.merkle_root.hex() == expected_body_mr, "{} != {}".format(
            block.body.merkle_root.hex(), expected_body_mr
        )
