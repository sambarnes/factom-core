import hashlib
import struct
from dataclasses import dataclass, field
from typing import Dict, List, Union

from factom_core.block_elements.balance_increase import BalanceIncrease
from factom_core.block_elements.chain_commit import ChainCommit
from factom_core.block_elements.entry_commit import EntryCommit
from factom_core.utils import varint
from .directory_block import DirectoryBlock


ECIDTypes = Union[ChainCommit, EntryCommit, int]


@dataclass
class EntryCreditBlockHeader:

    CHAIN_ID = bytes.fromhex(
        "000000000000000000000000000000000000000000000000000000000000000c"
    )

    body_hash: bytes
    prev_header_hash: bytes
    prev_full_hash: bytes
    height: int
    expansion_area: bytes
    object_count: int
    body_size: int

    def __post_init__(self):
        # TODO: value assertions
        pass

    def marshal(self) -> bytes:
        buf = bytearray()
        buf.extend(EntryCreditBlockHeader.CHAIN_ID)
        buf.extend(self.body_hash)
        buf.extend(self.prev_header_hash)
        buf.extend(self.prev_full_hash)
        buf.extend(struct.pack(">I", self.height))
        buf.extend(varint.encode(len(self.expansion_area)))
        buf.extend(self.expansion_area)
        buf.extend(struct.pack(">Q", self.object_count))
        buf.extend(struct.pack(">Q", self.body_size))
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        h, data = EntryCreditBlockHeader.unmarshal_with_remainder(raw)
        assert len(data) == 0, "Extra bytes remaining!"
        return h

    @classmethod
    def unmarshal_with_remainder(cls, raw: bytes):
        chain_id, data = raw[:32], raw[32:]
        assert chain_id == EntryCreditBlockHeader.CHAIN_ID
        body_hash, data = data[:32], data[32:]
        prev_header_hash, data = data[:32], data[32:]
        prev_full_hash, data = data[:32], data[32:]
        height, data = struct.unpack(">I", data[:4])[0], data[4:]

        header_expansion_size, data = varint.decode(data)
        header_expansion_area, data = (
            data[:header_expansion_size],
            data[header_expansion_size:],
        )

        object_count, data = struct.unpack(">Q", data[:8])[0], data[8:]
        body_size, data = struct.unpack(">Q", data[:8])[0], data[8:]

        return (
            EntryCreditBlockHeader(
                body_hash=body_hash,
                prev_header_hash=prev_header_hash,
                prev_full_hash=prev_full_hash,
                height=height,
                expansion_area=header_expansion_area,
                object_count=object_count,
                body_size=body_size,
            ),
            data,
        )


