import bottle
import json
import sys
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
    db = factom_core.db.FactomdLevelDB(create_if_missing=True)
    block = db.get_directory_block(keymr=bytes.fromhex(keymr))
    db.close()
    if block is None:
        bottle.abort(404)
    return block.to_dict()


@app.get(f"{RestPaths.DIRECTORY_BLOCK.value}/<height:int>")
def get_directory_block_by_height(height: int):
    db = factom_core.db.FactomdLevelDB(create_if_missing=True)
    block = db.get_directory_block(height=height)
    db.close()
    if block is None:
        bottle.abort(404)
    return block.to_dict()


@app.get(f"{RestPaths.DIRECTORY_BLOCK.value}/head")
def get_directory_block_head():
    db = factom_core.db.FactomdLevelDB(create_if_missing=True)
    block = db.get_directory_block_head()
    db.close()
    if block is None:
        bottle.abort(404)
    return block.to_dict()


@bottle.get(f"{RestPaths.ADMIN_BLOCK.value}/<lookup_hash:re:{hex_regex}>")
def get_admin_block(lookup_hash: str):
    db = factom_core.db.FactomdLevelDB(create_if_missing=True)
    block = db.get_admin_block(lookup_hash=bytes.fromhex(lookup_hash))
    db.close()
    if block is None:
        bottle.abort(404)
    return block.to_dict()


@app.get(f"{RestPaths.ADMIN_BLOCK.value}/<height:int>")
def get_admin_block_by_height(height: int):
    db = factom_core.db.FactomdLevelDB(create_if_missing=True)
    block = db.get_admin_block(height=height)
    db.close()
    if block is None:
        bottle.abort(404)
    return block.to_dict()


@bottle.get(f"{RestPaths.ADMIN_BLOCK.value}/head")
def get_admin_block_head():
    db = factom_core.db.FactomdLevelDB(create_if_missing=True)
    block = db.get_admin_block_head()
    db.close()
    if block is None:
        bottle.abort(404)
    return block.to_dict()


@bottle.get(f"{RestPaths.FACTOID_BLOCK.value}/<keymr:re:{hex_regex}>")
def get_factoid_block(keymr: str):
    db = factom_core.db.FactomdLevelDB(create_if_missing=True)
    block = db.get_factoid_block(keymr=bytes.fromhex(keymr))
    db.close()
    if block is None:
        bottle.abort(404)
    return block.to_dict()


@bottle.get(f"{RestPaths.FACTOID_BLOCK.value}/<height:int>")
def get_factoid_block_by_height(height: int):
    db = factom_core.db.FactomdLevelDB(create_if_missing=True)
    block = db.get_factoid_block(height=height)
    db.close()
    if block is None:
        bottle.abort(404)
    return block.to_dict()


@bottle.get(f"{RestPaths.FACTOID_BLOCK.value}/head")
def get_factoid_block_head():
    db = factom_core.db.FactomdLevelDB(create_if_missing=True)
    block = db.get_factoid_block_head()
    db.close()
    if block is None:
        bottle.abort(404)
    return block.to_dict()


@bottle.get(f"{RestPaths.ENTRY_CREDIT_BLOCK.value}/<header_hash:re:{hex_regex}>")
def get_entry_credit_block(header_hash: str):
    db = factom_core.db.FactomdLevelDB(create_if_missing=True)
    block = db.get_entry_credit_block(keymr=bytes.fromhex(header_hash))
    db.close()
    if block is None:
        bottle.abort(404)
    return block.to_dict()


@bottle.get(f"{RestPaths.ENTRY_CREDIT_BLOCK.value}/<height:int>")
def get_entry_credit_block_by_height(height: int):
    db = factom_core.db.FactomdLevelDB(create_if_missing=True)
    block = db.get_entry_credit_block(height=height)
    db.close()
    if block is None:
        bottle.abort(404)
    return block.to_dict()


@bottle.get(f"{RestPaths.ENTRY_CREDIT_BLOCK.value}/head")
def get_entry_credit_block_head():
    db = factom_core.db.FactomdLevelDB(create_if_missing=True)
    block = db.get_entry_credit_block_head()
    db.close()
    if block is None:
        bottle.abort(404)
    return block.to_dict()


@bottle.get(f"{RestPaths.ENTRY_BLOCK.value}/<keymr:re:{hex_regex}>")
def get_entry_block(keymr: str):
    db = factom_core.db.FactomdLevelDB(create_if_missing=True)
    block = db.get_entry_block(keymr=bytes.fromhex(keymr))
    db.close()
    if block is None:
        bottle.abort(404)
    return block.to_dict()


@bottle.get(f"{RestPaths.ENTRY_BLOCK.value}/<chain_id:re:{hex_regex}>/head")
def get_entry_block_head(chain_id: str):
    db = factom_core.db.FactomdLevelDB(create_if_missing=True)
    block = db.get_entry_block_head(chain_id=bytes.fromhex(chain_id))
    db.close()
    if block is None:
        bottle.abort(404)
    return block.to_dict()


@bottle.get(f"{RestPaths.ENTRY.value}/<entry_hash:re:{hex_regex}>")
def get_entry(entry_hash: str):
    db = factom_core.db.FactomdLevelDB(create_if_missing=True)
    entry = db.get_entry(bytes.fromhex(entry_hash))
    db.close()
    if entry is None:
        bottle.abort(404)
    return entry.to_dict()


@bottle.error(404)
def error404(e):
    body = {"errors": {"detail": "Object not found"}}
    return json.dumps(body, separators=(",", ":"))


def run():
    print("Starting API Server (localhost:8000)...")
    try:
        bottle.run(host="localhost", port=8000, quiet=True)
    except (KeyboardInterrupt, SystemExit):
        sys.exit()


if __name__ == "__main__":
    run()
