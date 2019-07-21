import hashlib
from factom_core.blockchains import Blockchain


class CustomBlockchain(Blockchain):
    def __init__(self, network_name: str, data_path: str) -> None:
        self.network_id = hashlib.sha256(network_name.encode()).digest()[:4]
        super().__init__(data_path)
