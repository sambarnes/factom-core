import struct
from dataclasses import dataclass
from factom_core.blocks.entry_block import EntryBlock
from hashlib import sha256, sha512


@dataclass
class Entry:

    chain_id: bytes
    external_ids: list
    content: bytes

    _cached_entry_hash: bytes = None

    directory_block_keymr: bytes = None
    entry_block_keymr: bytes = None
    height: int = None
    timestamp: int = None
    stage: str = None

    def __post_init__(self):
        # TODO: value assertions
        pass
        # Optional contextual metadata. Derived from the directory block that contains this EntryBlock

    @property
    def entry_hash(self):
        """The entry hash in bytes. The algorithm used, along with the rationale behind its use, is shown at:
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#entry-hash
        """
        if self._cached_entry_hash is not None:
            return self._cached_entry_hash

        # Entry Hash = SHA256(SHA512(marshalled_entry_data) + marshalled_entry_data)
        data = self.marshal()
        h = sha512(data).digest()
        self._cached_entry_hash = sha256(h + data).digest()
        return self._cached_entry_hash

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
        ext_id_data = b""
        for external_id in self.external_ids:
            size = len(external_id)
            external_ids_size += size + 2
            ext_id_data += struct.pack(">h", size)
            ext_id_data += external_id
        size = struct.pack(">h", external_ids_size)
        buf.extend(size)
        buf.extend(ext_id_data)
        buf.extend(self.content)
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        """Returns a new Entry object, unmarshalling given bytes according to:
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#entry

        Useful for working with a single entry out of context, pulled directly from a factomd database for instance.

        Entry created will not include contextual metadata, such as created_at, entry_block, directory_block, stage, and
        other information inferred from where the entry lies in its chain.
        """
        data = raw[
            1:
        ]  # skip single byte version, probably just gonna be 0x00 for a long time anyways
        chain_id, data = data[:32], data[32:]
        external_ids_size, data = struct.unpack(">h", data[:2])[0], data[2:]
        external_ids = []
        while external_ids_size > 0:
            size, data = struct.unpack(">h", data[:2])[0], data[2:]
            external_id, data = data[:size], data[size:]
            external_ids.append(external_id)
            external_ids_size = external_ids_size - size - 2
        content = data  # Leftovers are the entry content
        return Entry(chain_id=chain_id, external_ids=external_ids, content=content)

    def add_context(self, entry_block: EntryBlock):
        self.directory_block_keymr = entry_block.directory_block_keymr
        self.entry_block_keymr = entry_block.keymr
        self.height = entry_block.header.height
        # Find what minute this entry appeared in within the entry block
        base_timestamp = entry_block.timestamp
        for minute, entry_hashes in entry_block.entry_hashes.items():
            if self.entry_hash in entry_hashes:
                self.timestamp = base_timestamp + minute * 60
                break
        else:
            # Entry not found, raise an error
            raise ValueError("provided EntryBlock does not contain this entry")

    def to_dict(self):
        return {
            # Required
            "chain_id": self.chain_id.hex(),
            "entry_hash": self.entry_hash.hex(),
            "external_ids": [e.hex() for e in self.external_ids],
            "content": self.content.hex(),
            # Optional contextual
            "directory_block_keymr": None
            if self.directory_block_keymr is None
            else self.directory_block_keymr.hex(),
            "entry_block_keymr": None
            if self.entry_block_keymr is None
            else self.entry_block_keymr.hex(),
            "height": self.height,
            "timestamp": self.timestamp,
            "stage": self.stage,
        }

    def __str__(self):
        return "{}(chain_id={}, entry_hash={})".format(
            self.__class__.__name__, self.chain_id.hex(), self.entry_hash.hex()
        )
