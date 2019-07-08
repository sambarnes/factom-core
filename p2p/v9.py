from p2p import Protocol


class HeaderV9:
    pass


class MessageV9:
    pass


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
