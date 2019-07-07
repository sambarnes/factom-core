class Protocol:

    version = None  # type: str

    def __init__(self):
        """
        Protocol is the interface for reading and writing parcels to the underlying connection.
        The job of a protocol is to encode a Parcel and send it over TCP to another instance of
        the same Protocol on the other end.
        

        
        Every protocol should be bootstraped in peer:bootstrapProtocol() where
        it can be initialized with the required serialization methods
        """
        if not isinstance(self.version, str) or len(self.version) == 0:
            raise ValueError("The Protocol class must be instantiated with a non-empty `version` string")

    def send(self, parcel):
        """
        Parcel => Protocol Encoder => Protocol Format => TCP

        :param parcel:
        :return:
        """
        pass

    def receive(self):
        """
        Receive: TCP => Protocol Format => Protocol Decoder => Parcel

        :return: the parcel object received
        """
        pass

    def make_peer_share(self, ps: list) -> bytes:
        """
        Creates the protocol specific payload for a TypePeerShare Parcel

        :param ps:
        :return: peer share payload
        """
        pass

    def parse_peer_share(self, payload: bytes):
        """
        Parses a marshalled peer share payload

        :param payload: marshalled peer share payload
        :return: list of peer share objects
        """
        pass


class ProtocolV10(Protocol):
    version = "10"

    def send(self, parcel):
        pass

    def receive(self):
        pass

    def make_peer_share(self, ps: list) -> bytes:
        pass

    def parse_peer_share(self, payload: bytes):
        pass


class ProtocolV9(Protocol):
    version = "9"

    def send(self, parcel):
        pass

    def receive(self):
        pass

    def make_peer_share(self, ps: list) -> bytes:
        pass

    def parse_peer_share(self, payload: bytes):
        pass
