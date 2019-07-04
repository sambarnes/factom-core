import struct
from .directory_block import DirectoryBlock


class EntryBlock:
    def __init__(self, keymr: bytes, chain_id: bytes, body_mr: bytes, prev_keymr: bytes, prev_full_hash: bytes,
                 sequence: int, height: int, entry_hashes: dict, **kwargs):
        # Required fields. Must be in every EntryBlock
        self.keymr = keymr
        self.chain_id = chain_id
        self.body_mr = body_mr
        self.prev_keymr = prev_keymr
        self.prev_full_hash = prev_full_hash
        self.sequence = sequence
        self.height = height
        self.entry_hashes = entry_hashes
        # TODO: assert they're all here

        # Optional contextual metadata. Derived from the directory block that contains this EntryBlock
        self.directory_block_keymr = kwargs.get('directory_block_keymr')
        self.timestamp = kwargs.get('timestamp')
        self.next_keymr = kwargs.get('next_keymr')

    def marshal(self):
        """Marshals the entry block according to the byte-level representation shown at
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#entry-block

        Data returned does not include contextual metadata, such as timestamp or the pointer to the next entry block.
        """
        buf = bytearray()
        buf.extend(self.chain_id)
        buf.extend(self.body_mr)
        buf.extend(self.prev_keymr)
        buf.extend(self.prev_full_hash)
        buf.extend(struct.pack('>I', self.sequence))
        buf.extend(struct.pack('>I', self.height))
        entry_count = 0
        for hashes in self.entry_hashes.values():
            entry_count += len(hashes) + 1
        buf.extend(struct.pack('>I', entry_count))
        for minute, hashes in self.entry_hashes.items():
            for h in hashes:
                buf.extend(h)
            buf.extend(bytes(31))
            buf.append(minute)
        return bytes(buf)

    @classmethod
    def unmarshal(cls, keymr: bytes, raw: bytes):
        """Returns a new EntryBlock object, unmarshalling given bytes according to:
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#entry-block

        Useful for working with a single eblock out of context, pulled directly from a factomd database for instance.

        EntryBlock created will not include contextual metadata, such as timestamp or the pointer to the
        next entry block.
        """
        chain_id, data = raw[:32], raw[32:]
        body_mr, data = data[:32], data[32:]
        prev_keymr, data = data[:32], data[32:]
        prev_full_hash, data = data[:32], data[32:]
        sequence, data = struct.unpack('>I', data[:4])[0], data[4:]
        height, data = struct.unpack('>I', data[:4])[0], data[4:]
        entry_count, data = struct.unpack('>I', data[:4])[0], data[4:]

        # Entry hashes are listed in order, with a minute marker following what minute those entries were in
        entry_hashes = {}
        current_minute_entries = []
        for i in range(entry_count):
            entry_hash, data = data[:32], data[32:]
            minute_marker = int(entry_hash.hex(), 16)
            if minute_marker <= 10:
                entry_hashes[minute_marker] = current_minute_entries
                current_minute_entries = []
            else:
                current_minute_entries.append(entry_hash)

        assert len(data) == 0, 'Extra bytes remaining!'

        return EntryBlock(
            keymr=keymr,
            chain_id=chain_id,
            body_mr=body_mr,
            prev_keymr=prev_keymr,
            prev_full_hash=prev_full_hash,
            sequence=sequence,
            height=height,
            entry_hashes=entry_hashes,
        )

    def add_context(self, directory_block: DirectoryBlock):
        self.directory_block_keymr = directory_block.keymr
        self.timestamp = directory_block.timestamp

    def to_dict(self):
        return {
            # Required
            'keymr': self.keymr,
            'chain_id': self.chain_id,
            'prev_keymr': self.prev_keymr,
            'prev_full_hash': self.prev_full_hash,
            'sequence': self.sequence,
            'height': self.height,
            'entry_hashes': self.entry_hashes,
            # Optional contextual
            'directory_block_keymr': self.directory_block_keymr,
            'timestamp': self.timestamp,
            'next_keymr': self.next_keymr
        }

    def __str__(self):
        return '{}(height={}, keymr={})'.format(self.__class__.__name__, self.height, self.keymr.hex())

