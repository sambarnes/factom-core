import factom_core.blocks as blocks
import factom_core.block_elements as block_elements
import plyvel
import struct

DIRECTORY_BLOCK = b'DirectoryBlock;'
DIRECTORY_BLOCK_NUMBER = b'DirectoryBlockNumber;'
DIRECTORY_BLOCK_SECONDARY = b'DirectoryBlockSecondaryIndex;'

ADMIN_BLOCK = b'AdminBlock;'
ADMIN_BLOCK_NUMBER = b'AdminBlockNumber;'
ADMIN_BLOCK_SECONDARY = b'AdminBlockSecondaryIndex;'

FACTOID_BLOCK = b'FactoidBlock;'
FACTOID_BLOCK_NUMBER = b'FactoidBlockNumber;'
FACTOID_BLOCK_SECONDARY = b'FactoidBlockSecondaryIndex;'

ENTRY_CREDIT_BLOCK = b'EntryCreditBlock;'
ENTRY_CREDIT_BLOCK_NUMBER = b'EntryCreditBlockNumber;'
ENTRY_CREDIT_BLOCK_SECONDARY = b'EntryCreditBlockSecondaryIndex;'

CHAIN_HEAD = b'ChainHead;'

ENTRY_BLOCK = b'EntryBlock;'
ENTRY_BLOCK_NUMBER = b'EntryBlockNumber;'
ENTRY_BLOCK_SECONDARY = b'EntryBlockSecondaryIndex;'

ENTRY = b'Entry;'

DIR_BLOCK_INFO = b'DirBlockInfo;'
DIR_BLOCK_INFO_UNCONFIRMED = b'DirBlockInfoUnconfirmed;'
DIR_BLOCK_INFO_NUMBER = b'DirBlockInfoNumber;'
DIR_BLOCK_INFO_SECONDARY = b'DirBlockInfoSecondaryIndex;'

INCLUDED_IN = b'IncludedIn;'

PAID_FOR = b'PaidFor;'
KEY_VALUE_STORE = b'KeyValueStore;'


class FactomdLevelDB:

    def __init__(self, path: str):
        self._db = plyvel.DB(path)

    def close(self):
        self._db.close()

    def get_directory_block(self, **kwargs):
        keymr = kwargs.get('keymr')
        height = kwargs.get('height')
        assert (keymr is None and isinstance(height, int)) or (isinstance(keymr, str) and height is None)
        if height is not None:
            sub_db = self._db.prefixed_db(DIRECTORY_BLOCK_NUMBER)
            height_encoded = struct.pack('>I', height)
            keymr = sub_db.get(height_encoded)
            if keymr is None:
                return None
        else:
            keymr = bytes.fromhex(keymr)

        sub_db = self._db.prefixed_db(DIRECTORY_BLOCK)
        raw = sub_db.get(keymr)
        return None if raw is None else blocks.DirectoryBlock.unmarshal(raw)

    def put_directory_block(self, directory_block: blocks.DirectoryBlock):
        sub_db = self._db.prefixed_db(DIRECTORY_BLOCK)
        sub_db.put(directory_block.keymr, directory_block.marshal())

    def get_entry_block(self, keymr: str):
        keymr_bytes = bytes.fromhex(keymr)
        sub_db = self._db.prefixed_db(ENTRY_BLOCK)
        raw = sub_db.get(keymr_bytes)
        return None if raw is None else blocks.EntryBlock.unmarshal(raw)

    def put_entry_block(self, entry_block: blocks.EntryBlock):
        sub_db = self._db.prefixed_db(ENTRY_BLOCK)
        sub_db.put(entry_block.keymr, entry_block.marshal())

    def get_entry(self, entry_hash: str):
        sub_db = self._db.prefixed_db(ENTRY)
        entry_hash_bytes = bytes.fromhex(entry_hash)
        chain_id = sub_db.get(entry_hash_bytes)
        raw = self._db.get(chain_id + ';'.encode() + entry_hash_bytes)
        return None if raw is None else block_elements.Entry.unmarshal(raw)

    def put_entry(self, entry: block_elements.Entry):
        sub_db = self._db.prefixed_db(ENTRY)
        sub_db.put(entry.entry_hash, entry.chain_id)
        sub_db = self._db.prefixed_db(entry.chain_id + ';'.encode())
        sub_db.put(entry.entry_hash, entry.marshal())
