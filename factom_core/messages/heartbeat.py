import struct
from dataclasses import dataclass

import factom_core.primitives as primitives
from factom_core.blockchains import Blockchain
from factom_core.messages import Message


@dataclass
class Heartbeat(Message):
    """
    A heartbeat message for Audit Servers to send out
    """

    TYPE = 10

    timestamp: bytes
    secret_number: int
    height: int
    directory_block_hash: bytes
    chain_id: bytes
    signature: primitives.FullSignature

    def __post_init__(self):
        # TODO: type/value assertions
        self.is_p2p = True
        super().__post_init__()

    def marshal(self) -> bytes:
        """
        Marshal the message into the following representation:
        - first byte is the message type (always 10)
        - next 6 bytes are the timestamp
        - next 4 bytes are a secret number
        - next 4 bytes are the directory block height
        - next 32 bytes are the directory block hash
        - next 32 bytes are the server's identity chain id
        - next 32 bytes are the signing public key
        - next 64 bytes are the signature

        :return: byte representation of the message
        """
        buf = bytearray()
        buf.append(self.TYPE)
        buf.extend(self.timestamp)
        buf.extend(struct.pack(">I", self.secret_number))
        buf.extend(struct.pack(">I", self.height))
        buf.extend(self.chain_id)
        buf.extend(self.signature.marshal())
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))

        timestamp, data = data[:6], data[6:]
        secret_number, data = struct.unpack(">I", data[:4])[0], data[4:]
        height, data = struct.unpack(">I", data[:4])[0], data[4:]
        directory_block_hash, data = data[:32], data[32:]
        chain_id, data = data[:32], data[32:]
        signature, data = primitives.FullSignature.unmarshal(data[:96]), data[96:]

        return Heartbeat(
            timestamp=timestamp,
            secret_number=secret_number,
            height=height,
            directory_block_hash=directory_block_hash,
            chain_id=chain_id,
            signature=signature,
        )

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.hex(),
            "secret_number": self.secret_number,
            "height": self.height,
            "directory_block_hash": self.directory_block_hash.hex(),
            "chain_id": self.chain_id.hex(),
            "signature": self.signature.to_dict(),
        }

    def leader_execute(self, state: Blockchain):
        self.follower_execute(state)

    def follower_execute(self, state: Blockchain):
        pass
