import plyvel
import os
import struct
from typing import List, Tuple, Union

import factom_core.blocks as blocks
import factom_core.block_elements as block_elements

DIRECTORY_BLOCK = b"DirectoryBlock;"
DIRECTORY_BLOCK_NUMBER = b"DirectoryBlockNumber;"
DIRECTORY_BLOCK_SECONDARY = b"DirectoryBlockSecondaryIndex;"

ADMIN_BLOCK = b"AdminBlock;"
ADMIN_BLOCK_NUMBER = b"AdminBlockNumber;"
ADMIN_BLOCK_SECONDARY = b"AdminBlockSecondaryIndex;"

FACTOID_BLOCK = b"FactoidBlock;"
FACTOID_BLOCK_NUMBER = b"FactoidBlockNumber;"
FACTOID_BLOCK_SECONDARY = b"FactoidBlockSecondaryIndex;"

ENTRY_CREDIT_BLOCK = b"EntryCreditBlock;"
ENTRY_CREDIT_BLOCK_NUMBER = b"EntryCreditBlockNumber;"
ENTRY_CREDIT_BLOCK_SECONDARY = b"EntryCreditBlockSecondaryIndex;"

CHAIN_HEAD = b"ChainHead;"

ENTRY_BLOCK = b"EntryBlock;"
ENTRY_BLOCK_NUMBER = b"EntryBlockNumber;"
ENTRY_BLOCK_SECONDARY = b"EntryBlockSecondaryIndex;"

ENTRY = b"Entry;"

DIR_BLOCK_INFO = b"DirBlockInfo;"
DIR_BLOCK_INFO_UNCONFIRMED = b"DirBlockInfoUnconfirmed;"
DIR_BLOCK_INFO_NUMBER = b"DirBlockInfoNumber;"
DIR_BLOCK_INFO_SECONDARY = b"DirBlockInfoSecondaryIndex;"

INCLUDED_IN = b"IncludedIn;"

PAID_FOR = b"PaidFor;"
KEY_VALUE_STORE = b"KeyValueStore;"


FullBlockSet = Tuple[
    blocks.DirectoryBlock,
    blocks.AdminBlock,
    blocks.EntryCreditBlock,
    blocks.FactoidBlock,
    List[blocks.EntryBlock],
]


