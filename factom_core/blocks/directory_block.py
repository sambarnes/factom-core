import hashlib
import struct
from dataclasses import dataclass, field

import factom_core
from factom_core.utils import merkle


@dataclass
class DirectoryBlockHeader:
    LENGTH = 113

    CHAIN_ID = bytes.fromhex(
        "000000000000000000000000000000000000000000000000000000000000000d"
    )

    network_id: bytes
    body_mr: bytes
    prev_keymr: bytes
    prev_full_hash: bytes
    timestamp: int  # Note: timestamp in minutes, multiply by 60
    height: int
    block_count: int

    def __post_init__(self):
        # TODO: value assertions
        pass

    def marshal(self):
        buf = bytearray()
        buf.append(0x00)
        buf.extend(self.network_id)
        buf.extend(self.body_mr)
        buf.extend(self.prev_keymr)
        buf.extend(self.prev_full_hash)
        buf.extend(struct.pack(">I", self.timestamp))
        buf.extend(struct.pack(">I", self.height))
        buf.extend(struct.pack(">I", self.block_count))
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        if len(raw) != DirectoryBlockHeader.LENGTH:
            raise ValueError(
                "`raw` must be exactly {} bytes long".format(
                    DirectoryBlockHeader.LENGTH
                )
            )
        data = raw[1:]  # skip single byte version
        network_id, data = data[:4], data[4:]
        body_mr, data = data[:32], data[32:]
        prev_keymr, data = data[:32], data[32:]
        prev_full_hash, data = data[:32], data[32:]
        timestamp, data = struct.unpack(">I", data[:4])[0], data[4:]
        height, data = struct.unpack(">I", data[:4])[0], data[4:]
        block_count, data = struct.unpack(">I", data[:4])[0], data[4:]
        return DirectoryBlockHeader(
            network_id=network_id,
            body_mr=body_mr,
            prev_keymr=prev_keymr,
            prev_full_hash=prev_full_hash,
            timestamp=timestamp,
            height=height,
            block_count=block_count,
        )


@dataclass
class DirectoryBlockBody:

    admin_block_lookup_hash: bytes
    entry_credit_block_header_hash: bytes
    factoid_block_keymr: bytes
    entry_blocks: list = field(default_factory=list)

    _cached_mr: bytes = None

    def __post_init__(self):
        # TODO: value assertions
        pass

    @property
    def merkle_root(self):
        if self._cached_mr is not None:
            return self._cached_mr

        body_elements = [
            factom_core.blocks.AdminBlockHeader.CHAIN_ID,
            self.admin_block_lookup_hash,
            factom_core.blocks.EntryCreditBlockHeader.CHAIN_ID,
            self.entry_credit_block_header_hash,
            factom_core.blocks.FactoidBlockHeader.CHAIN_ID,
            self.factoid_block_keymr,
        ]
        for e_block in self.entry_blocks:
            body_elements.append(e_block.get("chain_id"))
            body_elements.append(e_block.get("keymr"))
        self._cached_mr = merkle.get_merkle_root(body_elements)
        return self._cached_mr

    def marshal(self):
        buf = bytearray()
        buf.extend(factom_core.blocks.AdminBlockHeader.CHAIN_ID)
        buf.extend(self.admin_block_lookup_hash)
        buf.extend(factom_core.blocks.EntryCreditBlockHeader.CHAIN_ID)
        buf.extend(self.entry_credit_block_header_hash)
        buf.extend(factom_core.blocks.FactoidBlockHeader.CHAIN_ID)
        buf.extend(self.factoid_block_keymr)
        for e_block in self.entry_blocks:
            buf.extend(e_block.get("chain_id"))
            buf.extend(e_block.get("keymr"))
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes, block_count: int):
        body, data = cls.unmarshal_with_remainder(raw, block_count)
        assert len(data) == 0, "Extra bytes remaining!"
        return body

    @classmethod
    def unmarshal_with_remainder(cls, raw: bytes, block_count: int):
        data = raw
        admin_block_chain_id, data = data[:32], data[32:]
        assert admin_block_chain_id == factom_core.blocks.AdminBlockHeader.CHAIN_ID
        admin_block_lookup_hash, data = data[:32], data[32:]
        ec_block_chain_id, data = data[:32], data[32:]
        assert ec_block_chain_id == factom_core.blocks.EntryCreditBlockHeader.CHAIN_ID
        entry_credit_block_header_hash, data = data[:32], data[32:]
        factoid_block_chain_id, data = data[:32], data[32:]
        assert factoid_block_chain_id == factom_core.blocks.FactoidBlockHeader.CHAIN_ID
        factoid_block_keymr, data = data[:32], data[32:]
        entry_blocks = []
        for i in range(block_count - 3):
            entry_block_chain_id, data = data[:32], data[32:]
            entry_block_keymr, data = data[:32], data[32:]
            entry_blocks.append(
                {"chain_id": entry_block_chain_id, "keymr": entry_block_keymr}
            )
        return (
            DirectoryBlockBody(
                admin_block_lookup_hash=admin_block_lookup_hash,
                entry_credit_block_header_hash=entry_credit_block_header_hash,
                factoid_block_keymr=factoid_block_keymr,
                entry_blocks=entry_blocks,
            ),
            data,
        )

    def construct_header(
        self,
        network_id: bytes,
        prev_keymr: bytes,
        prev_full_hash: bytes,
        timestamp: int,
        height: int,
    ) -> DirectoryBlockHeader:
        return DirectoryBlockHeader(
            network_id=network_id,
            body_mr=self.merkle_root,
            prev_keymr=prev_keymr,
            prev_full_hash=prev_full_hash,
            timestamp=timestamp,
            height=height,
            block_count=len(self.entry_blocks) + 3,
        )


