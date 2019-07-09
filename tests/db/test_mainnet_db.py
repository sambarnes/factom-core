import unittest

import os
from factom_core.db import FactomdLevelDB


class TestMainnetDatabase(unittest.TestCase):

    @classmethod
    def _load_block_from_db(cls, db: FactomdLevelDB, height: int):
        directory_block = db.get_directory_block(height=height)
        if directory_block is None:
            return False

        admin_block = db.get_admin_block(height=height)
        if admin_block.lookup_hash != directory_block.admin_block_lookup_hash:
            print("Admin Block Lookup Hash in DBlock {} != Admin Block Lookup Hash at that height: {} != {}".format(
                height, directory_block.admin_block_lookup_hash.hex(), admin_block.lookup_hash.hex()))

        factoid_block = db.get_factoid_block(height=height)
        if factoid_block.keymr != directory_block.factoid_block_keymr:
            print("Factoid KeyMR in DBlock {} != Factoid Block KeyMR at that height: {} != {}".format(
                height, directory_block.factoid_block_keymr.hex(), factoid_block.keymr.hex()))

        entry_credit_block = db.get_entry_credit_block(height=height)
        if entry_credit_block is None:
            print("EC Block does not exist for DBlock {}".format(height))
        elif entry_credit_block.header_hash != directory_block.entry_credit_block_header_hash:
            print("EC Block Header Hash in DBlock {} != EC Block Header Hash at that height: {} != {}".format(
                height, directory_block.entry_credit_block_header_hash.hex(), entry_credit_block.header_hash.hex()))

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
        return True

    def test_all_blocks(self):
        home = os.getenv("HOME")
        path = '{home}/.factom/m2/main-database/ldb/MAIN/factoid_level.db/'.format(home=home)
        level_db = FactomdLevelDB(path)
        height = 0
        while True:
            result = None
            try:
                result = TestMainnetDatabase._load_block_from_db(level_db, height)
            except (ValueError, AssertionError) as e:
                print("Error at height {}: {}".format(height, e))
            if result is False:
                break
            height += 1
        level_db.close()

    def test_single_block(self):
        home = os.getenv("HOME")
        path = '{home}/.factom/m2/main-database/ldb/MAIN/factoid_level.db/'.format(home=home)
        level_db = FactomdLevelDB(path)
        height = 91949
        result = None
        try:
            result = TestMainnetDatabase._load_block_from_db(level_db, height)
        except (ValueError, AssertionError) as e:
            print("Error: {}".format(e))

        level_db.close()
        assert result is True
