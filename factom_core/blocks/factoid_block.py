import struct
from .directory_block import DirectoryBlock
from factom_core.block_elements.factoid_transaction import FactoidTransaction
from factom_core.utils import varint


class FactoidBlock:

    CHAIN_ID = bytes.fromhex("000000000000000000000000000000000000000000000000000000000000000f")

    def __init__(self, keymr: bytes, body_mr: bytes, prev_keymr: bytes, prev_ledger_keymr: bytes,
                 ec_exchange_rate: int, height: int, header_expansion_area: bytes, transactions: list, **kwargs):
        # Required fields. Must be in every FactoidBlock
        self.keymr = keymr
        self.body_mr = body_mr
        self.prev_keymr = prev_keymr
        self.prev_ledger_keymr = prev_ledger_keymr
        self.ec_exchange_rate = ec_exchange_rate
        self.height = height
        self.header_expansion_area = header_expansion_area
        self.transactions = transactions
        # TODO: assert they're all here
        # TODO: use kwargs for some optional metadata

    def marshal(self):
        """Marshals the factoid block according to the byte-level representation shown at
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#factoid-block

        Data returned does not include contextual metadata, such as timestamp or the pointer to the next factoid block.
        """
        buf = bytearray()
        buf.extend(FactoidBlock.CHAIN_ID)
        buf.extend(self.body_mr)
        buf.extend(self.prev_keymr)
        buf.extend(self.prev_ledger_keymr)
        buf.extend(struct.pack('>Q', self.ec_exchange_rate))
        buf.extend(struct.pack('>I', self.height))
        buf.extend(varint.encode(len(self.header_expansion_area)))
        buf.extend(self.header_expansion_area)
        transaction_count = 0
        body_buf = bytearray()
        for transactions in self.transactions.values():
            transaction_count += len(transactions)
            for tx in transactions:
                body_buf.extend(tx.marshal())
            body_buf.append(0x00)
        buf.extend(struct.pack('>I', transaction_count))
        buf.extend(struct.pack('>I', len(body_buf)))
        buf.extend(body_buf)
        return bytes(buf)

    @classmethod
    def unmarshal(cls, keymr: bytes, raw: bytes):
        """Returns a new FactoidBlock object, unmarshalling given bytes according to:
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#factoid-block

        Useful for working with a single fblock out of context, pulled directly from a factomd database for instance.

        FactoidBlock created will not include contextual metadata, such as timestamp or the pointer to the
        next factoid block.
        """
        chain_id, data = raw[:32], raw[32:]
        assert chain_id == FactoidBlock.CHAIN_ID
        body_mr, data = data[:32], data[32:]
        prev_keymr, data = data[:32], data[32:]
        prev_ledger_keymr, data = data[:32], data[32:]
        ec_exchange_rate, data = struct.unpack('>Q', data[:8])[0], data[8:]
        height, data = struct.unpack('>I', data[:4])[0], data[4:]

        header_expansion_size, data = varint.decode(data)
        header_expansion_area, data = data[:header_expansion_size], data[header_expansion_size:]

        expected_transaction_count, data = struct.unpack('>I', data[:4])[0], data[4:]
        body_size, data = struct.unpack('>I', data[:4])[0], data[4:]
        assert body_size == len(data)

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

        assert transaction_count == expected_transaction_count, 'Unexpected transaction count!'
        assert len(data) == 0, 'Extra bytes remaining!'

        return FactoidBlock(
            keymr=keymr,
            body_mr=body_mr,
            prev_keymr=prev_keymr,
            prev_ledger_keymr=prev_ledger_keymr,
            ec_exchange_rate=ec_exchange_rate,
            height=height,
            header_expansion_area=header_expansion_area,
            transactions=transactions
        )

    def add_context(self, directory_block: DirectoryBlock):
        pass

    def to_dict(self):
        pass
    
    def __str__(self):
        return '{}(height={}, keymr={})'.format(self.__class__.__name__, self.height, self.keymr.hex())

