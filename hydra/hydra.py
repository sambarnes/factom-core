#!/usr/bin/env python3.7

import click
import json
import multiprocessing
import requests
import sys
import time

import factom_core.blockchains as blockchains
import factom_core.db

import p2p_server
from rpc import server as api_server


HYDRA_HEADER = "\n".join(
    (
        "\n",
        r"   _               _           ",
        r"  | |__  _   _  __| |_ __ __ _ ",
        r"  | '_ \| | | |/ _` | '__/ _` |",
        r"  | | | | |_| | (_| | | | (_| |",
        r"  |_| |_|\__, |\__,_|_|  \__,_|",
        r"         |___/                 ",
        "\n",
    )
)


@click.group()
def main():
    pass


@main.command()
def run():
    """Main entry point for the node"""
    print(HYDRA_HEADER)

    inbox = multiprocessing.Queue()
    p2p = multiprocessing.Process(name="p2p", target=p2p_server.run, args=(inbox,))
    api = multiprocessing.Process(name="api_server", target=api_server.run)

    p2p.start()
    api.start()
    sync_start(inbox)


def sync_start(inbox: multiprocessing.Queue):
    blockchain = blockchains.MainnetBlockchain()
    print(f"Loading From Database at: {blockchain.db.data_path}")

    head = blockchain.db.get_directory_block_head()
    if head is None:
        print("Database empty, loading genesis block...")
        head = blockchain.load_genesis_block()

    print(f"Finished loading from database. Current block head:\n{head}")
    blockchain.current_block = blockchains.PendingBlock(previous=head)

    print("Running node...")
    try:
        while True:
            msg = inbox.get()
            if msg is None:
                time.sleep(0.5)
                continue
            print(msg.__class__.__name__, msg.to_dict())
    except (KeyboardInterrupt, SystemExit):
        sys.exit()


# --------------------
# RPC wrapper commands
# --------------------

ERROR_NOT_FOUND = '{"error": {"detail": "not found"}}'


@main.command()
@click.option("--connection-type", "-c", type=click.Choice(["rpc", "db"]))
@click.argument("block_id")
def get_directory_block(connection_type, block_id):
    if connection_type == "db":
        db = factom_core.db.FactomdLevelDB(create_if_missing=True)
        block = (
            db.get_directory_block(height=int(block_id))
            if len(block_id) < 64
            else db.get_directory_block(keymr=bytes.fromhex(block_id))
        )
        print(json.dumps(block.to_dict()) if block is not None else ERROR_NOT_FOUND)
        return
    r = requests.get(
        f"http://localhost:8000{api_server.RestPaths.DIRECTORY_BLOCK.value}/{block_id}"
    )
    print(r.text)


@main.command()
@click.option("--connection-type", "-c", type=click.Choice(["rpc", "db"]))
def get_directory_block_head(connection_type):
    if connection_type == "db":
        db = factom_core.db.FactomdLevelDB(create_if_missing=True)
        block = db.get_directory_block_head()
        print(json.dumps(block.to_dict()) if block is not None else ERROR_NOT_FOUND)
        return
    r = requests.get(
        f"http://localhost:8000{api_server.RestPaths.DIRECTORY_BLOCK.value}/head"
    )
    print(r.text)


@main.command()
@click.option("--connection-type", "-c", type=click.Choice(["rpc", "db"]))
@click.argument("block_id")
def get_admin_block(connection_type, block_id):
    if connection_type == "db":
        db = factom_core.db.FactomdLevelDB(create_if_missing=True)
        block = (
            db.get_admin_block(height=int(block_id))
            if len(block_id) < 64
            else db.get_admin_block(lookup_hash=bytes.fromhex(block_id))
        )
        print(json.dumps(block.to_dict()) if block is not None else ERROR_NOT_FOUND)
        return
    r = requests.get(
        f"http://localhost:8000{api_server.RestPaths.ADMIN_BLOCK.value}/{block_id}"
    )
    print(r.text)


@main.command()
@click.option("--connection-type", "-c", type=click.Choice(["rpc", "db"]))
def get_admin_block_head(connection_type):
    if connection_type == "db":
        db = factom_core.db.FactomdLevelDB(create_if_missing=True)
        block = db.get_admin_block_head()
        print(json.dumps(block.to_dict()) if block is not None else ERROR_NOT_FOUND)
        return
    r = requests.get(
        f"http://localhost:8000{api_server.RestPaths.ADMIN_BLOCK.value}/head"
    )
    print(r.text)


