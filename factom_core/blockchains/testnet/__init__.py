from .constants import (
    TESTNET_NETWORK_ID
)

from factom_core.blockchains import Blockchain


class TestnetBlockchain(Blockchain):
    network_id = TESTNET_NETWORK_ID