@dataclass
class EntryCreditBlockBody:

    objects: Dict[int, List[ECIDTypes]] = field(default_factory=dict)

    def __post_init__(self):
        # TODO: value assertions
        pass

    def marshal(self):
        buf = bytearray()
        for minute, objects in self.objects.items():
            for o in objects:
                if isinstance(o, int):
                    buf.append(0x00)
                    buf.append(o)
                elif isinstance(o, ChainCommit):
                    buf.append(ChainCommit.ECID)
                    buf.extend(o.marshal())
                elif isinstance(o, EntryCommit):
                    buf.append(EntryCommit.ECID)
                    buf.extend(o.marshal())
                elif isinstance(o, BalanceIncrease):
                    buf.append(BalanceIncrease.ECID)
                    buf.extend(o.marshal())
                else:
                    raise ValueError("Invalid ECID type!")
            buf.append(0x01)
            buf.append(minute)
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes, object_count: int):
        body, data = cls.unmarshal_with_remainder(raw, object_count)
        assert len(data) == 0, "Extra bytes remaining!"
        return body

    @classmethod
    def unmarshal_with_remainder(cls, raw: bytes, object_count: int):
        data = raw
        objects = {}  # map of minute --> objects array
        current_minute_objects = []
        for i in range(object_count):
            ecid, data = data[0], data[1:]
            if ecid == 0x00:
                server_index, data = data[0], data[1:]
                current_minute_objects.append(server_index)
            elif ecid == 0x01:
                minute, data = data[0], data[1:]
                objects[minute] = current_minute_objects
                current_minute_objects = []
            elif ecid == ChainCommit.ECID:
                chain_commit, data = (
                    data[: ChainCommit.BITLENGTH],
                    data[ChainCommit.BITLENGTH :],
                )
                chain_commit = ChainCommit.unmarshal(chain_commit)
                current_minute_objects.append(chain_commit)
            elif ecid == EntryCommit.ECID:
                entry_commit, data = (
                    data[: EntryCommit.BITLENGTH],
                    data[EntryCommit.BITLENGTH :],
                )
                entry_commit = EntryCommit.unmarshal(entry_commit)
                current_minute_objects.append(entry_commit)
            elif ecid == BalanceIncrease.ECID:
                balance_increase, data = BalanceIncrease.unmarshal_with_remainder(data)
                current_minute_objects.append(balance_increase)
            else:
                raise ValueError

        return EntryCreditBlockBody(objects=objects), data

    def construct_header(
        self, prev_header_hash: bytes, prev_full_hash: bytes, height: int
    ) -> EntryCreditBlockHeader:
        object_count = 0
        for object_list in self.objects.values():
            object_count += len(object_list) + 1
        marshalled_body = self.marshal()
        return EntryCreditBlockHeader(
            body_hash=hashlib.sha256(marshalled_body).digest(),
            prev_header_hash=prev_header_hash,
            prev_full_hash=prev_full_hash,
            height=height,
            expansion_area=b"",
            object_count=object_count,
            body_size=len(marshalled_body),
        )


@dataclass
class EntryCreditBlock:

    header: EntryCreditBlockHeader
    body: EntryCreditBlockBody

    _cached_header_hash: bytes = None

    def __post_init__(self):
        # TODO: value assertions
        pass

    @property
    def header_hash(self):
        if self._cached_header_hash is not None:
            return self._cached_header_hash
        self._cached_header_hash = hashlib.sha256(self.header.marshal()).digest()
        return self._cached_header_hash

    @property
    def full_hash(self):
        return hashlib.sha256(self.marshal()).digest()

    def marshal(self):
        """Marshals the directory block according to the byte-level representation shown at
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#entry-credit-block

        Data returned does not include contextual metadata, such as timestamp or the pointer to the
        next entry-credit block.
        """
        buf = bytearray()
        buf.extend(self.header.marshal())
        buf.extend(self.body.marshal())
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        """Returns a new EntryCreditBlock object, unmarshalling given bytes according to:
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#entry-credit-block

        Useful for working with a single ecblock out of context, pulled directly from a factomd database for instance.

        EntryCreditBlock created will not include contextual metadata, such as timestamp or the pointer to the
        next entry-credit block.
        """
        block, data = cls.unmarshal_with_remainder(raw)
        assert len(data) == 0, "Extra bytes remaining!"
        return block

    @classmethod
    def unmarshal_with_remainder(cls, raw: bytes):
        header, data = EntryCreditBlockHeader.unmarshal_with_remainder(raw)
        body, data = EntryCreditBlockBody.unmarshal_with_remainder(
            data, header.object_count
        )
        return EntryCreditBlock(header=header, body=body), data

    def add_context(self, directory_block: DirectoryBlock):
        pass

    def to_dict(self):
        return {
            "header_hash": self.header_hash.hex(),
            "body_hash": self.header.body_hash.hex(),
            "prev_header_hash": self.header.prev_header_hash.hex(),
            "prev_full_hash": self.header.prev_full_hash.hex(),
            "height": self.header.height,
            "expansion_area": self.header.expansion_area.hex(),
            "object_count": self.header.object_count,
            "body_size": self.header.body_size,
            "objects": {
                minute: [o if type(o) is int else o.to_dict() for o in objects]
                for minute, objects in self.body.objects.items()
            },
        }

    def __str__(self):
        return "{}(height={})".format(self.__class__.__name__, self.header.height)