@main.command()
@click.option("--connection-type", "-c", type=click.Choice(["rpc", "db"]))
@click.argument("block_id")
def get_factoid_block(connection_type, block_id):
    if connection_type == "db":
        db = factom_core.db.FactomdLevelDB(create_if_missing=True)
        block = (
            db.get_factoid_block(height=int(block_id))
            if len(block_id) < 64
            else db.get_factoid_block(keymr=bytes.fromhex(block_id))
        )
        print(json.dumps(block.to_dict()) if block is not None else ERROR_NOT_FOUND)
        return
    r = requests.get(
        f"http://localhost:8000{api_server.RestPaths.FACTOID_BLOCK.value}/{block_id}"
    )
    print(r.text)


@main.command()
@click.option("--connection-type", "-c", type=click.Choice(["rpc", "db"]))
def get_factoid_block_head(connection_type):
    if connection_type == "db":
        db = factom_core.db.FactomdLevelDB(create_if_missing=True)
        block = db.get_factoid_block_head()
        print(json.dumps(block.to_dict()) if block is not None else ERROR_NOT_FOUND)
        return
    r = requests.get(
        f"http://localhost:8000{api_server.RestPaths.FACTOID_BLOCK.value}/head"
    )
    print(r.text)


@main.command()
@click.option("--connection-type", "-c", type=click.Choice(["rpc", "db"]))
@click.argument("block_id")
def get_entry_credit_block(connection_type, block_id):
    if connection_type == "db":
        db = factom_core.db.FactomdLevelDB(create_if_missing=True)
        block = (
            db.get_entry_credit_block(height=int(block_id))
            if len(block_id) < 64
            else db.get_entry_credit_block(keymr=bytes.fromhex(block_id))
        )
        print(json.dumps(block.to_dict()) if block is not None else ERROR_NOT_FOUND)
        return
    r = requests.get(
        f"http://localhost:8000{api_server.RestPaths.ENTRY_CREDIT_BLOCK.value}/{block_id}"
    )
    print(r.text)


@main.command()
@click.option("--connection-type", "-c", type=click.Choice(["rpc", "db"]))
def get_entry_credit_block_head(connection_type):
    if connection_type == "db":
        db = factom_core.db.FactomdLevelDB(create_if_missing=True)
        block = db.get_entry_credit_block_head()
        print(json.dumps(block.to_dict()) if block is not None else ERROR_NOT_FOUND)
        return
    r = requests.get(
        f"http://localhost:8000{api_server.RestPaths.ENTRY_CREDIT_BLOCK.value}/head"
    )
    print(r.text)


@main.command()
@click.option("--connection-type", "-c", type=click.Choice(["rpc", "db"]))
@click.argument("keymr")
def get_entry_block(connection_type, keymr):
    if connection_type == "db":
        db = factom_core.db.FactomdLevelDB(create_if_missing=True)
        block = db.get_entry_block(keymr=keymr)
        print(json.dumps(block.to_dict()) if block is not None else ERROR_NOT_FOUND)
        return
    r = requests.get(
        f"http://localhost:8000{api_server.RestPaths.ENTRY_BLOCK.value}/{keymr}"
    )
    print(r.text)


@main.command()
@click.option("--connection-type", "-c", type=click.Choice(["rpc", "db"]))
@click.argument("chain-id")
def get_entry_block_head(connection_type, chain_id):
    if connection_type == "db":
        db = factom_core.db.FactomdLevelDB(create_if_missing=True)
        block = db.get_entry_block_head(chain_id=bytes.fromhex(chain_id))
        print(json.dumps(block.to_dict()) if block is not None else ERROR_NOT_FOUND)
        return
    r = requests.get(
        f"http://localhost:8000{api_server.RestPaths.ENTRY_BLOCK.value}/{chain_id}/head"
    )
    print(r.text)


@main.command()
@click.option("--connection-type", "-c", type=click.Choice(["rpc", "db"]))
@click.argument("entry_hash")
def get_entry(connection_type, entry_hash):
    if connection_type == "db":
        db = factom_core.db.FactomdLevelDB(create_if_missing=True)
        block = db.get_entry(bytes.fromhex(entry_hash))
        print(json.dumps(block.to_dict()) if block is not None else ERROR_NOT_FOUND)
        return
    r = requests.get(
        f"http://localhost:8000{api_server.RestPaths.ENTRY.value}/{entry_hash}"
    )
    print(r.text)


if __name__ == "__main__":
    main()
