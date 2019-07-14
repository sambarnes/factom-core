from p2p import Protocol


class HeaderV10:
    pass


class MessageV10:
    pass


class ShareV10:
    pass


class ProtocolV10(Protocol):
    version = "10"

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

