import factom_core
import struct


class DirectoryBlock:

    def __init__(self, keymr: bytes, network_id: bytes, body_mr: bytes, prev_keymr: bytes, prev_full_hash: bytes,
                 timestamp: int, height: int, admin_block_lookup_hash: bytes, entry_credit_block_header_hash:  bytes,
                 factoid_block_keymr:  bytes, entry_blocks: list, **kwargs):
        # Required fields
        self.keymr = keymr
        self.network_id = network_id
        self.body_mr = body_mr
        self.prev_keymr = prev_keymr
        self.prev_full_hash = prev_full_hash
        self.timestamp = timestamp
        self.height = height
        self.admin_block_lookup_hash = admin_block_lookup_hash
        self.entry_credit_block_header_hash = entry_credit_block_header_hash
        self.factoid_block_keymr = factoid_block_keymr
        self.entry_blocks = entry_blocks

        # Optional contextual fields
        self.next_keymr = kwargs.get('next_keymr')
        self.anchor_entry_hash = kwargs.get('anchor_entry_hash')

    def marshal(self):
        """Marshals the directory block according to the byte-level representation shown at
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#directory-block

        Data returned does not include contextual metadata, such as anchor information or the pointer to the
        next directory block.
        """
        buf = bytearray()
        buf.append(0x00)
        buf.extend(self.network_id)
        buf.extend(self.body_mr)
        buf.extend(self.prev_keymr)
        buf.extend(self.prev_full_hash)
        buf.extend(struct.pack('>I', self.timestamp))
        buf.extend(struct.pack('>I', self.height))
        buf.extend(struct.pack('>I', len(self.entry_blocks) + 3))
        buf.extend(factom_core.blocks.AdminBlock.CHAIN_ID)
        buf.extend(self.admin_block_lookup_hash)
        buf.extend(factom_core.blocks.EntryCreditBlock.CHAIN_ID)
        buf.extend(self.entry_credit_block_header_hash)
        buf.extend(factom_core.blocks.FactoidBlock.CHAIN_ID)
        buf.extend(self.factoid_block_keymr)
        for e_block in self.entry_blocks:
            buf.extend(e_block.get('chain_id'))
            buf.extend(e_block.get('keymr'))
        return bytes(buf)

    @classmethod
    def unmarshal(cls, keymr: bytes, raw: bytes):
        """Returns a new DirectoryBlock object, unmarshalling given bytes according to:
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#directory-block

        Useful for working with a single dblock out of context, pulled directly from a factomd database for instance.

        DirectoryBlock created will not include contextual metadata, such as anchor information or the pointer to the
        next directory block.
        """
        data = raw[1:]  # skip single byte version
        network_id, data = data[:4], data[4:]
        body_mr, data = data[:32], data[32:]
        prev_keymr, data = data[:32], data[32:]
        prev_full_hash, data = data[:32], data[32:]
        timestamp, data = struct.unpack('>I', data[:4])[0], data[4:]
        height, data = struct.unpack('>I', data[:4])[0], data[4:]
        block_count, data = struct.unpack('>I', data[:4])[0], data[4:]
        admin_block_chain_id, data = data[:32], data[32:]
        assert admin_block_chain_id == factom_core.blocks.AdminBlock.CHAIN_ID
        admin_block_lookup_hash, data = data[:32], data[32:]
        entry_credit_block_chain_id, data = data[:32], data[32:]
        assert entry_credit_block_chain_id == factom_core.blocks.EntryCreditBlock.CHAIN_ID
        entry_credit_block_header_hash, data = data[:32], data[32:]
        factoid_block_chain_id, data = data[:32], data[32:]
        assert factoid_block_chain_id == factom_core.blocks.FactoidBlock.CHAIN_ID
        factoid_block_keymr, data = data[:32], data[32:]
        entry_blocks = []
        for i in range(block_count - 3):
            entry_block_chain_id, data = data[:32], data[32:]
            entry_block_keymr, data = data[:32], data[32:]
            entry_blocks.append({'chain_id': entry_block_chain_id, 'keymr': entry_block_keymr})
        assert len(data) == 0, 'Extra bytes remaining!'

        return DirectoryBlock(
            keymr=keymr,
            network_id=network_id,
            body_mr=body_mr,
            prev_keymr=prev_keymr,
            prev_full_hash=prev_full_hash,
            timestamp=timestamp,
            height=height,
            admin_block_lookup_hash=admin_block_lookup_hash,
            entry_credit_block_header_hash=entry_credit_block_header_hash,
            factoid_block_keymr=factoid_block_keymr,
            entry_blocks=entry_blocks,
        )

    def to_dict(self):
        return {
            'keymr': self.keymr,
            'network_id': self.network_id,
            'body_mr': self.body_mr,
            'prev_keymr': self.prev_keymr,
            'next_keymr': self.next_keymr,
            'prev_full_hash': self.prev_full_hash,
            'height': self.height,
            'admin_block_lookup_hash': self.admin_block_lookup_hash,
            'entry_credit_block_header_hash': self.entry_credit_block_header_hash,
            'factoid_block_keymr': self.factoid_block_keymr,
            'entry_blocks': [
                {'chain_id': chain_id, 'keymr': keymr}
                for chain_id, keymr in self.entry_blocks
            ]
        }

    def __str__(self):
        return '{}(height={}, keymr={})'.format(self.__class__.__name__, self.height, self.keymr.hex())