class FactomdLevelDB:
    def __init__(self, path: str = None, **kwargs):
        """
        A wrapper around the legacy factomd level-db

        :param path: filepath to the factomd leveldb database, defaults to: /$HOME/.factom/hydra/data/
        """
        if path is None:
            home = os.getenv("HOME")
            path = f"{home}/.factom/hydra/data/"
        self._db = plyvel.DB(path, **kwargs)

    def close(self):
        self._db.close()

    def get_chain_head(self, chain_id: bytes):
        sub_db = self._db.prefixed_db(CHAIN_HEAD)
        return sub_db.get(chain_id)

    def put_chain_head(self, chain_id: bytes, head: bytes):
        sub_db = self._db.prefixed_db(CHAIN_HEAD)
        sub_db.put(chain_id, head)

    #
    # Directory Block
    #

    def get_directory_block(self, **kwargs) -> Union[blocks.DirectoryBlock, None]:
        keymr = kwargs.get("keymr")
        height = kwargs.get("height")
        assert (keymr is None and type(height) is int) or (
            type(keymr) is bytes and height is None
        )
        if height is not None:
            sub_db = self._db.prefixed_db(DIRECTORY_BLOCK_NUMBER)
            height_encoded = struct.pack(">I", height)
            keymr = sub_db.get(height_encoded)
            if keymr is None:
                return None
        sub_db = self._db.prefixed_db(DIRECTORY_BLOCK)
        raw = sub_db.get(keymr)
        return None if raw is None else blocks.DirectoryBlock.unmarshal(raw)

    def get_directory_block_head(self) -> Union[blocks.DirectoryBlock, None]:
        prev_keymr = self.get_chain_head(blocks.DirectoryBlockHeader.CHAIN_ID)
        if prev_keymr is None:
            return None
        return self.get_directory_block(keymr=prev_keymr)

    def put_directory_block(self, block: blocks.DirectoryBlock):
        sub_db = self._db.prefixed_db(DIRECTORY_BLOCK_NUMBER)
        sub_db.put(struct.pack(">I", block.header.height), block.keymr)
        sub_db = self._db.prefixed_db(DIRECTORY_BLOCK)
        sub_db.put(block.keymr, block.marshal())

    def put_directory_block_head(self, block: blocks.DirectoryBlock):
        self.put_directory_block(block)
        self.put_chain_head(block.header.CHAIN_ID, block.keymr)

    #
    # Admin Block
    #

    def get_admin_block(self, **kwargs) -> Union[blocks.AdminBlock, None]:
        lookup_hash = kwargs.get("lookup_hash")
        height = kwargs.get("height")
        assert (lookup_hash is None and type(height) is int) or (
            type(lookup_hash) is bytes and height is None
        )
        if height is not None:
            sub_db = self._db.prefixed_db(ADMIN_BLOCK_NUMBER)
            height_encoded = struct.pack(">I", height)
            lookup_hash = sub_db.get(height_encoded)
            if lookup_hash is None:
                return None
        sub_db = self._db.prefixed_db(ADMIN_BLOCK)
        raw = sub_db.get(lookup_hash)
        if raw is None:
            return None
        block = blocks.AdminBlock.unmarshal(raw)
        return block

    def get_admin_block_head(self) -> Union[blocks.AdminBlock, None]:
        prev_hash = self.get_chain_head(blocks.AdminBlockHeader.CHAIN_ID)
        if prev_hash is None:
            return None
        return self.get_admin_block(lookup_hash=prev_hash)

    def put_admin_block(self, block: blocks.AdminBlock):
        sub_db = self._db.prefixed_db(ADMIN_BLOCK_NUMBER)
        sub_db.put(struct.pack(">I", block.header.height), block.lookup_hash)
        sub_db = self._db.prefixed_db(ADMIN_BLOCK)
        sub_db.put(block.lookup_hash, block.marshal())

    def put_admin_block_head(self, block: blocks.AdminBlock):
        self.put_admin_block(block)
        self.put_chain_head(block.header.CHAIN_ID, block.lookup_hash)

    #
    # Factoid Block
    #

    def get_factoid_block(self, **kwargs) -> Union[blocks.FactoidBlock, None]:
        keymr = kwargs.get("keymr")
        height = kwargs.get("height")
        assert (keymr is None and type(height) is int) or (
            type(keymr) is bytes and height is None
        )
        if height is not None:
            sub_db = self._db.prefixed_db(FACTOID_BLOCK_NUMBER)
            height_encoded = struct.pack(">I", height)
            keymr = sub_db.get(height_encoded)
            if keymr is None:
                return None
        sub_db = self._db.prefixed_db(FACTOID_BLOCK)
        raw = sub_db.get(keymr)
        if raw is None:
            return None
        block = blocks.FactoidBlock.unmarshal(raw)
        return block

    def get_factoid_block_head(self) -> Union[blocks.FactoidBlock, None]:
        prev_keymr = self.get_chain_head(blocks.FactoidBlockHeader.CHAIN_ID)
        if prev_keymr is None:
            return None
        return self.get_factoid_block(keymr=prev_keymr)

    def put_factoid_block(self, block: blocks.FactoidBlock):
        sub_db = self._db.prefixed_db(FACTOID_BLOCK_NUMBER)
        sub_db.put(struct.pack(">I", block.header.height), block.keymr)
        sub_db = self._db.prefixed_db(FACTOID_BLOCK)
        sub_db.put(block.keymr, block.marshal())

    def put_factoid_block_head(self, block: blocks.FactoidBlock):
        self.put_factoid_block(block)
        self.put_chain_head(block.header.CHAIN_ID, block.keymr)

    #
    # Entry Credit Block
    #

    def get_entry_credit_block(self, **kwargs) -> Union[blocks.EntryCreditBlock, None]:
        header_hash = kwargs.get("header_hash")
        height = kwargs.get("height")
        assert (header_hash is None and type(height) is int) or (
            type(header_hash) is bytes and height is None
        )
        if height is not None:
            sub_db = self._db.prefixed_db(ENTRY_CREDIT_BLOCK_NUMBER)
            height_encoded = struct.pack(">I", height)
            header_hash = sub_db.get(height_encoded)
            if header_hash is None:
                return None
        sub_db = self._db.prefixed_db(ENTRY_CREDIT_BLOCK)
        raw = sub_db.get(header_hash)
        if raw is None:
            return None
        block = blocks.EntryCreditBlock.unmarshal(raw)
        return block

    def get_entry_credit_block_head(self) -> Union[blocks.EntryCreditBlock, None]:
        prev_hash = self.get_chain_head(blocks.EntryCreditBlockHeader.CHAIN_ID)
        if prev_hash is None:
            return None
        return self.get_entry_credit_block(header_hash=prev_hash)

    def put_entry_credit_block(self, block: blocks.EntryCreditBlock):
        sub_db = self._db.prefixed_db(ENTRY_CREDIT_BLOCK_NUMBER)
        sub_db.put(struct.pack(">I", block.header.height), block.header_hash)
        sub_db = self._db.prefixed_db(ENTRY_CREDIT_BLOCK)
        sub_db.put(block.header_hash, block.marshal())

    def put_entry_credit_block_head(self, block: blocks.EntryCreditBlock):
        self.put_entry_credit_block(block)
        self.put_chain_head(block.header.CHAIN_ID, block.header_hash)

    #
    # Entry Block
    #

    def get_entry_block(self, keymr: bytes) -> Union[blocks.EntryBlock, None]:
        sub_db = self._db.prefixed_db(ENTRY_BLOCK)
        raw = sub_db.get(keymr)
        if raw is None:
            return None
        block = blocks.EntryBlock.unmarshal(raw)
        return block

    def get_entry_block_head(self, chain_id: bytes) -> Union[blocks.EntryBlock, None]:
        prev_keymr = self.get_chain_head(chain_id)
        if prev_keymr is None:
            return None
        return self.get_entry_block(prev_keymr)

    def put_entry_block(self, block: blocks.EntryBlock):
        sub_db = self._db.prefixed_db(ENTRY_BLOCK)
        sub_db.put(block.keymr, block.marshal())

    def put_entry_block_head(self, block: blocks.EntryBlock):
        self.put_entry_block(block)
        self.put_chain_head(block.header.chain_id, block.keymr)

    #
    # Entry
    #

    def get_entry(self, entry_hash: bytes) -> block_elements.Entry:
        sub_db = self._db.prefixed_db(ENTRY)
        chain_id = sub_db.get(entry_hash)
        if chain_id is None:
            return None
        raw = self._db.get(chain_id + b";" + entry_hash)
        return None if raw is None else block_elements.Entry.unmarshal(raw)

    def put_entry(self, entry: block_elements.Entry):
        sub_db = self._db.prefixed_db(ENTRY)
        sub_db.put(entry.entry_hash, entry.chain_id)
        sub_db = self._db.prefixed_db(entry.chain_id + ";".encode())
        sub_db.put(entry.entry_hash, entry.marshal())
