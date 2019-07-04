import struct
from factom_core.blocks.entry_block import EntryBlock
from hashlib import sha256, sha512


class Entry:
    def __init__(self, chain_id: bytes, entry_hash: bytes, external_ids: list, content: bytes, **kwargs):
        # Required fields. Must be in every Entry
        self.chain_id = chain_id
        self.entry_hash = entry_hash
        self.external_ids = external_ids
        self.content = content
        # TODO: assert they're all here
        assert self.entry_hash == self._calculate_entry_hash(), 'entry_hash does not match external_ids and content'

        # Optional contextual metadata. Derived from the directory block that contains this EntryBlock
        self.directory_block_keymr = kwargs.get('directory_block_keymr')
        self.entry_block_keymr = kwargs.get('entry_block_keymr')
        self.height = kwargs.get('height')
        self.timestamp = kwargs.get('timestamp')
        self.stage = kwargs.get('stage', 'replicated')

    def _calculate_entry_hash(self):
        """Returns the entry hash in bytes. The algorithm used, along with the rationale behind its use, is shown at:
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#entry-hash
        """
        # Entry Hash = SHA256(SHA512(marshalled_entry_data) + marshalled_entry_data)
        data = self.marshal()
        h = sha512(data).digest()
        return sha256(h + data).digest()

    def marshal(self):
        """Marshals the entry according to the byte-level representation shown at
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#entry

        Useful for proofs and constructing entry hashes.

        Data returned does not include contextual metadata, such as created_at, entry_block, directory_block, stage,
        and other information inferred from where the entry lies in its chain.
        """
        buf = bytearray()
        buf.append(0x00)  # single byte version
        buf.extend(self.chain_id)
        external_ids_size = 0
        ext_id_data = b''
        for external_id in self.external_ids:
            size = len(external_id)
            external_ids_size += size + 2
            ext_id_data += struct.pack('>h', size)
            ext_id_data += external_id
        size = struct.pack('>h', external_ids_size)
        buf.extend(size)
        buf.extend(ext_id_data)
        buf.extend(self.content)
        return bytes(buf)

    @classmethod
    def unmarshal(cls, entry_hash: bytes, raw: bytes):
        """Returns a new Entry object, unmarshalling given bytes according to:
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#entry

        Useful for working with a single entry out of context, pulled directly from a factomd database for instance.

        Entry created will not include contextual metadata, such as created_at, entry_block, directory_block, stage, and
        other information inferred from where the entry lies in its chain.
        """
        data = raw[1:]  # skip single byte version, probably just gonna be 0x00 for a long time anyways
        chain_id, data = data[:32], data[32:]
        external_ids_size, data = struct.unpack('>h', data[:2])[0], data[2:]
        external_ids = []
        while external_ids_size > 0:
            size, data = struct.unpack('>h', data[:2])[0], data[2:]
            external_id, data = data[:size], data[size:]
            external_ids.append(external_id)
            external_ids_size = external_ids_size - size - 2
        content = data  # Leftovers are the entry content
        return Entry(
            chain_id=chain_id,
            entry_hash=entry_hash,
            external_ids=external_ids,
            content=content
        )

    def add_context(self, entry_block: EntryBlock):
        self.directory_block_keymr = entry_block.directory_block_keymr
        self.entry_block_keymr = entry_block.keymr
        self.height = entry_block.height
        # Find what minute this entry appeared in within the entry block
        base_timestamp = entry_block.timestamp
        for minute, entry_hashes in entry_block.entry_hashes.items():
            if self.entry_hash in entry_hashes:
                self.timestamp = base_timestamp + minute * 60
                break
        else:
            # Entry not found, raise an error
            raise ValueError('provided EntryBlock does not contain this entry')

    def to_dict(self):
        return {
            # Required
            'chain_id': self.chain_id,
            'entry_hash': self.entry_hash,
            'external_ids': self.external_ids,
            'content': self.content,
            # Optional contextual
            'directory_block_keymr': self.directory_block_keymr,
            'entry_block_keymr': self.entry_block_keymr,
            'height': self.height,
            'timestamp': self.timestamp,
            'stage': self.stage
        }

    def __str__(self):
        return '{}(chain_id={}, entry_hash={})'.format(
            self.__class__.__name__, self.chain_id.hex(), self.entry_hash.hex())
