from dataclasses import dataclass, field, InitVar
from typing import Any, List, Tuple

import factom_core.blocks as blocks
from factom_core.db import FactomdLevelDB


FullBlockSet = Tuple[
    blocks.DirectoryBlock,
    blocks.AdminBlock,
    blocks.EntryCreditBlock,
    blocks.FactoidBlock,
    List[blocks.EntryBlock],
]


@dataclass
class BaseBlockchain:
    """The base class for all Blockchain objects"""

    network_id: bytes = None
    vms: List[Any] = None

    data_path: InitVar[str] = None
    db: FactomdLevelDB = field(init=False, default=None)
    current_block: blocks.PendingBlock = field(init=False, default=None)

    def __post_init__(self, data_path) -> None:
        if not isinstance(self.network_id, bytes) or len(self.network_id) != 4:
            raise ValueError(
                "The Blockchain class must be instantiated with a `network_id` bytes object of length 4"
            )
        if not isinstance(self.vms, list) or len(self.network_id) == 0:
            raise ValueError(
                "The Blockchain class must be instantiated with a `vms` list of length > 1"
            )

        self.db = FactomdLevelDB(path=data_path, create_if_missing=True)

    def vm_for_hash(self, h: bytes) -> int:
        raise NotImplementedError("Blockchain classes must implement this method")

    def seal_minute(self) -> None:
        raise NotImplementedError("Blockchain classes must implement this method")

    def rotate_vms(self) -> None:
        raise NotImplementedError("Blockchain classes must implement this method")

    def seal_block(self) -> FullBlockSet:
        raise NotImplementedError("Blockchain classes must implement this method")


@dataclass
class Blockchain(BaseBlockchain):
    """
    A Blockchain is a combination of VM classes. Each VM is associated
    with a range of chains. The Blockchain class acts as a wrapper around these other
    VM classes, delegating operations to the appropriate VM depending on the
    current block / minute number.
    """

    def __post_init__(self, data_path):
        super().__post_init__(data_path)

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
        blocks.
        """
        block_set = self.current_block.finalize()
        self.db.put_full_block_set(block_set)