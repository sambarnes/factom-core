import datetime
from dataclasses import dataclass, field
from typing import Dict, Union

import factom_core.block_elements as block_elements
import factom_core.blocks as blocks


@dataclass
class PendingBlock:

    admin_block: blocks.AdminBlockBody = field(
        init=False, default=blocks.AdminBlockBody()
    )
    factoid_block: blocks.FactoidBlockBody = field(
        init=False, default=blocks.FactoidBlockBody()
    )
    entry_credit_block: blocks.EntryCreditBlockBody = field(
        init=False, default=blocks.EntryCreditBlockBody()
    )
    entry_blocks: Dict[bytes, blocks.EntryBlockBody] = field(
        init=False, default_factory=dict
    )

    previous: blocks.DirectoryBlock = None
    current_minute: int = field(init=False, default=0)
    height: int = field(init=False, default=0)
    timestamp: int = int(datetime.datetime.utcnow().timestamp())

    def __post_init__(self):
        if self.previous is None:
            raise ValueError(
                "PendingBlock must be instantiated with a previous directory block"
            )

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
