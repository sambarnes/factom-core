import struct
from .directory_block import DirectoryBlock
from factom_core.block_elements.factoid_transaction import FactoidTransaction
from factom_core.utils import varint


class FactoidBlockHeader:

    CHAIN_ID = bytes.fromhex("000000000000000000000000000000000000000000000000000000000000000f")

    def __init__(self, body_mr: bytes, prev_keymr: bytes, prev_ledger_keymr: bytes, ec_exchange_rate: int, height: int,
                 expansion_area: bytes, transaction_count: int, body_size: int):
        self.body_mr = body_mr
        self.prev_keymr = prev_keymr
        self.prev_ledger_keymr = prev_ledger_keymr
        self.ec_exchange_rate = ec_exchange_rate
        self.height = height
        self.expansion_area = expansion_area
        self.transaction_count = transaction_count
        self.body_size = body_size

    def marshal(self) -> bytes:
        buf = bytearray()
        buf.extend(FactoidBlockHeader.CHAIN_ID)
        buf.extend(self.body_mr)
        buf.extend(self.prev_keymr)
        buf.extend(self.prev_ledger_keymr)
        buf.extend(struct.pack('>Q', self.ec_exchange_rate))
        buf.extend(struct.pack('>I', self.height))
        buf.extend(varint.encode(len(self.expansion_area)))
        buf.extend(self.expansion_area)
        buf.extend(struct.pack('>I', self.transaction_count))
        buf.extend(struct.pack('>I', self.body_size))
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        h, data = FactoidBlockHeader.unmarshal_with_remainder(raw)
        assert len(data) == 0, 'Extra bytes remaining!'
        return h

    @classmethod
    def unmarshal_with_remainder(cls, raw: bytes):
        chain_id, data = raw[:32], raw[32:]
        assert chain_id == FactoidBlockHeader.CHAIN_ID
        body_mr, data = data[:32], data[32:]
        prev_keymr, data = data[:32], data[32:]
        prev_ledger_keymr, data = data[:32], data[32:]
        ec_exchange_rate, data = struct.unpack('>Q', data[:8])[0], data[8:]
        height, data = struct.unpack('>I', data[:4])[0], data[4:]

        header_expansion_size, data = varint.decode(data)
        header_expansion_area, data = data[:header_expansion_size], data[header_expansion_size:]

        transaction_count, data = struct.unpack('>I', data[:4])[0], data[4:]
        body_size, data = struct.unpack('>I', data[:4])[0], data[4:]
        return FactoidBlockHeader(
            body_mr=body_mr,
            prev_keymr=prev_keymr,
            prev_ledger_keymr=prev_ledger_keymr,
            ec_exchange_rate=ec_exchange_rate,
            height=height,
            expansion_area=header_expansion_area,
            transaction_count=transaction_count,
            body_size=body_size
        ), data


class FactoidBlock:

    def __init__(self, header: FactoidBlockHeader, transactions: dict, **kwargs):
        # Required fields. Must be in every FactoidBlock
        self.header = header
        self.transactions = transactions
        # TODO: assert they're all here
        # TODO: use kwargs for some optional metadata
        self.keymr = b''  # TODO: calculate keymr

    def marshal(self):
        """Marshals the factoid block according to the byte-level representation shown at
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#factoid-block

        Data returned does not include contextual metadata, such as timestamp or the pointer to the next factoid block.
        """
        buf = bytearray()
        buf.extend(self.header.marshal())
        for transactions in self.transactions.values():
            for tx in transactions:
                buf.extend(tx.marshal())
            buf.append(0x00)
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
        assert len(data) == 0, 'Extra bytes remaining!'
        return block

    @classmethod
    def unmarshal_with_remainder(cls, raw: bytes):
        header, data = FactoidBlockHeader.unmarshal_with_remainder(raw)
        assert header.body_size == len(data), 'header body size does not match actual body size'
        # Body
        transactions = {}
        current_minute_transactions = []
        minute = 1
        transaction_count = 0
        while True:
            if data[0] == 0:
                data = data[1:]
                transactions[minute] = current_minute_transactions
                transaction_count += len(current_minute_transactions)
                if minute == 10:
                    break
                current_minute_transactions = []
                minute += 1
                continue
            tx, data = FactoidTransaction.unmarshal_with_remainder(data)
            current_minute_transactions.append(tx)

        assert transaction_count == header.transaction_count, 'Unexpected transaction count!'

        return FactoidBlock(
            header=header,
            transactions=transactions
        ), data

    def add_context(self, directory_block: DirectoryBlock):
        pass

    def to_dict(self):
        pass
    
    def __str__(self):
        return '{}(height={}, keymr={})'.format(self.__class__.__name__, self.header.height, self.keymr.hex())

