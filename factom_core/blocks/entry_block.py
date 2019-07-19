import struct
import hashlib
from dataclasses import dataclass
from typing import Dict, List

from factom_core.utils import merkle
from .directory_block import DirectoryBlock


@dataclass
class EntryBlockHeader:
    LENGTH = 140

    """Header section of an Entry Block, built from the body or unmarshalled from raw bytes"""

    chain_id: bytes
    body_mr: bytes
    prev_keymr: bytes
    prev_full_hash: bytes
    sequence: int
    height: int
    entry_count: int

    def marshal(self) -> bytes:
        buf = bytearray()
        buf.extend(self.chain_id)
        buf.extend(self.body_mr)
        buf.extend(self.prev_keymr)
        buf.extend(self.prev_full_hash)
        buf.extend(struct.pack(">I", self.sequence))
        buf.extend(struct.pack(">I", self.height))
        buf.extend(struct.pack(">I", self.entry_count))
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        if len(raw) != EntryBlockHeader.LENGTH:
            raise ValueError(
                "`raw` must be exactly {} bytes long".format(EntryBlockHeader.LENGTH)
            )
        chain_id, data = raw[:32], raw[32:]
        body_mr, data = data[:32], data[32:]
        prev_keymr, data = data[:32], data[32:]
        prev_full_hash, data = data[:32], data[32:]
        sequence, data = struct.unpack(">I", data[:4])[0], data[4:]
        height, data = struct.unpack(">I", data[:4])[0], data[4:]
        entry_count, data = struct.unpack(">I", data[:4])[0], data[4:]
        return EntryBlockHeader(
            chain_id=chain_id,
            body_mr=body_mr,
            prev_keymr=prev_keymr,
            prev_full_hash=prev_full_hash,
            sequence=sequence,
            height=height,
            entry_count=entry_count,
        )


@dataclass
class EntryBlockBody:

    entry_hashes: Dict[int, List[bytes]]
    _cached_mr: bytes = None

    def __post_init__(self):
        # TODO: assert they're all here
        pass

    @property
    def merkle_root(self):
        if self._cached_mr is not None:
            return self._cached_mr

        body_elements = []
        for minute, hashes in self.entry_hashes.items():
            for h in hashes:
                body_elements.append(h)
            buf = bytearray()
            buf.extend(bytes(31))
            buf.append(minute)
            body_elements.append(bytes(buf))
        self._cached_mr = merkle.get_merkle_root(body_elements)
        return self._cached_mr

    def marshal(self):
        buf = bytearray()
        for minute, hashes in self.entry_hashes.items():
            for h in hashes:
                buf.extend(h)
            buf.extend(bytes(31))
            buf.append(minute)
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes, entry_count: int):
        body, data = cls.unmarshal_with_remainder(raw, entry_count)
        assert len(data) == 0, "Extra bytes remaining!"
        return body

    @classmethod
    def unmarshal_with_remainder(cls, raw: bytes, entry_count: int):
        data = raw
        # Entry hashes are listed in order, with a minute marker following what minute those entries were in
        entry_hashes = {}
        current_minute_entries = []
        for i in range(entry_count):
            entry_hash, data = data[:32], data[32:]
            if entry_hash[:-1] == bytes(31) and entry_hash[-1] <= 10:
                entry_hashes[entry_hash[-1]] = current_minute_entries
                current_minute_entries = []
            else:
                current_minute_entries.append(entry_hash)

        return EntryBlockBody(entry_hashes=entry_hashes), data

    def construct_header(
        self,
        chain_id: bytes,
        prev_keymr: bytes,
        prev_full_hash: bytes,
        sequence: int,
        height: int,
    ) -> EntryBlockHeader:
        """
        Creates an returns an EntryBlockHeader for this body object, given the specified contextual
        parameters.
        """
        entry_count = 0
        for hashes in self.entry_hashes.values():
            entry_count += len(hashes)
        return EntryBlockHeader(
            chain_id=chain_id,
            body_mr=self.merkle_root,
            prev_keymr=prev_keymr,
            prev_full_hash=prev_full_hash,
            sequence=sequence,
            height=height,
            entry_count=entry_count,
        )


@dataclass
class EntryBlock:

    header: EntryBlockHeader
    body: EntryBlockBody

    _cached_keymr: bytes = None

    directory_block_keymr: bytes = None
    timestamp: int = None

    def __post_init__(self):
        # TODO: assert they're all here
        pass
        # Optional contextual metadata. Derived from the directory block that contains this EntryBlock
        # self.next_keymr = kwargs.get("next_keymr")

    @property
    def keymr(self):
        if self._cached_keymr is not None:
            return self._cached_keymr

        self._cached_keymr = merkle.calculate_keymr(
            self.header.marshal(), self.body.merkle_root
        )
        return self._cached_keymr

    @property
    def full_hash(self):
        return hashlib.sha256(self.marshal()).digest()

    def marshal(self):
        """Marshals the entry block according to the byte-level representation shown at
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#entry-block

        Data returned does not include contextual metadata, such as timestamp or the pointer to the next entry block.
        """
        buf = bytearray()
        buf.extend(self.header.marshal())
        buf.extend(self.body.marshal())
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        """Returns a new EntryBlock object, unmarshalling given bytes according to:
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#entry-block

        Useful for working with a single eblock out of context, pulled directly from a factomd database for instance.

        EntryBlock created will not include contextual metadata, such as timestamp or the pointer to the
        next entry block.
        """
        block, data = cls.unmarshal_with_remainder(raw)
        assert len(data) == 0, "Extra bytes remaining!"
        return block

    @classmethod
    def unmarshal_with_remainder(cls, raw: bytes):
        header_data, data = (
            raw[: EntryBlockHeader.LENGTH],
            raw[EntryBlockHeader.LENGTH :],
        )
        header = EntryBlockHeader.unmarshal(header_data)
        body, data = EntryBlockBody.unmarshal_with_remainder(data, header.entry_count)
        return EntryBlock(header=header, body=body), data

    def add_context(self, directory_block: DirectoryBlock):
        self.directory_block_keymr = directory_block.keymr
        self.timestamp = directory_block.header.timestamp

    def to_dict(self):
        return {
            # Required
            "keymr": self.keymr.hex(),
            "chain_id": self.header.chain_id.hex(),
            "prev_keymr": self.header.prev_keymr.hex(),
            "prev_full_hash": self.header.prev_full_hash.hex(),
            "sequence": self.header.sequence,
            "height": self.header.height,
            "entry_hashes": {
                minute: [h.hex() for h in hashes]
                for minute, hashes in self.body.entry_hashes.items()
            },
            # Optional contextual
            "directory_block_keymr": None
            if self.directory_block_keymr is None
            else self.directory_block_keymr.hex(),
            "timestamp": self.timestamp,
        }

    def __str__(self):
        return "{}(height={}, keymr={})".format(
            self.__class__.__name__, self.header.height, self.keymr.hex()
        )
