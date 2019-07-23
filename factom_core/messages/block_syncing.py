import struct
from dataclasses import dataclass, field
from typing import List

import factom_core.blockchains.mainnet
import factom_core.primitives as primitives
from factom_core.blockchains import Blockchain
from factom_core.blocks import (
    DirectoryBlock,
    AdminBlock,
    FactoidBlock,
    EntryCreditBlock,
    EntryBlock,
)
from factom_core.block_elements import Entry
from factom_core.messages import Message


@dataclass
class DirectoryBlockState(Message):
    """
    A message to communicate a Directory Block State
    """

    TYPE = 20

    timestamp: bytes
    directory_block: DirectoryBlock
    admin_block: AdminBlock
    factoid_block: FactoidBlock
    entry_credit_block: EntryCreditBlock
    entry_blocks: List[EntryBlock]
    entries: List[Entry]
    signatures: primitives.FullSignatureList

    # Not marshalled
    is_in_database: bool = field(init=False, default=False)

    def __post_init__(self):
        # TODO: type/value assertions
        self.is_p2p = True
        super().__post_init__()

    def marshal(self) -> bytes:
        """
        Marshal the message into the following representation:
        - first byte is the message type (always 20)
        - next bytes are the marshalled Directory Block
        - next bytes are the marshalled Admin Block
        - next bytes are the marshalled Factoid Block
        - next bytes are the marshalled Entry Credit Block
        - next 4 bytes are the number of Entry Blocks following (NOTE: always 0 now)
        - next bytes are the aforementioned marshalled Entry Blocks
        - next 4 bytes are the number of Entries following (NOTE: always 0 now)
        - next bytes are all of the Entries, marshalled as:
            - 4 bytes size of the Entry
            - marshalled Entry itself
        - next bytes are the number of signatures
        - next bytes are all of the signatures marshalled as:
            - 64 bytes signature
            - 32 byte public key

        :return: byte representation of the message
        """
        buf = bytearray()
        buf.append(self.TYPE)
        buf.extend(self.timestamp)
        buf.extend(self.directory_block.marshal())
        buf.extend(self.admin_block.marshal())
        buf.extend(self.factoid_block.marshal())
        buf.extend(self.entry_credit_block.marshal())
        buf.extend(struct.pack(">I", len(self.entry_blocks)))
        for entry_block in self.entry_blocks:
            buf.extend(entry_block.marshal())
        buf.extend(struct.pack(">I", len(self.entries)))
        for entry in self.entries:
            entry_data = entry.marshal()
            buf.extend(struct.pack(">I", len(entry_data)))
            buf.extend(entry_data)
        buf.extend(self.signatures.marshal())
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))

        timestamp, data = data[:6], data[6:]
        directory_block, data = DirectoryBlock.unmarshal_with_remainder(data)
        admin_block, data = AdminBlock.unmarshal_with_remainder(data)
        factoid_block, data = FactoidBlock.unmarshal_with_remainder(data)
        entry_credit_block, data = EntryCreditBlock.unmarshal_with_remainder(data)

        entry_block_count, data = struct.unpack(">I", data[:4])[0], data[4:]
        entry_blocks = []
        for i in range(entry_block_count):
            entry_block, data = EntryBlock.unmarshal_with_remainder(data)
            entry_blocks.append(entry_block)

        entry_count, data = struct.unpack(">I", data[:4])[0], data[4:]
        entries = []
        for i in range(entry_count):
            entry_size, data = struct.unpack(">I", data[:4])[0], data[4:]
            entry, data = Entry.unmarshal(data[:entry_size]), data[entry_size:]
            entries.append(entry)

        signatures = primitives.FullSignatureList.unmarshal(data)

        return DirectoryBlockState(
            timestamp=timestamp,
            directory_block=directory_block,
            admin_block=admin_block,
            factoid_block=factoid_block,
            entry_credit_block=entry_credit_block,
            entry_blocks=entry_blocks,
            entries=entries,
            signatures=signatures,
        )

    def to_dict(self):
        return {
            "timestamp": self.timestamp.hex(),
            "directory_block": self.directory_block.to_dict(),
            "admin_block": self.admin_block.to_dict(),
            "factoid_block": self.factoid_block.to_dict(),
            "entry_credit_block": self.entry_credit_block.to_dict(),
            "entry_blocks": [v.to_dict() for v in self.entry_blocks],
            "entries": [v.to_dict() for v in self.entries],
            "signatures": [sig.to_dict() for sig in self.signatures],
        }

    def is_sane(self, state: Blockchain):
        if None in {
            self.directory_block,
            self.admin_block,
            self.factoid_block,
            self.entry_credit_block,
        }:
            return False

        if self.is_in_database:
            return True

        height = self.directory_block.header.height
        if height == 0:
            return True  # Always accept genesis blocks
        # TODO: if height < state.height_at_boot: return False
        # TODO: if height < state.highest_saved_block: return False

        if state.network_id != self.directory_block.header.network_id:
            return False

        if type(state) is factom_core.blockchains.mainnet.MainnetBlockchain:
            checkpoints = factom_core.blockchains.mainnet.constants.CHECKPOINTS
            keymr = checkpoints.get(height)
            if keymr is not None:
                if self.directory_block.keymr.hex() != keymr:
                    return False
        return True

    def is_valid(self):
        # TODO: dbstate.validate_signatures()

        # Hash checks for all blocks in Directory Block Body
        body = self.directory_block.body
        if body.admin_block_lookup_hash != self.admin_block.lookup_hash:
            return False
        if body.factoid_block_keymr != self.factoid_block.keymr:
            return False
        if body.entry_credit_block_header_hash != self.entry_credit_block.header_hash:
            return False

        # Make dict of stuff claimed to be in directory block
        entry_block_claims = set()
        entry_claims = set()
        for entry_block in body.entry_blocks:
            entry_block_claims.add(entry_block.keymr)

        # Check claims against actual included entry blocks
        for entry_block in self.entry_blocks:
            if entry_block.keymr not in entry_block_claims:
                return False
            # Add claims from the included entry blocks
            claims = {
                entry_hash
                for hashes in entry_block.body.entry_hashes.values()
                for entry_hash in hashes
            }
            entry_claims.update(claims)

        # Check claims of entry blocks against actual included entries
        for entry in self.entries:
            if entry.entry_hash not in entry_claims:
                return False

        return True

    def leader_execute(self, state: Blockchain):
        self.follower_execute(state)

    def follower_execute(self, state: Blockchain):
        pass