@dataclass
class DirectoryBlock:

    header: DirectoryBlockHeader
    body: DirectoryBlockBody

    _cached_keymr: bytes = None

    def __post_init__(self,):
        # TODO: assert they're all here\
        pass

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
        """Marshals the directory block according to the byte-level representation shown at
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#directory-block

        Data returned does not include contextual metadata, such as anchor information or the pointer to the
        next directory block.
        """
        buf = bytearray()
        buf.extend(self.header.marshal())
        buf.extend(self.body.marshal())
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        """Returns a new DirectoryBlock object, unmarshalling given bytes according to:
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#directory-block

        Useful for working with a single dblock out of context, pulled directly from a factomd database for instance.

        DirectoryBlock created will not include contextual metadata, such as anchor information or the pointer to the
        next directory block.
        """
        block, data = cls.unmarshal_with_remainder(raw)
        assert len(data) == 0, "Extra bytes remaining!"
        return block

    @classmethod
    def unmarshal_with_remainder(cls, raw: bytes):
        header_data, data = (
            raw[: DirectoryBlockHeader.LENGTH],
            raw[DirectoryBlockHeader.LENGTH :],
        )
        header = DirectoryBlockHeader.unmarshal(header_data)
        body, data = DirectoryBlockBody.unmarshal_with_remainder(
            data, header.block_count
        )
        return DirectoryBlock(header=header, body=body), data

    def to_dict(self):
        return {
            "keymr": self.keymr.hex(),
            "network_id": self.header.network_id.hex(),
            "body_mr": self.header.body_mr.hex(),
            "prev_keymr": self.header.prev_keymr.hex(),
            "prev_full_hash": self.header.prev_full_hash.hex(),
            "timestamp": self.header.timestamp,
            "height": self.header.height,
            "admin_block_lookup_hash": self.body.admin_block_lookup_hash.hex(),
            "entry_credit_block_header_hash": self.body.entry_credit_block_header_hash.hex(),
            "factoid_block_keymr": self.body.factoid_block_keymr.hex(),
            "entry_blocks": [
                {
                    "chain_id": entry_block.get("chain_id").hex(),
                    "keymr": entry_block.get("keymr").hex(),
                }
                for entry_block in self.body.entry_blocks
            ],
        }

    def __str__(self):
        return "{}(height={}, keymr={})".format(
            self.__class__.__name__, self.header.height, self.keymr.hex()
        )
