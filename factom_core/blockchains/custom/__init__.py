import hashlib
from factom_core.blockchains import Blockchain


class CustomBlockchain(Blockchain):
    def __init__(self, network_name) -> None:
        self.network_id = hashlib.sha256(network_name.encode()).digest()[:4]
        super().__init__()
