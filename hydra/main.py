import click
import multiprocessing
import time
import requests

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
    )
)


@click.group()
def main():
    pass


@main.command()
def run():
    """Main entry point for the node"""
    print(HYDRA_HEADER)
    api = multiprocessing.Process(name="api_server", target=api_server.run)
    sync = multiprocessing.Process(name="sync", target=sync_start)
    api.start()
    sync.start()


def sync_start():
    while True:
        print("Running node...")
        time.sleep(30)


# --------------------
# RPC wrapper commands
# --------------------


@main.command()
@click.argument("block_id")
def get_directory_block(block_id):
    r = requests.get(
        f"http://localhost:8000{api_server.RestPaths.DIRECTORY_BLOCK.value}/{block_id}"
    )
    print(r.text)


@main.command()
@click.argument("block_id")
def get_admin_block(block_id):
    r = requests.get(
        f"http://localhost:8000{api_server.RestPaths.ADMIN_BLOCK.value}/{block_id}"
    )
    print(r.text)


@main.command()
@click.argument("block_id")
def get_factoid_block(block_id):
    r = requests.get(
        f"http://localhost:8000{api_server.RestPaths.FACTOID_BLOCK.value}/{block_id}"
    )
    print(r.text)


@main.command()
@click.argument("block_id")
def get_entry_credit_block(block_id):
    r = requests.get(
        f"http://localhost:8000{api_server.RestPaths.ENTRY_CREDIT_BLOCK.value}/{block_id}"
    )
    print(r.text)


@main.command()
@click.argument("keymr")
def get_entry_block(keymr):
    r = requests.get(
        f"http://localhost:8000{api_server.RestPaths.ENTRY_BLOCK.value}/{keymr}"
    )
    print(r.text)


@main.command()
@click.argument("entry_hash")
def get_entry(entry_hash):
    r = requests.get(
        f"http://localhost:8000{api_server.RestPaths.ENTRY.value}/{entry_hash}"
    )
    print(r.text)


if __name__ == "__main__":
    main()