@dataclass
class DirectoryBlockStateRequest(Message):
    """
    A request for missing DBState objects.
    """

    TYPE = 21

    timestamp: bytes
    block_height_start: int
    block_height_end: int

    def __post_init__(self):
        # TODO: type/value assertions
        self.is_p2p = True
        super().__post_init__()

    def marshal(self) -> bytes:
        """
        Marshal the message into the following representation:
        - first byte is the message type (always 21)
        - next 6 bytes are the timestamp
        - next 4 bytes are the block height start
        - next 4 bytes are the block height end

        :return: byte representation of the message
        """
        buf = bytearray()
        buf.append(self.TYPE)
        buf.extend(self.timestamp)
        buf.extend(struct.pack(">I", self.block_height_start))
        buf.extend(struct.pack(">I", self.block_height_end))
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))

        timestamp, data = data[:6], data[6:]
        block_height_start, data = struct.unpack(">I", data[:4])[0], data[4:]
        block_height_end, data = struct.unpack(">I", data[:4])[0], data[4:]

        return DirectoryBlockStateRequest(
            timestamp=timestamp,
            block_height_start=block_height_start,
            block_height_end=block_height_end,
        )

    def to_dict(self):
        return {
            "timestamp": self.timestamp.hex(),
            "block_height_start": self.block_height_start,
            "block_height_end": self.block_height_end,
        }

    def leader_execute(self, state: Blockchain):
        self.follower_execute(state)

    def follower_execute(self, state: Blockchain):
        pass


@dataclass()
class BlockRequest(Message):
    """
    An unimplemented message. I assume for requesting single blocks of any type.
    """

    TYPE = 14

    timestamp: bytes

    def __post_init__(self):
        # TODO: type/value assertions
        super().__post_init__()

    def marshal(self) -> bytes:
        """
        Marshal the message into the following representation:
        - first byte is the message type (always 14)
        - next 6 bytes are a timestamp

        :return: byte representation of the message
        """
        buf = bytearray()
        buf.append(self.TYPE)
        buf.extend(self.timestamp)
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))
        timestamp, data = data[:6], data[6:]
        assert len(data) == 0, "Extra bytes remaining!"
        return BlockRequest(timestamp=timestamp)

    def to_dict(self):
        return {"timestamp": self.timestamp.hex()}
