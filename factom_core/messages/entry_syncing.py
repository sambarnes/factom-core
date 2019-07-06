from factom_core.block_elements import Entry
from factom_core.blocks import EntryBlock
from factom_core.messages import Message


class MissingDataRequest(Message):
    """
    A request for an entry or entry block. Used when entry syncing.
    """

    TYPE = 17

    def __init__(self, timestamp: bytes, request_hash: bytes):
        # TODO: type/value assertions
        self.timestamp = timestamp
        self.request_hash = request_hash
        self.is_p2p = True
        super().__init__()

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
    def unmarshal(cls, raw:  bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))

        timestamp, data = data[:6], data[6:]
        request_hash, data = data[:32], data[32:]

        return MissingDataRequest(
            timestamp=timestamp,
            request_hash=request_hash,
        )

    def __str__(self):
        return '{}(hash={})'.format(self.__class__.__name__, self.request_hash)


class MissingDataResponse(Message):
    """
    A response to a MissingDataRequest, including the Entry or Entry Block requested.
    """
    TYPE = 18

    def __init__(self, requested_object):
        # TODO: type/value assertions
        self.requested_object = requested_object
        self.is_p2p = True
        super().__init__()

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
    def unmarshal(cls, raw:  bytes):
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

        return MissingDataResponse(
            requested_object=requested_object
        )

    def __str__(self):
        is_entry = isinstance(self.requested_object, Entry)
        object_type = "Entry" if is_entry else "Entry Block"
        h = self.requested_object.entry_hash if is_entry else self.requested_object.keymr
        return '{}(type={}, hash={})'.format(self.__class__.__name__, object_type, h)
