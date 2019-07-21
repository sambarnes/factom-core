import hashlib
import struct
from dataclasses import dataclass, field
from typing import Dict, List

from factom_core.block_elements.factoid_transaction import FactoidTransaction
from factom_core.utils import merkle, varint
from .directory_block import DirectoryBlock


@dataclass
class FactoidBlockHeader:

    CHAIN_ID = bytes.fromhex(
        "000000000000000000000000000000000000000000000000000000000000000f"
    )

    body_mr: bytes
    prev_keymr: bytes
    prev_ledger_keymr: bytes
    ec_exchange_rate: int
    height: int
    expansion_area: bytes
    tx_count: int
    body_size: int

    def __post_init__(self):
        # TODO: value assertions
        pass

    def marshal(self) -> bytes:
        buf = bytearray()
        buf.extend(FactoidBlockHeader.CHAIN_ID)
        buf.extend(self.body_mr)
        buf.extend(self.prev_keymr)
        buf.extend(self.prev_ledger_keymr)
        buf.extend(struct.pack(">Q", self.ec_exchange_rate))
        buf.extend(struct.pack(">I", self.height))
        buf.extend(varint.encode(len(self.expansion_area)))
        buf.extend(self.expansion_area)
        buf.extend(struct.pack(">I", self.tx_count))
        buf.extend(struct.pack(">I", self.body_size))
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        h, data = FactoidBlockHeader.unmarshal_with_remainder(raw)
        assert len(data) == 0, "Extra bytes remaining!"
        return h

    @classmethod
    def unmarshal_with_remainder(cls, raw: bytes):
        chain_id, data = raw[:32], raw[32:]
        assert chain_id == FactoidBlockHeader.CHAIN_ID
        body_mr, data = data[:32], data[32:]
        prev_keymr, data = data[:32], data[32:]
        prev_ledger_keymr, data = data[:32], data[32:]
        ec_exchange_rate, data = struct.unpack(">Q", data[:8])[0], data[8:]
        height, data = struct.unpack(">I", data[:4])[0], data[4:]

        header_expansion_size, data = varint.decode(data)
        header_expansion_area, data = (
            data[:header_expansion_size],
            data[header_expansion_size:],
        )

        tx_count, data = struct.unpack(">I", data[:4])[0], data[4:]
        body_size, data = struct.unpack(">I", data[:4])[0], data[4:]
        return (
            FactoidBlockHeader(
                body_mr=body_mr,
                prev_keymr=prev_keymr,
                prev_ledger_keymr=prev_ledger_keymr,
                ec_exchange_rate=ec_exchange_rate,
                height=height,
                expansion_area=header_expansion_area,
                tx_count=tx_count,
                body_size=body_size,
            ),
            data,
        )


@dataclass
class FactoidBlockBody:

    transactions: Dict[int, List[FactoidTransaction]] = field(default_factory=dict)
    _cached_mr: bytes = None

    def __post_init__(self):
        # TODO: value assertions
        pass

    @property
    def merkle_root(self):
        if self._cached_mr is not None:
            return self._cached_mr

        # For Factoid Blocks, body MR is implemented differently in that you first take a single sha256 of every element
        # in the body. And you make a Merkle tree out of the hashed body elements, rather than the elements themselves.
        body_elements = []
        for transactions in self.transactions.values():
            for tx in transactions:
                body_elements.append(tx.hash)
            minute_marker = hashlib.sha256(b"\x00").digest()
            body_elements.append(minute_marker)
        self._cached_mr = merkle.get_merkle_root(body_elements)
        return self._cached_mr

    def marshal(self):
        buf = bytearray()
        for transactions in self.transactions.values():
            for tx in transactions:
                buf.extend(tx.marshal())
            buf.append(0x00)
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes, tx_count: int):
        body, data = cls.unmarshal_with_remainder(raw, tx_count)
        assert len(data) == 0, "Extra bytes remaining!"
        return body

    @classmethod
    def unmarshal_with_remainder(cls, raw: bytes, tx_count: int):
        data = raw
        transactions = {}
        current_minute_transactions = []
        minute = 1
        tx_count_observed = 0
        while True:
            if data[0] == 0:
                data = data[1:]
                transactions[minute] = current_minute_transactions
                tx_count_observed += len(current_minute_transactions)
                if minute == 10:
                    break
                current_minute_transactions = []
                minute += 1
                continue
            tx, data = FactoidTransaction.unmarshal_with_remainder(data)
            current_minute_transactions.append(tx)

        assert tx_count_observed == tx_count, "Unexpected transaction count!"

        return FactoidBlockBody(transactions=transactions), data

    def construct_header(
        self,
        prev_keymr: bytes,
        prev_ledger_keymr: bytes,
        ec_exchange_rate: int,
        height: int,
    ) -> FactoidBlockHeader:
        """
        Seals this factoid block body by constructing and returning it's header
        """
        tx_count = 0
        for tx_list in self.transactions.values():
            tx_count += len(tx_list)
        return FactoidBlockHeader(
            body_mr=self.merkle_root,
            prev_keymr=prev_keymr,
            prev_ledger_keymr=prev_ledger_keymr,
            ec_exchange_rate=ec_exchange_rate,
            height=height,
            expansion_area=b"",
            tx_count=tx_count,
            body_size=len(self.marshal()),
        )


@dataclass
class FactoidBlock:

    header: FactoidBlockHeader
    body: FactoidBlockBody

    _cached_keymr: bytes = None

    def __post_init__(self):
        # TODO: value assertions
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
    def ledger_keymr(self):
        pass  # TODO: calculate ledger keymr

    def marshal(self):
        """Marshals the factoid block according to the byte-level representation shown at
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#factoid-block

        Data returned does not include contextual metadata, such as timestamp or the pointer to the next factoid block.
        """
        buf = bytearray()
        buf.extend(self.header.marshal())
        buf.extend(self.body.marshal())
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        """Returns a new FactoidBlock object, unmarshalling given bytes according to:
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#factoid-block

        Useful for working with a single fblock out of context, pulled directly from a factomd database for instance.

        FactoidBlock created will not include contextual metadata, such as timestamp or the pointer to the
        next factoid block.
        """
        block, data = cls.unmarshal_with_remainder(raw)
        assert len(data) == 0, "Extra bytes remaining!"
        return block

    @classmethod
    def unmarshal_with_remainder(cls, raw: bytes):
        header, data = FactoidBlockHeader.unmarshal_with_remainder(raw)
        body, data = FactoidBlockBody.unmarshal_with_remainder(data, header.tx_count)
        return FactoidBlock(header=header, body=body), data

    def add_context(self, directory_block: DirectoryBlock):
        pass

    def to_dict(self):
        return {
            "keymr": self.keymr.hex(),
            "body_mr": self.header.body_mr.hex(),
            "prev_keymr": self.header.prev_keymr.hex(),
            "prev_ledger_keymr": self.header.prev_ledger_keymr.hex(),
            "ec_exchange_rate": self.header.ec_exchange_rate,
            "height": self.header.height,
            "expansion_area": self.header.expansion_area.hex(),
            "transaction_count": self.header.tx_count,
            "body_size": self.header.body_size,
            "transactions": {
                minute: [tx.to_dict() for tx in txs]
                for minute, txs in self.body.transactions.items()
            },
        }

    def __str__(self):
        return "{}(height={}, keymr={})".format(
            self.__class__.__name__, self.header.height, self.keymr.hex()
        )
