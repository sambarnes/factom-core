from dataclasses import dataclass

import factom_core.block_elements as block_elements
import factom_core.primitives as primitives
from factom_core.blockchains import Blockchain
from factom_core.messages import Message


@dataclass
class FactoidTransaction(Message):
    """
    A message holding a FactoidTransaction object.
    """

    TYPE = 9

    tx: block_elements.FactoidTransaction

    def __post_init__(self):
        # TODO: type/value assertions
        super().__post_init__()

    def marshal(self) -> bytes:
        """
        Marshal the message into the following representation:
        - first byte is the message type (always 9)
        - next bytes are the marshalled Factoid Transaction object

        :return: byte representation of the message
        """
        buf = bytearray()
        buf.append(self.TYPE)
        buf.extend(self.tx.marshal())
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))
        tx = block_elements.FactoidTransaction.unmarshal(data)
        return FactoidTransaction(tx=tx)

    def to_dict(self) -> dict:
        return {"tx": self.tx.to_dict()}

    def leader_execute(self, state: Blockchain):
        pass

    def follower_execute(self, state: Blockchain):
        pass


@dataclass
class ChainCommit(Message):
    """
    A message holding a ChainCommit object.
    """

    TYPE = 5

    commit: block_elements.ChainCommit
    signature: primitives.FullSignature

    def __post_init__(self):
        # TODO: type/value assertions
        super().__post_init__()

    def marshal(self) -> bytes:
        """
        Marshal the message into the following representation:
        - first byte is the message type (always 5)
        - next bytes are the marshalled Chain Commit object
        - next 32 bytes are the public key
        - next 64 bytes are the signature

        :return: byte representation of the message
        """
        buf = bytearray()
        buf.append(self.TYPE)
        buf.extend(self.commit.marshal())
        buf.extend(self.signature.marshal())
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))

        commit_size = block_elements.ChainCommit.BITLENGTH
        commit, data = (
            block_elements.ChainCommit.unmarshal(data[:commit_size]),
            data[commit_size:],
        )

        # TODO: found in factomd code, is this actually not signed sometimes?
        if len(data) > 0:
            signature, data = primitives.FullSignature.unmarshal(data[:96]), data[96:]
        else:
            signature = primitives.FullSignature(b"", b"")

        return ChainCommit(commit=commit, signature=signature)

    def to_dict(self) -> dict:
        return {"commit": self.commit.to_dict(), "signature": self.signature.to_dict()}

    def leader_execute(self, state: Blockchain):
        pass

    def follower_execute(self, state: Blockchain):
        pass


@dataclass
class EntryCommit(Message):
    """
    A message holding a EntryCommit object.
    """

    TYPE = 6

    commit: block_elements.EntryCommit
    signature: primitives.FullSignature

    def __post_init__(self):
        # TODO: type/value assertions
        super().__post_init__()

    def marshal(self) -> bytes:
        """
        Marshal the message into the following representation:
        - first byte is the message type (always 6)
        - next bytes are the marshalled Entry Commit object
        - next 32 bytes are the public key
        - next 64 bytes are the signature

        :return: byte representation of the message
        """
        buf = bytearray()
        buf.append(self.TYPE)
        buf.extend(self.commit.marshal())
        buf.extend(self.signature.marshal())
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))

        commit_size = block_elements.EntryCommit.BITLENGTH
        commit, data = (
            block_elements.EntryCommit.unmarshal(data[:commit_size]),
            data[commit_size:],
        )

        if (
            len(data) > 0
        ):  # TODO: found in factomd code, is this actually not signed sometimes?
            signature, data = primitives.FullSignature.unmarshal(data[:96]), data[96:]
        else:
            signature = primitives.FullSignature(b"", b"")

        return EntryCommit(commit=commit, signature=signature)

    def to_dict(self) -> dict:
        return {"commit": self.commit.to_dict(), "signature": self.signature.to_dict()}

    def leader_execute(self, state: Blockchain):
        pass

    def follower_execute(self, state: Blockchain):
        pass


@dataclass
class EntryReveal(Message):
    """
    A message holding an Entry object to be revealed (can reveal a Chain as well)
    """

    TYPE = 13

    timestamp: bytes
    entry: block_elements.Entry

    def __post_init__(self):
        # TODO: type/value assertions
        super().__post_init__()

    def marshal(self) -> bytes:
        """
        Marshal the message into the following representation:
        - first byte is the message type (always 13)
        - next 6 bytes are the timestamp
        - next bytes are the marshalled Entry itself

        :return: byte representation of the message
        """
        buf = bytearray()
        buf.append(self.TYPE)
        buf.extend(self.timestamp)
        buf.extend(self.entry.marshal())
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))

        timestamp, data = data[:6], data[6:]
        entry = block_elements.Entry.unmarshal(data)
        return EntryReveal(timestamp=timestamp, entry=entry)

    def to_dict(self) -> dict:
        return {"timestamp": self.timestamp.hex(), "entry": self.entry.to_dict()}

    def leader_execute(self, state: Blockchain):
        pass

    def follower_execute(self, state: Blockchain):
        pass
