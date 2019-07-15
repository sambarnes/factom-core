import bottle
import os
import factom_core.messages
import factom_core.db
from enum import Enum


bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024
app = bottle.default_app()

rest_path = "/rest/v1"


class RestPaths(Enum):
    DIRECTORY_BLOCK = f"{rest_path}/dblocks"
    ADMIN_BLOCK = f"{rest_path}/ablocks"
    FACTOID_BLOCK = f"{rest_path}/fblocks"
    ENTRY_CREDIT_BLOCK = f"{rest_path}/ecblocks"
    ENTRY_BLOCK = f"{rest_path}/eblocks"
    ENTRY = f"{rest_path}/entries"


hex_regex = "[0-9A-Fa-f]{64}"


@bottle.hook("before_request")
def strip_path():
    """Strip trailing '/' on all requests. '/foo' and /foo/' are two unique endpoints in bottle"""
    bottle.request.environ["PATH_INFO"] = bottle.request.environ["PATH_INFO"].rstrip(
        "/"
    )


@bottle.get("/health")
def health_check():
    return {"data": "Healthy!"}


@bottle.get(f"{RestPaths.DIRECTORY_BLOCK.value}/<keymr:re:{hex_regex}>")
def get_directory_block(keymr: str):
    db = get_db()
    block = db.get_directory_block(keymr=bytes.fromhex(keymr))
    db.close()
    return block.__str__()


@bottle.get(f"{RestPaths.DIRECTORY_BLOCK.value}/<height:int>")
def get_directory_block_by_height(height: int):
    db = get_db()
    block = db.get_directory_block(height=height)
    db.close()
    return block.__str__()


@bottle.get(f"{RestPaths.ADMIN_BLOCK.value}/<lookup_hash:re:{hex_regex}>")
def get_admin_block(lookup_hash: str):
    db = get_db()
    block = db.get_factoid_block(keymr=bytes.fromhex(lookup_hash))
    db.close()
    return block.__str__()


@bottle.get(f"{RestPaths.ADMIN_BLOCK.value}/<height:int>")
def get_admin_block_by_height(height: int):
    db = get_db()
    block = db.get_admin_block(height=height)
    db.close()
    return block.__str__()


@bottle.get(f"{RestPaths.FACTOID_BLOCK.value}/<keymr:re:{hex_regex}>")
def get_factoid_block(keymr: str):
    db = get_db()
    block = db.get_factoid_block(keymr=bytes.fromhex(keymr))
    db.close()
    return block.__str__()


@bottle.get(f"{RestPaths.FACTOID_BLOCK.value}/<height:int>")
def get_factoid_block_by_height(height: int):
    db = get_db()
    block = db.get_factoid_block(height=height)
    db.close()
    return block.__str__()


@bottle.get(f"{RestPaths.ENTRY_CREDIT_BLOCK.value}/<header_hash:re:{hex_regex}>")
def get_entry_credit_block(header_hash: str):
    db = get_db()
    block = db.get_entry_credit_block(keymr=bytes.fromhex(header_hash))
    db.close()
    return block.__str__()


@bottle.get(f"{RestPaths.ENTRY_CREDIT_BLOCK.value}/<height:int>")
def get_entry_credit_block_by_height(height: int):
    db = get_db()
    block = db.get_entry_credit_block(height=height)
    db.close()
    return block.__str__()


@bottle.get(f"{RestPaths.ENTRY_BLOCK.value}/<keymr:re:{hex_regex}>")
def get_entry_block(keymr: str):
    db = get_db()
    block = db.get_entry_block(keymr=bytes.fromhex(keymr))
    db.close()
    return block.__str__()


@bottle.get(f"{RestPaths.ENTRY.value}/<entry_hash:re:{hex_regex}>")
def get_entry(entry_hash: str):
    db = get_db()
    entry = db.get_entry(bytes.fromhex(entry_hash))
    db.close()
    return entry.__str__()


def get_db() -> factom_core.db.FactomdLevelDB:
    home = os.getenv("HOME")
    path = f"{home}/.factom/m2/main-database/ldb/MAIN/factoid_level.db/"
    return factom_core.db.FactomdLevelDB(path)


def run():
    bottle.run(host="localhost", port=8000)
