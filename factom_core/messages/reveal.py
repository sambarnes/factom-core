from factom_core.block_elements import Entry
from factom_core.messages import Message


class EntryReveal(Message):
    """
    A message holding an Entry object to be revealed (can reveal a Chain as well)
    """

    TYPE = 13

    def __init__(self, timestamp: bytes, entry: Entry):
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
        entry = Entry.unmarshal(data)
        return EntryReveal(
            timestamp=timestamp,
            entry=entry,
        )
