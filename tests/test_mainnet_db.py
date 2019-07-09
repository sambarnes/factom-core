import unittest

import os
from factom_core.db import FactomdLevelDB


class TestMainnetDatabase(unittest.TestCase):

    @classmethod
    def _load_block_from_db(cls, db: FactomdLevelDB, height: int = 0):
        directory_block = db.get_directory_block(height=height)
        if directory_block is None:
            print('Block not found. All blocks loaded.')
            return True

        # Load system blocks (admin, factoid, and entry credit)
        admin_block = db.get_admin_block(lookup_hash=directory_block.admin_block_lookup_hash)
        assert admin_block.header.height == height
        admin_block_by_height = db.get_admin_block(height=height)
        assert admin_block.marshal() == admin_block_by_height.marshal()
        assert admin_block.lookup_hash == admin_block_by_height.lookup_hash

        factoid_block = db.get_factoid_block(keymr=directory_block.factoid_block_keymr)
        assert factoid_block.header.height == height
        factoid_block_by_height = db.get_factoid_block(height=height)
        assert factoid_block.marshal() == factoid_block_by_height.marshal()
        assert factoid_block.keymr == factoid_block_by_height.keymr

        entry_credit_block = db.get_entry_credit_block(header_hash=directory_block.entry_credit_block_header_hash)
        assert entry_credit_block.header.height == height
        entry_credit_block_by_height = db.get_entry_credit_block(height=height)
        assert entry_credit_block.marshal() == entry_credit_block_by_height.marshal()
        assert entry_credit_block.header_hash == entry_credit_block_by_height.header_hash

        # Load all entry blocks within the directory block
        for descriptor in directory_block.entry_blocks:
            keymr = descriptor.get('keymr')
            entry_block = db.get_entry_block(keymr)
            assert entry_block.header.height == height
            entry_block.add_context(directory_block)

            # Load all entries in all minutes within the entry block
            for minute, entry_hashes_in_minute in entry_block.entry_hashes.items():
                for entry_hash in entry_hashes_in_minute:
                    entry = db.get_entry(entry_hash)
                    entry.add_context(entry_block)
                    assert entry.height == height

        return TestMainnetDatabase._load_block_from_db(db, height + 1)

    def test_load(self):
        home = os.getenv("HOME")
        path = '{home}/.factom/m2/main-database/ldb/MAIN/factoid_level.db/'.format(home=home)
        level_db = FactomdLevelDB(path)
        assert TestMainnetDatabase._load_block_from_db(level_db) is True
        level_db.close()
