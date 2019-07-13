import unittest

from factom_core.blocks import EntryCreditBlock
from factom_core.block_elements import ChainCommit, EntryCommit, BalanceIncrease


class TestEntryCreditBlock(unittest.TestCase):

    # TODO: there must be a better way...
    test_data = (
        "000000000000000000000000000000000000000000000000000000000000000c2f9d25a35dd9569815262c46d3fde3a7d658"
        "9ab110464b01900f37f28c058b1ba42ad12da47374765aab409d70cb30c5938c89160366835d41eccc7cda0374b5b44dca79"
        "fb958a5198a74bceaa6faeff6ff7c3b7982ff8b2944a1269b9341a0400030b24000000000000000029000000000000122b01"
        "010300016bb028a000ad622780fd32b0986bc955e177c62eec0e17a48eef267aa862e240a3c3271677011d8aabf98c7a4879"
        "ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f58056f8a9af0ff67c3b45adb1a3c6c68de30932c4ebcece5e4382aeeb"
        "a45c77b8b50fe09d566758333c9ff0513ca00bca640b80d8541906e2f977cb675c07dfc940050300016bb0289f65f9555109"
        "8e03bf6d5a00989f37b2cec7f9e06e2d4b1c62014bf531791d3301bc021d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f"
        "55ddb3e2d36b5742f5805616bf98fa99f7c382e4604e221f34ea0022a78554c6592b5be62305d00ea41329245a39d115c8fe"
        "b28644d45a0bb35d621a1a42b0d37c56512525706e8ba90c090300016bb028a0eabd2a248f6c52a2c32b1c2067261f783d81"
        "a38d03ed7af90bafaf7aaa668b60fa021d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f580569292"
        "87ec72bb294ac54c5ee36f758670b9ce56edf0b19b89f67affda76790c5f6f3ec1a4d1701fa5c553d9c2a14e5c9a880d19b8"
        "8166b48b0f50c05271b4ff0a0300016bb028a19739e440db4ab07ef3cb57c9301367d5e95e87996d4d1c985e1ffa80fe3403"
        "c810011d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f580569a6ffd3fb127f1f6c81b8ef6d52cc1"
        "b8d15a7dcb897d3b088267052610fc085adb73da02c1ecd87d4046018bc342d4ce67156b9e6911a95ef00c6d0c41f2010603"
        "00016bb029666d1c986f8d7432fbbb66d69f07df6cbe1e5b294a786bfb4c4b0e094777c4cfc2580165a068d8d2a7ba79d5a6"
        "943740862f35214e8b31584d6a513fc51087160ebbe6f614a900a7f139deb75d60d7f183245260241f68beac241a5c6fd89d"
        "3348216a47750b2dbce95b62858d639cc641b9d566e638ca44b7f2df48c69cfa9420fe0101020300016bb029d1fb99ab1224"
        "e0755acd0577ded2cb3477fd105dd1fafbd025a998dd580618e908bd021d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f"
        "55ddb3e2d36b5742f5805610ee876b8ceef37d49c6d8be2e2589ab4649d3f8f50fb2e70b722c61182131322a0d587896c907"
        "560d2de0ec906226ee97840d74362b7875d8d94c04655389040300016bb029d29768499dfa4472dbb1bf139fbd3e66d5307f"
        "d30049cc2a3cdb8554eb62f464d318011d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f58056f233"
        "9ae60186af5febe645f01954914e841046c06db3f91fe58447abb2b118a139c087679eb9b9952e452042099d03e314b32aa5"
        "52fd6551028487796a6cd8060200016bb029d361f7e02792e58aa6f9b7d8f15d4681532e642ecd322b1d7e15405b937efbc9"
        "404d1c4004862cf670cc0015a6c268fb898040629a64f039c6c3514c0ef1a99fb920fabc28db5d9a4127a634e6b163f8f5f4"
        "055a2bae16ef62cb54264b610fc462420b1d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f580562d"
        "c1becca5813131c3ad9dcd354142968df848df392d55dfd45cdd5015fec97094f521d26ab2bb3fe9f3b78f4761becc852d1c"
        "362ef2cd86facb3ce526ea090d0200016bb029d405d573e1c94dbb32dad6da21a5187750b3416d714f48e01f71daf3b52193"
        "88464843111f5de168f565faa031ded22b6ce1e771eb505b67112562436f9249a638d3dc0d3017ec414f680f8cbad6355e0f"
        "8050dfaac87b899aafa313687e0e039ecb0b1d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f58056"
        "4defc68b276f1a79f8c1b76849fd9e5c51466d3122ba5ab8fc570f4fd6123dbcb05fba73378f2223ca023be4810e84570e91"
        "be67cbeeafff0071540f9252230d0200016bb029d4bd7491263b7ee1531668588659dd1047a14d3fe195c429d2d2ebe1206b"
        "d038a53a7d3fa6f1a05a93795e35b977865d49d35f41bc72a999d8a9a51140fdea894dd8deec5c0e29d49a3ca89280c8cdc7"
        "4f2b43efdca912361a1ef3768affe8cec9ce0b1d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f580"
        "56c39eb17baad77e72d40b2f116c2bd1bca2ae58e49cd8fe5bcdf0fa2fc52f21d38faac6f4caf5bd0c9a5510e3789d4bf591"
        "80b2003d5ed793f187bc3e127db60901030300016bb02ad5a3570ecdbe6f6f5e62527c4ceb7db3bb6d2c7e41ab631a1313bd"
        "b14a7a308e4523021d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f58056403f13a9ffc61a5e1e3e"
        "d26f142406af9b3ef9d0ba2ec365624c39012c58b6fbe10e0a0f1801c11c6fb66245782e52fedcaf6b7c4c18c989fe654b5b"
        "0f5118030300016bb02ad65263e8e541e082d003b5b16d146971539f473205c3ad23b81df623ffd653bad787011d8aabf98c"
        "7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f580566d48b6b220a957981c00d1a62515f6fa59aa1c619d79e2"
        "e05ae99d647856b75be0b150b74288c83f8ecb045ae450155ca6dfac211adf88bd22999720f5e732000200016bb02ad6fd14"
        "8e1d95fb770e4f57f26faaf3f061ee314bf21a2eacbd84014c143862e30d3f646572a7eb488d371a550e418b40fbb6d4d5e8"
        "dc30fb5f3fa6935e5c1f8e7d8847f24899baed0bacd818606e6ec3aa55a981eb266533e7fa983ae10019009a3a0b1d8aabf9"
        "8c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f58056734601e8a21e71e0d99714b4bb4fe5b982e15c3f37eb"
        "2e512100b40a962695e6aa80438fd9d1337c43b26c91be0dc2ffa1bec1a70a1d1d3163dcb8de936a8d060200016bb02ad7b7"
        "bb6900a5fe9ba9ae00757b9f3402c258b670ce2ef6d1a8d60d1fddf6c5cf0666020b7c63bbcb625cd2d637e0bf7e3f69886a"
        "d0e2011b55213f26568a7288832748483e810e749a946122b93b5ce97ff596f79403a134863fc593ad8716ff58a00b1d8aab"
        "f98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f580567daed09c95947b5521f95293eb1aeb6b35d125a24a"
        "a8256b0cfe6385835b3b5f1aaeb2b74c292769987810c72b6c1178050f10a0829097f73f1d2e8dd228810b0200016bb02ad8"
        "8456a14050a3d0d37828199bc45fcd64ca197cc2b1157e888121ebfd4a42a0682c63258fe7829cc15de9d8560031e3205857"
        "a6c45c110e9d1f4600da9207174b4438d74323b32b7c2d34a86635a244737ca1177739961daaabdc55f78a35c2daa20b1d8a"
        "abf98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f58056aae459960aa513c0792e34a6f884c445f04d3ab5"
        "e28f5509131fd2a8faf8af41ca41b57d3fb7b7f215318276fb02d2de3b23c73f4e356fec1297a21470110c09010401050106"
        "0107010801090300016bb03043ed1503d1d8b8d8036ad7cb270321996c0b1f050b4ebaea79ab48d007071cf370f201d4f933"
        "6bb919ee384e2f3adfc5b9f54d55c6385f99012a1051c0564184b671c7d6437eadcedbb248b4015510ef019b5e5908de606a"
        "4c1da1627eafd48494685b5b4b390ea05f0f4f695cc16598d5bbc8066080b1b4fdf5e3c783ae6159e77a090300016bb03053"
        "b3170b3dc2def10bda963be05699ecd6ac8f4692573f4a8dd36b4a17392db70ff701166041975f981c678cda28aedb3cc5a3"
        "713668ace7f2c8b2fa4c04dbbf9035668f8ace3b96a170094e373b7e7e39753e605b7795f3a58e586f032a5497cb838b36fb"
        "c5a3ffd07780c9e08a35847d0d27e8694d4a307d79d117dc8d8f798b83040300016bb03053b2b2491a8b8b8bb8395fc20f9a"
        "bd6779e90aaa22a38c0508c685e944082f77917601166041975f981c678cda28aedb3cc5a3713668ace7f2c8b2fa4c04dbbf"
        "9035660e537d2b9029175b48defc5c781490ebaafdfb09c32be7aa3b360dde9b8ccee143e92c340855db08876ca03dedcc2b"
        "f8cdfbb3bc6d3e68fe2619134a9f0522070300016bb03053aa7046dad9d0da9ffb27f9634e0665280f7f46bfe1f8e3a194f1"
        "68718cbdd28e2601166041975f981c678cda28aedb3cc5a3713668ace7f2c8b2fa4c04dbbf903566a645c3f207d119313ad3"
        "0bd5a4da49cec5bfed5a4037339f85befed14abb0cb30f0f505a1ab62ca8d894b9f50cb3bea1be59afdbdf3ca65ce5cee78a"
        "2e99ac020300016bb03053b123c29da73f7de3ee42a111fab451c376f3cadb7e12923fa05bc01a2150ff349d01166041975f"
        "981c678cda28aedb3cc5a3713668ace7f2c8b2fa4c04dbbf9035664fb61b2d9b88b99835203933bb60c55f1f1d317ea8368a"
        "32cd7193f00aa2ac685d43913583a56064719960af3695f9b638229ddae3f8e8bcadbbeb20d0da13030300016bb03053b25d"
        "d03aea8dcb5763a43f8e0fe6fd16c09d4f573d2b2f1df1e5fff8be372259bb01166041975f981c678cda28aedb3cc5a37136"
        "68ace7f2c8b2fa4c04dbbf9035662639f55f2cf3f496ae82a2c630607dc80975406841155b8c4623d425ec7fd7d67f70a829"
        "2c581ee23115bc5508562fb38e3625ea12b7567c17d5c94ba722ae0a0300016bb03053b7a181dd737eedc079eaf16181f646"
        "8273210036db00669b405db6958aa711cbf201166041975f981c678cda28aedb3cc5a3713668ace7f2c8b2fa4c04dbbf9035"
        "66b77ddc8a5c97f95dd2806a0d52fe0bc0690ae4b54bade414dcd773d74c7c2206a06fb9b2c5a9fd1538930ea7efb9c3ff1e"
        "9e38f504ebb816c5c3e5f963fa6a0e0300016bb03053b464a2d4bfa2b1c7e1093b9ae88ac8efb305f50798cfa8c07bf3699c"
        "ab0aef398301166041975f981c678cda28aedb3cc5a3713668ace7f2c8b2fa4c04dbbf90356648a7527beef5007ad0d67770"
        "7eb943b4576797eeb6bc61abaaccbafb6a09c0914795dec52b5b4aa0ec6ce1371ef0d113108d6a7f699728047bcb40280398"
        "580a0300016bb03053b5dc9e6f420e3b7e7f08e7d144cfe03cbc40f35abd27821a4769bccfa054e44b0001166041975f981c"
        "678cda28aedb3cc5a3713668ace7f2c8b2fa4c04dbbf903566eb968d5df2c5b83688bf03e4630bfa34b26dc099490047df1f"
        "dc90a8d5b3b9c08975db451aee4bef7148a08bfd06fe353ec3c04cd2e0b2d21d2256caf750d6070300016bb03053ac20a51d"
        "ae748935ca3f52ee7f892121290c12fa5fb71815271a9dc35947dc4cd801166041975f981c678cda28aedb3cc5a3713668ac"
        "e7f2c8b2fa4c04dbbf9035661666ccf3b5fa35fabfaaa8e901a2b29b6d99fe6001704564815fbf22c1b66731fe96ff94dc3a"
        "5a2f818c7ac6020e8bbcacf1eaba566adc56ea5f5b3b4880c3010300016bb03053b52159e8322a02a299812ca3170eef0c6c"
        "a90ef847bc69d4e5a66357735fb1899301166041975f981c678cda28aedb3cc5a3713668ace7f2c8b2fa4c04dbbf903566db"
        "280a4c8a53c02d629d146364e88d932622b3373cd7287eb3c2a920bda0c338507d7fc724843673021f7653dd3c7719766082"
        "2d4f70a736b8908249b8d6d20d0300016bb03053b4b088d1744550627b82b3a9159c6acb0e3676cdb21d70cba5144aac1c6c"
        "e1a23101166041975f981c678cda28aedb3cc5a3713668ace7f2c8b2fa4c04dbbf9035661abe2bcf93ed27ec2f9d7a0b9ef2"
        "b573c257a6d317c10360ba13712086ff8d2751b8d687ef75be994d7baeffe084c30bab2c09e4ed1c679d661d81b7e0049c04"
        "0300016bb03053b6b056456d9176e6c80a67a89e471a75c164bf19bdf0e0550af4e66943fad8e6c801166041975f981c678c"
        "da28aedb3cc5a3713668ace7f2c8b2fa4c04dbbf90356649025f14c80d0d1e8b15b14e8e81bb3d0e07fb365c73142a9cc92d"
        "f62a2a4d9fee595d4736c2a4b1c4bfc3057612565f2d94e39844439e19e62e15c8f32476090300016bb03053b6563030a164"
        "e795050947415f0f4970b076ca74ecf491aecf1e8e714481ccd7d801166041975f981c678cda28aedb3cc5a3713668ace7f2"
        "c8b2fa4c04dbbf9035660d92ee04be6c9c6a0e75acc0d95d24655b14ede5763421fd2f15802ccd3dc6f80ecdbef58474875c"
        "35abcbabee7cec11448733a3caf7c5e32ae9b7cf4a06e30b0300016bb0308fcf0a5bd6faacca17d36b47663b9764429405ac"
        "aec36be26aae2cb9bd44f76a14eb01d87869bc85e802bed893ac48ad07bbee8aaf625035af3fcd145c55273013431a5dd229"
        "9497247d1850711fcf98a07709b32d0a1251fea5d0b63c52545a8c49bc5c3eeae014bdafbb0044e25a1b5ab02496342a4b7a"
        "a8f8089cd740b9198067030300016bb03093b9eba1585feaba30a4de4a1766aeb537d53ca2a1a6fd33c0ca0e606d85d7de9a"
        "6e01d87869bc85e802bed893ac48ad07bbee8aaf625035af3fcd145c55273013431a4fa3bd8ff5e498e3809c40d1a08e35ab"
        "f04f2b5a240a0c782793ed1515ae4de8c9093f4bfd6c79644850b7f2132127a435e676baef785616928e3317ce15d206010a"
    )

    def test_unmarshal(self):
        block = EntryCreditBlock.unmarshal(
            bytes.fromhex(TestEntryCreditBlock.test_data)
        )
        expected_body_hash = (
            "2f9d25a35dd9569815262c46d3fde3a7d6589ab110464b01900f37f28c058b1b"
        )
        expected_prev_header_hash = (
            "a42ad12da47374765aab409d70cb30c5938c89160366835d41eccc7cda0374b5"
        )
        expected_prev_full_hash = (
            "b44dca79fb958a5198a74bceaa6faeff6ff7c3b7982ff8b2944a1269b9341a04"
        )
        expected_height = 199460
        expected_objects = {
            1: [],
            2: [
                {
                    "ecid": 0x03,
                    "timestamp": "016bb028a000",
                    "entry_hash": "ad622780fd32b0986bc955e177c62eec0e17a48eef267aa862e240a3c3271677",
                    "ec_spent": 1,
                    "ec_public_key": "1d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f58056",
                    "signature": "f8a9af0ff67c3b45adb1a3c6c68de30932c4ebcece5e4382aeeba45c77b8b50fe09d566758333c9ff0513"
                    "ca00bca640b80d8541906e2f977cb675c07dfc94005",
                },
                {
                    "ecid": 0x03,
                    "timestamp": "016bb0289f65",
                    "entry_hash": "f95551098e03bf6d5a00989f37b2cec7f9e06e2d4b1c62014bf531791d3301bc",
                    "ec_spent": 2,
                    "ec_public_key": "1d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f58056",
                    "signature": "16bf98fa99f7c382e4604e221f34ea0022a78554c6592b5be62305d00ea41329245a39d115c8feb28644d"
                    "45a0bb35d621a1a42b0d37c56512525706e8ba90c09",
                },
                {
                    "ecid": 0x03,
                    "timestamp": "016bb028a0ea",
                    "entry_hash": "bd2a248f6c52a2c32b1c2067261f783d81a38d03ed7af90bafaf7aaa668b60fa",
                    "ec_spent": 2,
                    "ec_public_key": "1d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f58056",
                    "signature": "929287ec72bb294ac54c5ee36f758670b9ce56edf0b19b89f67affda76790c5f6f3ec1a4d1701fa5c553d"
                    "9c2a14e5c9a880d19b88166b48b0f50c05271b4ff0a",
                },
                {
                    "ecid": 0x03,
                    "timestamp": "016bb028a197",
                    "entry_hash": "39e440db4ab07ef3cb57c9301367d5e95e87996d4d1c985e1ffa80fe3403c810",
                    "ec_spent": 1,
                    "ec_public_key": "1d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f58056",
                    "signature": "9a6ffd3fb127f1f6c81b8ef6d52cc1b8d15a7dcb897d3b088267052610fc085adb73da02c1ecd87d40460"
                    "18bc342d4ce67156b9e6911a95ef00c6d0c41f20106",
                },
                {
                    "ecid": 0x03,
                    "timestamp": "016bb029666d",
                    "entry_hash": "1c986f8d7432fbbb66d69f07df6cbe1e5b294a786bfb4c4b0e094777c4cfc258",
                    "ec_spent": 1,
                    "ec_public_key": "65a068d8d2a7ba79d5a6943740862f35214e8b31584d6a513fc51087160ebbe6",
                    "signature": "f614a900a7f139deb75d60d7f183245260241f68beac241a5c6fd89d3348216a47750b2dbce95b62858d6"
                    "39cc641b9d566e638ca44b7f2df48c69cfa9420fe01",
                },
            ],
            3: [
                {
                    "ecid": 0x03,
                    "timestamp": "016bb029d1fb",
                    "entry_hash": "99ab1224e0755acd0577ded2cb3477fd105dd1fafbd025a998dd580618e908bd",
                    "ec_spent": 2,
                    "ec_public_key": "1d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f58056",
                    "signature": "10ee876b8ceef37d49c6d8be2e2589ab4649d3f8f50fb2e70b722c61182131322a0d587896c907560d2de"
                    "0ec906226ee97840d74362b7875d8d94c0465538904",
                },
                {
                    "ecid": 0x03,
                    "timestamp": "016bb029d297",
                    "entry_hash": "68499dfa4472dbb1bf139fbd3e66d5307fd30049cc2a3cdb8554eb62f464d318",
                    "ec_spent": 1,
                    "ec_public_key": "1d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f58056",
                    "signature": "f2339ae60186af5febe645f01954914e841046c06db3f91fe58447abb2b118a139c087679eb9b9952e452"
                    "042099d03e314b32aa552fd6551028487796a6cd806",
                },
                {
                    "ecid": 0x02,
                    "timestamp": "016bb029d361",
                    "chain_id_hash": "f7e02792e58aa6f9b7d8f15d4681532e642ecd322b1d7e15405b937efbc9404d",
                    "commit_weld": "1c4004862cf670cc0015a6c268fb898040629a64f039c6c3514c0ef1a99fb920",
                    "entry_hash": "fabc28db5d9a4127a634e6b163f8f5f4055a2bae16ef62cb54264b610fc46242",
                    "ec_spent": 11,
                    "ec_public_key": "1d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f58056",
                    "signature": "2dc1becca5813131c3ad9dcd354142968df848df392d55dfd45cdd5015fec97094f521d26ab2bb3fe9f3b"
                    "78f4761becc852d1c362ef2cd86facb3ce526ea090d",
                },
                {
                    "ecid": 0x02,
                    "timestamp": "016bb029d405",
                    "chain_id_hash": "d573e1c94dbb32dad6da21a5187750b3416d714f48e01f71daf3b52193884648",
                    "commit_weld": "43111f5de168f565faa031ded22b6ce1e771eb505b67112562436f9249a638d3",
                    "entry_hash": "dc0d3017ec414f680f8cbad6355e0f8050dfaac87b899aafa313687e0e039ecb",
                    "ec_spent": 11,
                    "ec_public_key": "1d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f58056",
                    "signature": "4defc68b276f1a79f8c1b76849fd9e5c51466d3122ba5ab8fc570f4fd6123dbcb05fba73378f2223ca023"
                    "be4810e84570e91be67cbeeafff0071540f9252230d",
                },
                {
                    "ecid": 0x02,
                    "timestamp": "016bb029d4bd",
                    "chain_id_hash": "7491263b7ee1531668588659dd1047a14d3fe195c429d2d2ebe1206bd038a53a",
                    "commit_weld": "7d3fa6f1a05a93795e35b977865d49d35f41bc72a999d8a9a51140fdea894dd8",
                    "entry_hash": "deec5c0e29d49a3ca89280c8cdc74f2b43efdca912361a1ef3768affe8cec9ce",
                    "ec_spent": 11,
                    "ec_public_key": "1d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f58056",
                    "signature": "c39eb17baad77e72d40b2f116c2bd1bca2ae58e49cd8fe5bcdf0fa2fc52f21d38faac6f4caf5bd0c9a551"
                    "0e3789d4bf59180b2003d5ed793f187bc3e127db609",
                },
            ],
            4: [
                {
                    "ecid": 0x03,
                    "timestamp": "016bb02ad5a3",
                    "entry_hash": "570ecdbe6f6f5e62527c4ceb7db3bb6d2c7e41ab631a1313bdb14a7a308e4523",
                    "ec_spent": 2,
                    "ec_public_key": "1d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f58056",
                    "signature": "403f13a9ffc61a5e1e3ed26f142406af9b3ef9d0ba2ec365624c39012c58b6fbe10e0a0f1801c11c6fb66"
                    "245782e52fedcaf6b7c4c18c989fe654b5b0f511803",
                },
                {
                    "ecid": 0x03,
                    "timestamp": "016bb02ad652",
                    "entry_hash": "63e8e541e082d003b5b16d146971539f473205c3ad23b81df623ffd653bad787",
                    "ec_spent": 1,
                    "ec_public_key": "1d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f58056",
                    "signature": "6d48b6b220a957981c00d1a62515f6fa59aa1c619d79e2e05ae99d647856b75be0b150b74288c83f8ecb0"
                    "45ae450155ca6dfac211adf88bd22999720f5e73200",
                },
                {
                    "ecid": 0x02,
                    "timestamp": "016bb02ad6fd",
                    "chain_id_hash": "148e1d95fb770e4f57f26faaf3f061ee314bf21a2eacbd84014c143862e30d3f",
                    "commit_weld": "646572a7eb488d371a550e418b40fbb6d4d5e8dc30fb5f3fa6935e5c1f8e7d88",
                    "entry_hash": "47f24899baed0bacd818606e6ec3aa55a981eb266533e7fa983ae10019009a3a",
                    "ec_spent": 11,
                    "ec_public_key": "1d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f58056",
                    "signature": "734601e8a21e71e0d99714b4bb4fe5b982e15c3f37eb2e512100b40a962695e6aa80438fd9d1337c43b26"
                    "c91be0dc2ffa1bec1a70a1d1d3163dcb8de936a8d06",
                },
                {
                    "ecid": 0x02,
                    "timestamp": "016bb02ad7b7",
                    "chain_id_hash": "bb6900a5fe9ba9ae00757b9f3402c258b670ce2ef6d1a8d60d1fddf6c5cf0666",
                    "commit_weld": "020b7c63bbcb625cd2d637e0bf7e3f69886ad0e2011b55213f26568a72888327",
                    "entry_hash": "48483e810e749a946122b93b5ce97ff596f79403a134863fc593ad8716ff58a0",
                    "ec_spent": 11,
                    "ec_public_key": "1d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f58056",
                    "signature": "7daed09c95947b5521f95293eb1aeb6b35d125a24aa8256b0cfe6385835b3b5f1aaeb2b74c29276998781"
                    "0c72b6c1178050f10a0829097f73f1d2e8dd228810b",
                },
                {
                    "ecid": 0x02,
                    "timestamp": "016bb02ad884",
                    "chain_id_hash": "56a14050a3d0d37828199bc45fcd64ca197cc2b1157e888121ebfd4a42a0682c",
                    "commit_weld": "63258fe7829cc15de9d8560031e3205857a6c45c110e9d1f4600da9207174b44",
                    "entry_hash": "38d74323b32b7c2d34a86635a244737ca1177739961daaabdc55f78a35c2daa2",
                    "ec_spent": 11,
                    "ec_public_key": "1d8aabf98c7a4879ba4a2c9e6d923631d65c7c2d4f55ddb3e2d36b5742f58056",
                    "signature": "aae459960aa513c0792e34a6f884c445f04d3ab5e28f5509131fd2a8faf8af41ca41b57d3fb7b7f215318"
                    "276fb02d2de3b23c73f4e356fec1297a21470110c09",
                },
            ],
            5: [],
            6: [],
            7: [],
            8: [],
            9: [],
            10: [
                {
                    "ecid": 0x03,
                    "timestamp": "016bb03043ed",
                    "entry_hash": "1503d1d8b8d8036ad7cb270321996c0b1f050b4ebaea79ab48d007071cf370f2",
                    "ec_spent": 1,
                    "ec_public_key": "d4f9336bb919ee384e2f3adfc5b9f54d55c6385f99012a1051c0564184b671c7",
                    "signature": "d6437eadcedbb248b4015510ef019b5e5908de606a4c1da1627eafd48494685b5b4b390ea05f0f4f695c"
                    "c16598d5bbc8066080b1b4fdf5e3c783ae6159e77a09",
                },
                {
                    "ecid": 0x03,
                    "timestamp": "016bb03053b3",
                    "entry_hash": "170b3dc2def10bda963be05699ecd6ac8f4692573f4a8dd36b4a17392db70ff7",
                    "ec_spent": 1,
                    "ec_public_key": "166041975f981c678cda28aedb3cc5a3713668ace7f2c8b2fa4c04dbbf903566",
                    "signature": "8f8ace3b96a170094e373b7e7e39753e605b7795f3a58e586f032a5497cb838b36fbc5a3ffd07780c9e08"
                    "a35847d0d27e8694d4a307d79d117dc8d8f798b8304",
                },
                {
                    "ecid": 0x03,
                    "timestamp": "016bb03053b2",
                    "entry_hash": "b2491a8b8b8bb8395fc20f9abd6779e90aaa22a38c0508c685e944082f779176",
                    "ec_spent": 1,
                    "ec_public_key": "166041975f981c678cda28aedb3cc5a3713668ace7f2c8b2fa4c04dbbf903566",
                    "signature": "0e537d2b9029175b48defc5c781490ebaafdfb09c32be7aa3b360dde9b8ccee143e92c340855db08876ca"
                    "03dedcc2bf8cdfbb3bc6d3e68fe2619134a9f052207",
                },
                {
                    "ecid": 0x03,
                    "timestamp": "016bb03053aa",
                    "entry_hash": "7046dad9d0da9ffb27f9634e0665280f7f46bfe1f8e3a194f168718cbdd28e26",
                    "ec_spent": 1,
                    "ec_public_key": "166041975f981c678cda28aedb3cc5a3713668ace7f2c8b2fa4c04dbbf903566",
                    "signature": "a645c3f207d119313ad30bd5a4da49cec5bfed5a4037339f85befed14abb0cb30f0f505a1ab62ca8d894b"
                    "9f50cb3bea1be59afdbdf3ca65ce5cee78a2e99ac02",
                },
                {
                    "ecid": 0x03,
                    "timestamp": "016bb03053b1",
                    "entry_hash": "23c29da73f7de3ee42a111fab451c376f3cadb7e12923fa05bc01a2150ff349d",
                    "ec_spent": 1,
                    "ec_public_key": "166041975f981c678cda28aedb3cc5a3713668ace7f2c8b2fa4c04dbbf903566",
                    "signature": "4fb61b2d9b88b99835203933bb60c55f1f1d317ea8368a32cd7193f00aa2ac685d43913583a5606471996"
                    "0af3695f9b638229ddae3f8e8bcadbbeb20d0da1303",
                },
                {
                    "ecid": 0x03,
                    "timestamp": "016bb03053b2",
                    "entry_hash": "5dd03aea8dcb5763a43f8e0fe6fd16c09d4f573d2b2f1df1e5fff8be372259bb",
                    "ec_spent": 1,
                    "ec_public_key": "166041975f981c678cda28aedb3cc5a3713668ace7f2c8b2fa4c04dbbf903566",
                    "signature": "2639f55f2cf3f496ae82a2c630607dc80975406841155b8c4623d425ec7fd7d67f70a8292c581ee23115b"
                    "c5508562fb38e3625ea12b7567c17d5c94ba722ae0a",
                },
                {
                    "ecid": 0x03,
                    "timestamp": "016bb03053b7",
                    "entry_hash": "a181dd737eedc079eaf16181f6468273210036db00669b405db6958aa711cbf2",
                    "ec_spent": 1,
                    "ec_public_key": "166041975f981c678cda28aedb3cc5a3713668ace7f2c8b2fa4c04dbbf903566",
                    "signature": "b77ddc8a5c97f95dd2806a0d52fe0bc0690ae4b54bade414dcd773d74c7c2206a06fb9b2c5a9fd1538930"
                    "ea7efb9c3ff1e9e38f504ebb816c5c3e5f963fa6a0e",
                },
                {
                    "ecid": 0x03,
                    "timestamp": "016bb03053b4",
                    "entry_hash": "64a2d4bfa2b1c7e1093b9ae88ac8efb305f50798cfa8c07bf3699cab0aef3983",
                    "ec_spent": 1,
                    "ec_public_key": "166041975f981c678cda28aedb3cc5a3713668ace7f2c8b2fa4c04dbbf903566",
                    "signature": "48a7527beef5007ad0d677707eb943b4576797eeb6bc61abaaccbafb6a09c0914795dec52b5b4aa0ec6ce"
                    "1371ef0d113108d6a7f699728047bcb40280398580a",
                },
                {
                    "ecid": 0x03,
                    "timestamp": "016bb03053b5",
                    "entry_hash": "dc9e6f420e3b7e7f08e7d144cfe03cbc40f35abd27821a4769bccfa054e44b00",
                    "ec_spent": 1,
                    "ec_public_key": "166041975f981c678cda28aedb3cc5a3713668ace7f2c8b2fa4c04dbbf903566",
                    "signature": "eb968d5df2c5b83688bf03e4630bfa34b26dc099490047df1fdc90a8d5b3b9c08975db451aee4bef7148a"
                    "08bfd06fe353ec3c04cd2e0b2d21d2256caf750d607",
                },
                {
                    "ecid": 0x03,
                    "timestamp": "016bb03053ac",
                    "entry_hash": "20a51dae748935ca3f52ee7f892121290c12fa5fb71815271a9dc35947dc4cd8",
                    "ec_spent": 1,
                    "ec_public_key": "166041975f981c678cda28aedb3cc5a3713668ace7f2c8b2fa4c04dbbf903566",
                    "signature": "1666ccf3b5fa35fabfaaa8e901a2b29b6d99fe6001704564815fbf22c1b66731fe96ff94dc3a5a2f818c7"
                    "ac6020e8bbcacf1eaba566adc56ea5f5b3b4880c301",
                },
                {
                    "ecid": 0x03,
                    "timestamp": "016bb03053b5",
                    "entry_hash": "2159e8322a02a299812ca3170eef0c6ca90ef847bc69d4e5a66357735fb18993",
                    "ec_spent": 1,
                    "ec_public_key": "166041975f981c678cda28aedb3cc5a3713668ace7f2c8b2fa4c04dbbf903566",
                    "signature": "db280a4c8a53c02d629d146364e88d932622b3373cd7287eb3c2a920bda0c338507d7fc724843673021f7"
                    "653dd3c77197660822d4f70a736b8908249b8d6d20d",
                },
                {
                    "ecid": 0x03,
                    "timestamp": "016bb03053b4",
                    "entry_hash": "b088d1744550627b82b3a9159c6acb0e3676cdb21d70cba5144aac1c6ce1a231",
                    "ec_spent": 1,
                    "ec_public_key": "166041975f981c678cda28aedb3cc5a3713668ace7f2c8b2fa4c04dbbf903566",
                    "signature": "1abe2bcf93ed27ec2f9d7a0b9ef2b573c257a6d317c10360ba13712086ff8d2751b8d687ef75be994d7ba"
                    "effe084c30bab2c09e4ed1c679d661d81b7e0049c04",
                },
                {
                    "ecid": 0x03,
                    "timestamp": "016bb03053b6",
                    "entry_hash": "b056456d9176e6c80a67a89e471a75c164bf19bdf0e0550af4e66943fad8e6c8",
                    "ec_spent": 1,
                    "ec_public_key": "166041975f981c678cda28aedb3cc5a3713668ace7f2c8b2fa4c04dbbf903566",
                    "signature": "49025f14c80d0d1e8b15b14e8e81bb3d0e07fb365c73142a9cc92df62a2a4d9fee595d4736c2a4b1c4bfc"
                    "3057612565f2d94e39844439e19e62e15c8f3247609",
                },
                {
                    "ecid": 0x03,
                    "timestamp": "016bb03053b6",
                    "entry_hash": "563030a164e795050947415f0f4970b076ca74ecf491aecf1e8e714481ccd7d8",
                    "ec_spent": 1,
                    "ec_public_key": "166041975f981c678cda28aedb3cc5a3713668ace7f2c8b2fa4c04dbbf903566",
                    "signature": "0d92ee04be6c9c6a0e75acc0d95d24655b14ede5763421fd2f15802ccd3dc6f80ecdbef58474875c35abc"
                    "babee7cec11448733a3caf7c5e32ae9b7cf4a06e30b",
                },
                {
                    "ecid": 0x03,
                    "timestamp": "016bb0308fcf",
                    "entry_hash": "0a5bd6faacca17d36b47663b9764429405acaec36be26aae2cb9bd44f76a14eb",
                    "ec_spent": 1,
                    "ec_public_key": "d87869bc85e802bed893ac48ad07bbee8aaf625035af3fcd145c55273013431a",
                    "signature": "5dd2299497247d1850711fcf98a07709b32d0a1251fea5d0b63c52545a8c49bc5c3eeae014bdafbb0044e"
                    "25a1b5ab02496342a4b7aa8f8089cd740b919806703",
                },
                {
                    "ecid": 0x03,
                    "timestamp": "016bb03093b9",
                    "entry_hash": "eba1585feaba30a4de4a1766aeb537d53ca2a1a6fd33c0ca0e606d85d7de9a6e",
                    "ec_spent": 1,
                    "ec_public_key": "d87869bc85e802bed893ac48ad07bbee8aaf625035af3fcd145c55273013431a",
                    "signature": "4fa3bd8ff5e498e3809c40d1a08e35abf04f2b5a240a0c782793ed1515ae4de8c9093f4bfd6c79644850b"
                    "7f2132127a435e676baef785616928e3317ce15d206",
                },
            ],
        }

        assert block.header.body_hash.hex() == expected_body_hash
        assert block.header.prev_header_hash.hex() == expected_prev_header_hash
        assert block.header.prev_full_hash.hex() == expected_prev_full_hash
        assert block.header.height == expected_height

        for minute, objects in block.objects.items():
            for i, o in enumerate(objects):
                expected_object = expected_objects[minute][i]
                if isinstance(object, int):
                    assert 0x00 == expected_object.get("ecid")
                    # TODO: have a test case that checks server index ECID
                elif isinstance(o, ChainCommit):
                    assert ChainCommit.ECID == expected_object.get("ecid")
                    assert o.timestamp.hex() == expected_object.get("timestamp")
                    assert o.chain_id_hash.hex() == expected_object.get("chain_id_hash")
                    assert o.commit_weld.hex() == expected_object.get("commit_weld")
                    assert o.entry_hash.hex() == expected_object.get("entry_hash")
                    assert o.ec_spent == expected_object.get("ec_spent")
                    assert o.ec_public_key.hex() == expected_object.get("ec_public_key")
                    assert o.signature.hex() == expected_object.get("signature")
                elif isinstance(o, EntryCommit):
                    assert EntryCommit.ECID == expected_object.get("ecid")
                    assert o.timestamp.hex() == expected_object.get("timestamp")
                    assert o.entry_hash.hex() == expected_object.get("entry_hash")
                    assert o.ec_spent == expected_object.get("ec_spent")
                    assert o.ec_public_key.hex() == expected_object.get("ec_public_key")
                    assert o.signature.hex() == expected_object.get("signature")
                elif isinstance(o, BalanceIncrease):
                    assert BalanceIncrease.ECID == expected_object.get("ecid")
                    # TODO: have a test case that checks balance increase ECID

    def test_marshal(self):
        block = EntryCreditBlock.unmarshal(
            bytes.fromhex(TestEntryCreditBlock.test_data)
        )
        assert block.marshal().hex() == TestEntryCreditBlock.test_data

    def test_header_hash(self):
        expected_header_hash = (
            "95dcfe56875b826336c09059d1259401082042cdc99e9b7f41b2b6deadb5e26b"
        )
        block = EntryCreditBlock.unmarshal(
            bytes.fromhex(TestEntryCreditBlock.test_data)
        )
        assert block.header_hash.hex() == expected_header_hash, "{} != {}".format(
            block.lookup_hash.hex(), expected_header_hash
        )
