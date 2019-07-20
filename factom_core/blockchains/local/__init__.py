from .constants import LOCAL_NETWORK_ID

from factom_core.blockchains import Blockchain


class LocalBlockchain(Blockchain):
    network_id = LOCAL_NETWORK_ID
