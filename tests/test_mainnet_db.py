import unittest

from factom_core.db import FactomdLevelDB


class TestMainnetDatabase(unittest.TestCase):

    @classmethod
    def _load_block_from_db(cls, db: FactomdLevelDB, height: int = 0):
        directory_block = db.get_directory_block(height=height)
        if directory_block is None:
            print('Block not found. All blocks loaded.')
            return True

        # Sync all entry blocks within the directory block
        for descriptor in directory_block.entry_blocks:
            keymr = descriptor.get('keymr').hex()
            entry_block = db.get_entry_block(keymr)
            entry_block.add_context(directory_block)  # Contextual information like timestamp and directory block keymr

            # Sync all entries in all minutes within the entry block
            for minute, entry_hashes_in_minute in entry_block.entry_hashes.items():
                for entry_hash in entry_hashes_in_minute:
                    entry = db.get_entry(entry_hash.hex())
                    entry.add_context(entry_block)

        return TestMainnetDatabase._load_block_from_db(db, height + 1)

    def test_sync(self):
        path = '/home/sam/.factom/m2/local-database/ldb/LOCAL/factoid_level.db/'
        level_db = FactomdLevelDB(path)
        assert TestMainnetDatabase._load_block_from_db(level_db) is True
        level_db.close()




