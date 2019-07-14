import asyncio
import datetime

from p2p import (
    P2PConfiguration,
    Parcel,
    ParcelType,
    Protocol,
)

from p2p.v9 import (
    HeaderV9,
    MessageV9,
)


class Handshake(MessageV9):  # use v9 as the base for backwards compatibility
    @classmethod
    def from_config(cls, config: P2PConfiguration, nonce: bytes):
        header = HeaderV9(
            network=config.network,
            version=config.protocol_version,
            parcel_type=ParcelType.HANDSHAKE,
            length=len(nonce),
            node_id=config.node_id,
            peer_port=config.listen_port,
            app_hash="NetworkMessage",
            app_type="Network",
        )
        return Handshake(
            header=header,
            payload=nonce,
        )


class PeerMetrics:
    def __init__(self, peer_hash : str, peer_address: str, moment_connected: int, peer_quality: int, last_receive: int,
                 last_send: int, messages_sent: int, bytes_sent: int, messages_received: int, bytes_received: int,
                 incoming: bool, peer_type: str, connection_state: str):
        self.peer_hash = peer_hash
        self.peer_address = peer_address
        self.moment_connected = moment_connected
        self.peer_quality = peer_quality
        self.last_receive = last_receive
        self.last_send = last_send
        self.messages_sent = messages_sent
        self.bytes_sent = bytes_sent
        self.messages_received = messages_received
        self.bytes_received = bytes_received
        self.incoming = incoming
        self.peer_type = peer_type
        self.connection_state = connection_state
        

class Peer:
    def __init__(
            self,
            network,
            connection,
            protocol: Protocol,
            is_incoming: bool,
            ip: str,
            node_id: int,
            peer_hash: str,
            last_peer_request: int, last_peer_send: int,
            is_peer_share_ask: bool,
            time_connected: int,
            quality_score: int,
            last_receive: int, last_send: int,
            parcels_sent: int, parcels_received: int,
            bytes_sent: int, bytes_received: int,
    ):
        self.network = network
        self.connection = connection
        self.protocol = protocol
        self.is_incoming = is_incoming
        self.ip = ip
        self.node_id = node_id
        self.peer_hash = peer_hash
        self.last_peer_request = last_peer_request
        self.last_peer_send = last_peer_send
        self.is_peer_share_ask = is_peer_share_ask

        # Metrics
        self.metrics_lock = asyncio.Lock()
        self.time_connected = time_connected
        self.quality_score = quality_score
        self.last_receive = last_receive
        self.last_send = last_send
        self.parcels_sent = parcels_sent
        self.parcels_received = parcels_received
        self.bytes_sent = bytes_sent
        self.bytes_received = bytes_received

    def start_with_handshake(self) -> bool:
        """
        StartWithHandshake performs a basic handshake maneuver to establish the validity
        of the connection. Immediately sends a Peer Request upon connection and waits for the
        response, which can be any parcel. The information in the header is verified, especially the port.
        
        The handshake ensures that ALL peers have a valid Port field to start with.
        If there is no reply within the specified HandshakeTimeout config setting, the process fails

        :return: True if successful, False otherwise
        """
        timeout = int(datetime.datetime.now().timestamp()) + self.network.config.handshake_timeout
        nonce = self.network.instance_id
        handshake = Handshake.from_config(self.network.config, nonce)

        # TODO: gob encoder and decoder... https://github.com/mgeisler/pygob
        # TODO: send out the handshake and get the response
        return False

    def stop(self) -> None:
        """
        Stop disconnects the peer from its active connection

        :return: None
        """
        pass

    def send(self, parcel: Parcel) -> None:
        pass

    def quality(self, diff: int) -> int:
        pass

    def read_loop(self) -> None:
        pass

    def deliver(self, parcel: Parcel) -> bool:
        """
        A blocking delivery of this peer's messages to the peer manager

        :param parcel: Parcel to be delivered
        :return: True if successful, False otherwise
        """
        pass

    def send_loop(self) -> None:
        """
        Listens to the Outgoing channel, pushing all data from there to the TCP connection

        :return: None
        """
        pass

    def get_metrics(self) -> PeerMetrics:
        """
        Get live metrics for this connection

        :return: a PeerMetrics object representing this Peer in its current state
        """
        yield from self.metrics_lock
        try:
            peer_type = "regular"
            # TODO: check if peer type is special, and if so, set it to "special_config"
            metrics = PeerMetrics(
                peer_hash=self.peer_hash,
                peer_address=self.ip,
                moment_connected=self.time_connected,
                peer_quality=self.quality_score,
                last_receive=self.last_receive,
                last_send=self.last_send,
                messages_sent=self.parcels_sent,
                bytes_sent=self.bytes_sent,
                messages_received=self.parcels_received,
                bytes_received=self.bytes_received,
                incoming=self.is_incoming,
                peer_type=peer_type,
                connection_state="v{}".format(self.protocol.version),
            )
        finally:
            self.metrics_lock.release()
        return metrics
