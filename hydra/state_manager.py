import multiprocessing
import os
import sys
import time

import factom_core.blockchains as blockchains

import p2p_server
from rpc import server as api_server


inbox = multiprocessing.Queue()


def start(network: str):
    p2p = multiprocessing.Process(name="p2p", target=p2p_server.run, args=(inbox,))
    api = multiprocessing.Process(name="api_server", target=api_server.run)
    db_loader = multiprocessing.Process(name="db_loader", target=load_database, args=(network,))

    p2p.start()
    api.start()
    db_loader.start()

    process_messages()


def load_database(network: str):
    home = os.getenv("HOME")
    if network is None or network == "mainnet":
        blockchain = blockchains.MainnetBlockchain()
    elif network == "testnet":
        data_path = f"{home}/.factom/hydra/data-testnet/"
        blockchain = blockchains.TestnetBlockchain(data_path)
    elif network == "localnet":
        data_path = f"{home}/.factom/hydra/data-localnet/"
        blockchain = blockchains.LocalBlockchain(data_path)
    else:
        data_path = f"{home}/.factom/hydra/data-{network}/"
        blockchain = blockchains.CustomBlockchain(
            network_name=network, data_path=data_path
        )

    print(f"Network: {network}")
    print(f"Loading From Database at: {blockchain.data_path}")

    head = blockchain.db.get_directory_block_head()
    if head is None:
        print("Database empty, loading genesis block...")
        head = blockchain.load_genesis_block()

    print(f"Finished loading from database. Current block head:\n{head}")
    blockchain.current_block = blockchains.PendingBlock(previous=head)


def process_messages():
    print("Running node...")
    try:
        while True:
            msg = inbox.get()
            if msg is None:
                time.sleep(0.5)
                continue
    except (KeyboardInterrupt, SystemExit):
        sys.exit()