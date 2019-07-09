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
        """
        A wrapper around the legacy factomd level-db

        :param path: filepath to the factomd leveldb database, typically in one of the following locations:
        Mainnet = /home/$USER/.factom/m2/main-database/ldb/LOCAL/factoid_level.db/
        Custom = /home/$USER/.factom/m2/custom-database/ldb/LOCAL/factoid_level.db/
        Local = /home/$USER/.factom/m2/local-database/ldb/LOCAL/factoid_level.db/
        """
        self._db = plyvel.DB(path)

    def close(self):
        self._db.close()

    def get_directory_block(self, **kwargs):
        keymr = kwargs.get('keymr')
        height = kwargs.get('height')
        assert (keymr is None and type(height) is int) or (type(keymr) is bytes and height is None)
        if height is not None:
            sub_db = self._db.prefixed_db(DIRECTORY_BLOCK_NUMBER)
            height_encoded = struct.pack('>I', height)
            keymr = sub_db.get(height_encoded)
            if keymr is None:
                return None
        sub_db = self._db.prefixed_db(DIRECTORY_BLOCK)
        raw = sub_db.get(keymr)
        return None if raw is None else blocks.DirectoryBlock.unmarshal(raw)

    def put_directory_block(self, block: blocks.DirectoryBlock):
        sub_db = self._db.prefixed_db(DIRECTORY_BLOCK_NUMBER)
        sub_db.put(struct.pack('>I', block.header.height), block.keymr)
        sub_db = self._db.prefixed_db(DIRECTORY_BLOCK)
        sub_db.put(block.keymr, block.marshal())

    def get_admin_block(self, **kwargs):
        lookup_hash = kwargs.get('lookup_hash')
        height = kwargs.get('height')
        assert (lookup_hash is None and type(height) is int) or (type(lookup_hash) is bytes and height is None)
        if height is not None:
            sub_db = self._db.prefixed_db(ADMIN_BLOCK_NUMBER)
            height_encoded = struct.pack('>I', height)
            lookup_hash = sub_db.get(height_encoded)
            if lookup_hash is None:
                return None
        sub_db = self._db.prefixed_db(ADMIN_BLOCK)
        raw = sub_db.get(lookup_hash)
        if raw is None:
            return None
        block = blocks.AdminBlock.unmarshal(raw)
        block._cached_lookup_hash = lookup_hash  # TODO: remove setting of lookup hash once calculation implemented
        return block

    def put_admin_block(self, block: blocks.AdminBlock):
        sub_db = self._db.prefixed_db(ADMIN_BLOCK_NUMBER)
        sub_db.put(struct.pack('>I', block.header.height), block.lookup_hash)
        sub_db = self._db.prefixed_db(ADMIN_BLOCK)
        sub_db.put(block.lookup_hash, block.marshal())

    def get_factoid_block(self, **kwargs):
        keymr = kwargs.get('keymr')
        height = kwargs.get('height')
        assert (keymr is None and type(height) is int) or (type(keymr) is bytes and height is None)
        if height is not None:
            sub_db = self._db.prefixed_db(FACTOID_BLOCK_NUMBER)
            height_encoded = struct.pack('>I', height)
            keymr = sub_db.get(height_encoded)
            if keymr is None:
                return None
        sub_db = self._db.prefixed_db(FACTOID_BLOCK)
        raw = sub_db.get(keymr)
        if raw is None:
            return None
        block = blocks.FactoidBlock.unmarshal(raw)
        block._cached_keymr = keymr  # TODO: remove setting of keymr once calculation implemented
        return block

    def put_factoid_block(self, block: blocks.FactoidBlock):
        sub_db = self._db.prefixed_db(FACTOID_BLOCK_NUMBER)
        sub_db.put(struct.pack('>I', block.header.height), block.keymr)
        sub_db = self._db.prefixed_db(FACTOID_BLOCK)
        sub_db.put(block.keymr, block.marshal())

    def get_entry_credit_block(self, **kwargs):
        header_hash = kwargs.get('header_hash')
        height = kwargs.get('height')
        assert (header_hash is None and type(height) is int) or (type(header_hash) is bytes and height is None)
        if height is not None:
            sub_db = self._db.prefixed_db(ENTRY_CREDIT_BLOCK_NUMBER)
            height_encoded = struct.pack('>I', height)
            header_hash = sub_db.get(height_encoded)
            if header_hash is None:
                return None
        sub_db = self._db.prefixed_db(ENTRY_CREDIT_BLOCK)
        raw = sub_db.get(header_hash)
        if raw is None:
            return None
        block = blocks.EntryCreditBlock.unmarshal(raw)
        block._cached_header_hash = header_hash  # TODO: remove setting of header hash once calculation implemented
        return block

    def put_entry_credit_block(self, block: blocks.EntryCreditBlock):
        sub_db = self._db.prefixed_db(ENTRY_CREDIT_BLOCK_NUMBER)
        sub_db.put(struct.pack('>I', block.header.height), block.header_hash)
        sub_db = self._db.prefixed_db(ENTRY_CREDIT_BLOCK)
        sub_db.put(block.header_hash, block.marshal())

    def get_entry_block(self, keymr: bytes):
        sub_db = self._db.prefixed_db(ENTRY_BLOCK)
        raw = sub_db.get(keymr)
        if raw is None:
            return None
        block = blocks.EntryBlock.unmarshal(raw)
        block._cached_keymr = keymr  # TODO: remove setting of keymr once calculation implemented
        return block

    def put_entry_block(self, block: blocks.EntryBlock):
        sub_db = self._db.prefixed_db(ENTRY_BLOCK)
        sub_db.put(block.keymr, block.marshal())

    def get_entry(self, entry_hash: bytes):
        sub_db = self._db.prefixed_db(ENTRY)
        chain_id = sub_db.get(entry_hash)
        raw = self._db.get(chain_id + b';' + entry_hash)
        return None if raw is None else block_elements.Entry.unmarshal(raw)

    def put_entry(self, entry: block_elements.Entry):
        sub_db = self._db.prefixed_db(ENTRY)
        sub_db.put(entry.entry_hash, entry.chain_id)
        sub_db = self._db.prefixed_db(entry.chain_id + ';'.encode())
        sub_db.put(entry.entry_hash, entry.marshal())
