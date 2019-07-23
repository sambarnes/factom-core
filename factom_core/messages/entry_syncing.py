from dataclasses import dataclass

from factom_core.block_elements import Entry
from factom_core.blockchains import Blockchain
from factom_core.blocks import EntryBlock
from factom_core.messages import Message


@dataclass
class MissingDataRequest(Message):
    """
    A request for an entry or entry block. Used when entry syncing.
    """

    TYPE = 17

    timestamp: bytes
    request_hash: bytes

    def __post_init__(self):
        # TODO: type/value assertions
        self.is_p2p = True
        super().__post_init__()

    def marshal(self) -> bytes:
        """
        Marshal the message into the following representation:
        - first byte is the message type (always 17)
        - next 6 bytes are the timestamp
        - next 32 bytes are the entry hash or entry block keymr being requested

        :return: byte representation of the message
        """
        buf = bytearray()
        buf.append(self.TYPE)
        buf.extend(self.timestamp)
        buf.extend(self.request_hash)
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))

        timestamp, data = data[:6], data[6:]
        request_hash, data = data[:32], data[32:]

        return MissingDataRequest(timestamp=timestamp, request_hash=request_hash)

    def to_dict(self):
        return {"timestamp": self.timestamp.hex(), "request_hash": self.request_hash}

    def __str__(self):
        return "{}(hash={})".format(self.__class__.__name__, self.request_hash)

    def leader_execute(self, state: Blockchain):
        self.follower_execute(state)

    def follower_execute(self, state: Blockchain):
        pass


@dataclass
class MissingDataResponse(Message):
    """
    A response to a MissingDataRequest, including the Entry or Entry Block requested.
    """

    TYPE = 18

    requested_object: object

    def __post_init__(self):
        if type(self.requested_object) not in {Entry, EntryBlock}:
            raise ValueError("requested_object must be an Entry or Entry Block")
        self.is_p2p = True
        super().__post_init__()

    def marshal(self) -> bytes:
        """
        Marshal the message into the following representation:
        - first byte is the message type (always 18)
        - second byte is the object type: 0 for Entry, 1 for Entry Block
        - remaining bytes are the marshalled Entry or Entry Block that was requested

        :return: byte representation of the message
        """
        buf = bytearray()
        buf.append(self.TYPE)
        buf.append(0 if isinstance(self.requested_object, Entry) else 1)
        buf.extend(self.requested_object.marshal())
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))

        object_type, data = data[0], data[1:]
        if object_type == 0:  # Entry
            requested_object = Entry.unmarshal(data)
        elif object_type == 1:  # Entry Block
            requested_object = EntryBlock.unmarshal(data)
        else:
            raise ValueError("Invalid object type ({})".format(object_type))

        return MissingDataResponse(requested_object=requested_object)

    def to_dict(self):
        assert type(self.requested_object) in {Entry, EntryBlock}
        return {"requested_object": self.requested_object.to_dict()}

    def __str__(self):
        h = (
            self.requested_object.entry_hash
            if isinstance(self.requested_object, Entry)
            else self.requested_object.keymr
        )
        return f"{self.__class__.__name__}(type={self.requested_object.__class__.__name__}, hash={h})"

    def leader_execute(self, state: Blockchain):
        self.follower_execute(state)

    def follower_execute(self, state: Blockchain):
        pass
