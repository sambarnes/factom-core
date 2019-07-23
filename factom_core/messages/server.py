from dataclasses import dataclass

import factom_core.primitives as primitives
from factom_core.blockchains import Blockchain
from factom_core.messages import Message


@dataclass
class AddServer(Message):
    """
    Add the identity as a Federated or Audit server
    """

    TYPE = 22

    timestamp: bytes
    chain_id: bytes
    is_federated: bool
    signature: primitives.FullSignature

    def __post_init__(self):
        # TODO: type/value assertions
        self.is_p2p = True
        super().__post_init__()

    def marshal(self) -> bytes:
        """
        Marshal the message into the following representation:
        - first byte is the message type (always 22)
        - next 6 bytes are a timestamp
        - next 32 bytes are the server's identity chain id
        - next byte is the server type (0 == Federated, 1 == Audit)
        - next 32 bytes are the public key signing this message
        - next 64 bytes are the signature

        :return: byte representation of the message
        """
        buf = bytearray()
        buf.append(self.TYPE)
        buf.extend(self.timestamp)
        buf.extend(self.chain_id)
        buf.append(0 if self.is_federated else 1)
        buf.extend(self.signature.marshal())
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))

        timestamp, data = data[:6], data[6:]
        chain_id, data = data[:32], data[32:]
        server_type, data = data[0], data[1:]
        signature, data = primitives.FullSignature.unmarshal(data[:96]), data[96:]
        assert len(data) == 0, "Extra bytes remaining!"
        return AddServer(
            timestamp=timestamp,
            chain_id=chain_id,
            is_federated=(server_type == 0),  # 0 == Federated, 1 == Audit
            signature=signature,
        )

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.hex(),
            "chain_id": self.chain_id.hex(),
            "is_federated": self.is_federated,
            "signature": self.signature.to_dict(),
        }

    def leader_execute(self, state: Blockchain):
        pass

    def follower_execute(self, state: Blockchain):
        pass


@dataclass
class ChangeServerKey(Message):
    """
    Change the key for the specified server identity
    """

    TYPE = 23

    CHANGE_TYPE_ADD_MATRYOSHKA = 0x03
    CHANGE_TYPE_ADD_FED_SERVER_KEY = 0x08
    CHANGE_TYPE_ADD_BTC_ANCHOR_KEY = 0x09

    timestamp: bytes
    chain_id: bytes
    admin_block_change: int
    key_type: int
    priority: int
    new_key: bytes
    signature: primitives.FullSignature

    def __post_init__(self):
        # TODO: type/value assertions
        super().__post_init__()

    def marshal(self) -> bytes:
        """
        Marshal the message into the following representation:
        - first byte is the message type (always 23)
        - next 6 bytes are a timestamp
        - next 32 bytes are the server's identity chain id
        - next byte is Admin Block Change
        - next byte is the key type
        - next byte is the key priority
        - next 32 bytes are the new public key for the identity
        - next 32 bytes are the public key signing this message
        - next 64 bytes are the signature

        :return: byte representation of the message
        """
        buf = bytearray()
        buf.append(self.TYPE)
        buf.extend(self.timestamp)
        buf.extend(self.chain_id)
        buf.append(self.admin_block_change)
        buf.append(self.key_type)
        buf.append(self.priority)
        buf.extend(self.new_key)
        buf.extend(self.signature.marshal())
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))

        timestamp, data = data[:6], data[6:]
        chain_id, data = data[:32], data[32:]
        admin_block_change, data = data[0], data[1:]
        key_type, data = data[0], data[1:]
        priority, data = data[0], data[1:]
        new_key, data = data[:32], data[32:]
        signature, data = primitives.FullSignature.unmarshal(data[:96]), data[96:]
        assert len(data) == 0, "Extra bytes remaining!"
        return ChangeServerKey(
            timestamp=timestamp,
            chain_id=chain_id,
            admin_block_change=admin_block_change,
            key_type=key_type,
            priority=priority,
            new_key=new_key,
            signature=signature,
        )

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.hex(),
            "chain_id": self.chain_id.hex(),
            "admin_block_change": self.admin_block_change,
            "key_type": self.key_type,
            "priority": self.priority,
            "new_key": self.new_key.hex(),
            "signature": self.signature.to_dict(),
        }

    def leader_execute(self, state: Blockchain):
        pass

    def follower_execute(self, state: Blockchain):
        pass


@dataclass
class RemoveServer(Message):
    """
    Remove the identity as a Federated or Audit server
    """

    TYPE = 24

    timestamp: bytes
    chain_id: bytes
    is_federated: bool
    signature: primitives.FullSignature

    def __post_init__(self):
        # TODO: type/value assertions
        self.is_p2p = True
        super().__post_init__()

    def marshal(self) -> bytes:
        """
        Marshal the message into the following representation:
        - first byte is the message type (always 24)
        - next 6 bytes are a timestamp
        - next 32 bytes are the server's identity chain id
        - next byte is the server type (0 == Federated, 1 == Audit)
        - next 32 bytes are the public key signing this message
        - next 64 bytes are the signature

        :return: byte representation of the message
        """
        buf = bytearray()
        buf.append(self.TYPE)
        buf.extend(self.timestamp)
        buf.extend(self.chain_id)
        buf.append(0 if self.is_federated else 1)
        buf.extend(self.signature.marshal())
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))

        timestamp, data = data[:6], data[6:]
        chain_id, data = data[:32], data[32:]
        server_type, data = data[0], data[1:]
        signature, data = primitives.FullSignature.unmarshal(data[:96]), data[96:]
        assert len(data) == 0, "Extra bytes remaining!"
        return RemoveServer(
            timestamp=timestamp,
            chain_id=chain_id,
            is_federated=(server_type == 0),  # 0 == Federated, 1 == Audit
            signature=signature,
        )

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.hex(),
            "chain_id": self.chain_id.hex(),
            "is_federated": self.is_federated,
            "signature": self.signature.to_dict(),
        }

    def leader_execute(self, state: Blockchain):
        pass

    def follower_execute(self, state: Blockchain):
        pass
