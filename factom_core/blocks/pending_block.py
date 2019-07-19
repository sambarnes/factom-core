import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Union

import factom_core.block_elements as block_elements
import factom_core.blocks as blocks


@dataclass
class PendingBlock:

    admin_block: blocks.AdminBlockBody
    factoid_block: blocks.FactoidBlockBody
    entry_credit_block: blocks.EntryCreditBlockBody
    entry_blocks: Dict[bytes, blocks.EntryBlockBody]

    previous: blocks.DirectoryBlock = None
    current_minute: int = field(init=False, default=0)
    height: int = field(init=False, default=0)
    timestamp: int = int(datetime.datetime.utcnow().timestamp())

    def __post_init__(self):
        if self.previous is not None:
            self.height = self.previous.header.height + 1

    def add_factoid_transaction(self, tx: block_elements.FactoidTransaction):
        if len(self.factoid_block.transactions.keys()) == 0:
            for i in range(1, 10):
                self.factoid_block.transactions[i] = []
        self.factoid_block.transactions[self.current_minute].append(tx)

    def add_commit(
        self, commit: Union[block_elements.ChainCommit, block_elements.EntryCommit]
    ):
        if self.current_minute not in self.entry_credit_block.objects:
            self.entry_credit_block.objects[self.current_minute] = [commit]
        else:
            self.entry_credit_block.objects[self.current_minute].append(commit)

    def add_entry(self, entry: block_elements.Entry):
        if entry.chain_id not in self.entry_blocks:
            entry_hashes = {self.current_minute: [entry.entry_hash]}
            entry_block = blocks.EntryBlockBody(entry_hashes=entry_hashes)
            self.entry_blocks[entry.chain_id] = entry_block
        elif self.current_minute not in self.entry_blocks[entry.chain_id]:
            self.entry_blocks[entry.chain_id].entry_hashes[self.current_minute] = [
                entry.entry_hash
            ]
        else:
            self.entry_blocks[entry.chain_id].entry_hashes[self.current_minute].append(
                entry.entry_hash
            )

    def seal_blocks(self):
        """
        Bundles all added transactions, entries, and other elements into a set of finalized
        blocks.

        :return:
        """
        # Make list of Entry Blocks
        entry_blocks: List[blocks.EntryBlock] = []
        for chain_id, block_body in self.entry_blocks.items():
            header = block_body.construct_header(
                chain_id=chain_id,
                prev_keymr=bytes(32),  # TODO
                prev_full_hash=bytes(32),  # TODO
                sequence=0,  # TODO
                height=self.height,
            )
            entry_blocks.append(blocks.EntryBlock(header, block_body))

        header = self.entry_credit_block.construct_header(
            prev_header_hash=bytes(32),  # TODO
            prev_full_hash=bytes(32),  # TODO
            height=self.height,
        )
        entry_credit_block = blocks.EntryCreditBlock(header, self.entry_credit_block)

        header = self.factoid_block.construct_header(
            prev_keymr=self.previous.body.factoid_block_keymr,
            prev_ledger_keymr=bytes(32),  # TODO
            ec_exchange_rate=1000,  # TODO
            height=self.height,
        )
        factoid_block = blocks.FactoidBlock(header, self.factoid_block)

        header = self.admin_block.construct_header(
            back_reference_hash=bytes(32), height=self.height  # TODO
        )
        admin_block = blocks.AdminBlock(header, self.admin_block)

        # Compile all the above blocks and the previous directory block, into a new one
        directory_block_body = blocks.DirectoryBlockBody(
            admin_block_lookup_hash=admin_block.lookup_hash,
            entry_credit_block_header_hash=entry_credit_block.header_hash,
            factoid_block_keymr=factoid_block.keymr,
            entry_blocks=[
                {"chain_id": entry_block.header.chain_id, "keymr": entry_block.keymr}
                for entry_block in entry_blocks
            ],
        )
        header = directory_block_body.construct_header(
            network_id=self.previous.header.network_id,
            prev_keymr=self.previous.keymr,
            prev_full_hash=self.previous.full_hash,
            timestamp=self.timestamp,
            height=self.height,
        )
        directory_block = blocks.DirectoryBlock(header, directory_block_body)

        return (
            directory_block,
            admin_block,
            entry_credit_block,
            factoid_block,
            entry_blocks,
        )
