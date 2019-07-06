import factom_core.block_elements as block_elements
from factom_core.messages import Message


class FactoidTransaction(Message):
    """
    A message holding a FactoidTransaction object.
    """

    TYPE = 9

    def __init__(self, tx: block_elements.FactoidTransaction):
        # TODO: type/value assertions
        self.tx = tx
        super().__init__()

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
    def unmarshal(cls, raw:  bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))
        tx = block_elements.FactoidTransaction.unmarshal(data)
        return FactoidTransaction(tx=tx)


class ChainCommit(Message):
    """
    A message holding a ChainCommit object.
    """

    TYPE = 5

    def __init__(self, commit: block_elements.ChainCommit, public_key: bytes, signature: bytes):
        # TODO: type/value assertions
        self.commit = commit
        self.public_key = public_key
        self.signature = signature
        super().__init__()

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
        buf.extend(self.public_key)
        buf.extend(self.signature)
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw:  bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))

        commit_size = block_elements.ChainCommit.BITLENGTH
        commit, data = block_elements.ChainCommit.unmarshal(data[:commit_size]), data[commit_size:]

        if len(data) > 0:  # TODO: found in factomd code, is this actually not signed sometimes?
            public_key, data = data[:32], data[32:]
            signature, data = data[:64], data[64:]
        else:
            signature, public_key = b'', b''

        return ChainCommit(
            commit=commit,
            public_key=public_key,
            signature=signature,
        )


class EntryCommit(Message):
    """
    A message holding a EntryCommit object.
    """

    TYPE = 6

    def __init__(self, commit: block_elements.EntryCommit, public_key: bytes, signature: bytes):
        # TODO: type/value assertions
        self.commit = commit
        self.public_key = public_key
        self.signature = signature
        super().__init__()

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
        buf.extend(self.public_key)
        buf.extend(self.signature)
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw:  bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))

        commit_size = block_elements.EntryCommit.BITLENGTH
        commit, data = block_elements.EntryCommit.unmarshal(data[:commit_size]), data[commit_size:]

        if len(data) > 0:  # TODO: found in factomd code, is this actually not signed sometimes?
            public_key, data = data[:32], data[32:]
            signature, data = data[:64], data[64:]
        else:
            public_key, signature = b'', b''

        return EntryCommit(
            commit=commit,
            public_key=public_key,
            signature=signature,
        )


class EntryReveal(Message):
    """
    A message holding an Entry object to be revealed (can reveal a Chain as well)
    """

    TYPE = 13

    def __init__(self, timestamp: bytes, entry: block_elements.Entry):
        self.timestamp = timestamp
        self.entry = entry
        super().__init__()

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
    def unmarshal(cls, raw:  bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))

        timestamp, data = data[:6], data[6:]
        entry = block_elements.Entry.unmarshal(data)
        return EntryReveal(
            timestamp=timestamp,
            entry=entry,
        )
