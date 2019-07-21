from typing import Any, List

import factom_core.blocks as blocks
from factom_core.db import FactomdLevelDB

from .pending_block import PendingBlock


class BaseBlockchain:
    """The base class for all Blockchain objects"""

    network_id: bytes = None
    vms: List[Any] = None

    data_path: str = None
    db: FactomdLevelDB = None
    current_block: PendingBlock = None

    def __init__(self, data_path: str = None) -> None:
        if not isinstance(self.network_id, bytes) or len(self.network_id) != 4:
            raise ValueError(
                "The Blockchain class must be instantiated with a `network_id` bytes object of length 4"
            )
        # if not isinstance(self.vms, list) or len(self.vms) == 0:
        #     raise ValueError(
        #         "The Blockchain class must be instantiated with a `vms` list of length > 1"
        #     )
        self.data_path = data_path
        self.db = FactomdLevelDB(path=data_path, create_if_missing=True)

    def load_genesis_block(self) -> blocks.DirectoryBlock:
        raise NotImplementedError("Blockchain classes must implement this method")

    def vm_for_hash(self, h: bytes) -> int:
        raise NotImplementedError("Blockchain classes must implement this method")

    def seal_minute(self) -> None:
        raise NotImplementedError("Blockchain classes must implement this method")

    def rotate_vms(self) -> None:
        raise NotImplementedError("Blockchain classes must implement this method")

    def seal_block(self) -> None:
        raise NotImplementedError("Blockchain classes must implement this method")


class Blockchain(BaseBlockchain):
    """
    A Blockchain is a combination of VM classes. Each VM is associated
    with a range of chains. The Blockchain class acts as a wrapper around these other
    VM classes, delegating operations to the appropriate VM depending on the
    current block / minute number.
    """

    def __init__(self, data_path: str = None):
        super().__init__(data_path)

    def load_genesis_block(self) -> blocks.DirectoryBlock:
        pass

    def vm_for_hash(self, h: bytes) -> int:
        """
        Compute the VM index responsible for hash h

        Taken from: factomd/state/processList.go/VMindexFor(hash []byte)
        """
        if len(self.vms) == 0:
            return 0
        v = 0
        for b in h:
            v += b
        return v % len(self.vms)

    def seal_minute(self) -> None:
        """Finalize the current block minute"""
        self.rotate_vms()

        if self.current_block.current_minute == 10:
            self.seal_block()
        else:
            self.current_block.current_minute += 1

    def rotate_vms(self) -> None:
        """Rotate the responsibilities of the VM set (if necessary)"""
        # TODO: see processList.go/MakgeMap for formula per block height
        if len(self.vms) == 1:
            return
        self.vms = self.vms[1:] + self.vms[:1]

    def seal_block(self):
        """
        Bundles all added transactions, entries, and other elements into a set of finalized
        blocks with headers.
        """
        block = self.current_block
        entry_blocks: List[blocks.EntryBlock] = []
        for chain_id, block_body in block.entry_blocks.items():
            prev = self.db.get_entry_block_head(chain_id)
            header = block_body.construct_header(
                chain_id=chain_id,
                prev_keymr=prev.keymr if prev is not None else bytes(32),
                prev_full_hash=prev.full_hash if prev is not None else bytes(32),
                sequence=prev.header.sequence + 1 if prev is not None else 0,
                height=block.height,
            )
            entry_blocks.append(blocks.EntryBlock(header, block_body))

        prev = self.db.get_entry_credit_block(height=block.height - 1)
        header = block.entry_credit_block.construct_header(
            prev_header_hash=prev.header_hash,
            prev_full_hash=prev.full_hash,
            height=block.height,
        )
        entry_credit_block = blocks.EntryCreditBlock(header, block.entry_credit_block)

        prev = self.db.get_factoid_block(height=block.height - 1)
        header = block.factoid_block.construct_header(
            prev_keymr=block.previous.body.factoid_block_keymr,
            prev_ledger_keymr=prev.ledger_keymr,
            ec_exchange_rate=1000,  # TODO
            height=block.height,
        )
        factoid_block = blocks.FactoidBlock(header, block.factoid_block)

        prev = self.db.get_admin_block(height=block.height - 1)
        header = block.admin_block.construct_header(
            back_reference_hash=prev.back_reference_hash, height=block.height
        )
        admin_block = blocks.AdminBlock(header, block.admin_block)

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
            network_id=self.network_id,
            prev_keymr=block.previous.keymr,
            prev_full_hash=block.previous.full_hash,
            timestamp=block.timestamp,
            height=block.height,
        )
        directory_block = blocks.DirectoryBlock(header, directory_block_body)

        # Persist the blocks as new chain heads
        self.db.put_directory_block_head(directory_block)
        self.db.put_admin_block_head(admin_block)
        self.db.put_entry_credit_block_head(entry_credit_block)
        self.db.put_factoid_block_head(factoid_block)
        for entry_block in entry_blocks:
            self.db.put_entry_block_head(entry_block)
