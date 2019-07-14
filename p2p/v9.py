import zlib
from p2p import (
    Protocol,
    ParcelType,
)


class HeaderV9:
    def __init__(self, network: bytes, version: int, parcel_type: ParcelType, length: int, target_peer: str, crc32: int,
                 part_number: int, parts_total: int, node_id: int, peer_address: str, peer_port: str, app_hash: str,
                 app_type: str):
        self.network = network
        self.version = version
        self.parcel_type = parcel_type
        self.length = length
        self.target_peer = target_peer
        self.crc32 = crc32
        self.part_number = part_number
        self.parts_total = parts_total
        self.node_id = node_id
        self.peer_address = peer_address
        self.peer_port = peer_port
        self.app_hash = app_hash
        self.app_type = app_type


class MessageV9:
    def __init__(self, header: HeaderV9, payload: bytes):
        self.header = header
        self.payload = payload
        self.set_payload(payload)

    def set_payload(self, payload: bytes):
        self.payload = payload
        self.header.crc32 = zlib.crc32(self.payload)
        self.header.length = len(payload)


class ShareV9:
    pass


class ProtocolV9(Protocol):
    version = "9"

    def __init__(self):
        super().__init__()

    def send(self, parcel):
        pass

    def receive(self):
        pass

    def make_peer_share(self, ps: list) -> bytes:
        pass

    def parse_peer_share(self, payload: bytes):
        pass
