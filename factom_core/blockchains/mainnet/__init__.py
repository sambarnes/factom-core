import factom_core.blocks as blocks
from factom_core.blockchains import Blockchain
from factom_core.blockchains.mainnet.constants import MAINNET_NETWORK_ID
from factom_core.blockchains.mainnet.genesis import genesis_factoid_block_bytes


class MainnetBlockchain(Blockchain):
    network_id: bytes = MAINNET_NETWORK_ID

    def load_genesis_block(self) -> blocks.DirectoryBlock:
        body = blocks.AdminBlockBody()
        header = body.construct_header(back_reference_hash=bytes(32), height=0)
        admin_block = blocks.AdminBlock(header, body)

        # Add M1 server index number
        body = blocks.EntryCreditBlockBody(
            objects={
                1: [0],
                2: [],
                3: [],
                4: [],
                5: [],
                6: [],
                7: [],
                8: [],
                9: [],
                10: [],
            }
        )
        header = body.construct_header(
            prev_header_hash=bytes(32), prev_full_hash=bytes(32), height=0
        )
        entry_credit_block = blocks.EntryCreditBlock(header, body)

        factoid_block = blocks.FactoidBlock.unmarshal(genesis_factoid_block_bytes)

        directory_block_body = blocks.DirectoryBlockBody(
            admin_block_lookup_hash=admin_block.lookup_hash,
            entry_credit_block_header_hash=entry_credit_block.header_hash,
            factoid_block_keymr=factoid_block.keymr,
        )
        directory_block_header = directory_block_body.construct_header(
            network_id=self.network_id,
            prev_keymr=bytes(32),
            prev_full_hash=bytes(32),
            timestamp=24018960,
            height=0,
        )
        directory_block = blocks.DirectoryBlock(
            header=directory_block_header, body=directory_block_body
        )

        # Persist the blocks as new chain heads
        self.db.put_directory_block_head(directory_block)
        self.db.put_admin_block_head(admin_block)
        self.db.put_entry_credit_block_head(entry_credit_block)
        self.db.put_factoid_block_head(factoid_block)

        return directory_block
