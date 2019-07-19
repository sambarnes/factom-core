from .constants import MAINNET_NETWORK_ID

from factom_core.blockchains import Blockchain


class MainnetBlockchain(Blockchain):
    network_id = MAINNET_NETWORK_ID
