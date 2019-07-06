import struct
from factom_core.blocks import (
    DirectoryBlock,
    AdminBlock,
    FactoidBlock,
    EntryCreditBlock,
    EntryBlock
)
from factom_core.block_elements import Entry
from factom_core.messages import Message


class SignatureList(list):  # TODO: should this go in a separate module or package? primitives?
    def marshal(self) -> bytes:
        buf = bytearray()
        buf.extend(struct.pack('>I', len(self)))
        for signature in self:
            buf.extend(signature.get('public_key'))
            buf.extend(signature.get('signature'))
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        length, data = struct.unpack('>I', raw[:4])[0], raw[4:]
        signatures = []
        for i in range(length):
            public_key, data = data[:32], data[32:]
            signature, data = data[:64], data[64:]
            signatures.append({
                'public_key': public_key,
                'signature': signature,
            })
        assert len(data) == 0, 'Extra bytes remaining!'
        return SignatureList(signatures)


class DirectoryBlockState(Message):
    """
    A message to communicate a Directory Block State
    """

    TYPE = 20

    def __init__(self, timestamp: bytes, directory_block: DirectoryBlock, admin_block: AdminBlock,
                 factoid_block: FactoidBlock, entry_credit_block: EntryCreditBlock, entry_blocks: list, entries: list,
                 signatures: SignatureList):
        # TODO: type/value assertions
        self.timestamp = timestamp
        self.directory_block = directory_block
        self.admin_block = admin_block
        self.factoid_block = factoid_block
        self.entry_credit_block = entry_credit_block
        self.entry_blocks = entry_blocks
        self.entries = entries  # TODO: can we just remove the entry field? It's no longer passed over the network
        self.signatures = signatures
        self.is_p2p = True
        super().__init__()

    def marshal(self) -> bytes:
        """
        Marshal the message into the following representation:
        - first byte is the message type (always 20)
        - next bytes are the marshalled Directory Block
        - next bytes are the marshalled Admin Block
        - next bytes are the marshalled Factoid Block
        - next bytes are the marshalled Entry Credit Block
        - next 4 bytes are the number of Entry Blocks following
        - next bytes are the aforementioned marshalled Entry Blocks
        - next 4 bytes are the number of Entries following (NOTE: always 0 now)
        - next bytes are all of the Entries, marshalled as:
            - 4 bytes size of the Entry
            - marshalled Entry itself
        - next bytes are the number of signatures
        - next bytes are all of the signatures marhsalled as:
            - 64 bytes signature
            - 32 byte public key

        :return: byte representation of the message
        """
        buf = bytearray()
        buf.append(self.TYPE)
        buf.extend(self.timestamp)
        buf.extend(self.directory_block.marshal())
        buf.extend(self.admin_block.marshal())
        buf.extend(self.factoid_block.marshal())
        buf.extend(self.entry_credit_block.marshal())
        buf.extend(struct.pack('>I', len(self.entry_blocks)))
        for entry_block in self.entry_blocks:
            buf.extend(entry_block.marshal())
        buf.extend(struct.pack('>I', len(self.entries)))
        for entry in self.entries:
            buf.extend(struct.pack('>I', len(entry)))
            buf.extend(entry.marshal())
        buf.extend(self.signatures.marshal())
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw:  bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))

        timestamp, data = data[:6], data[6:]
        directory_block, data = DirectoryBlock.unmarshal_with_remainder(data)
        admin_block, data = AdminBlock.unmarshal_with_remainder(data)
        factoid_block, data = FactoidBlock.unmarshal_with_remainder(data)
        entry_credit_block, data = EntryCreditBlock.unmarshal_with_remainder(data)

        entry_block_count, data = struct.unpack('>I', data[:4])[0], data[4:]
        entry_blocks = []
        for i in range(entry_block_count):
            entry_block, data = EntryBlock.unmarshal_with_remainder(data)
            entry_blocks.append(entry_block)

        entry_count, data = struct.unpack('>I', data[:4])[0], data[4:]
        entries = []
        for i in range(entry_count):
            entry_size, data = struct.unpack('>I', data[:4])[0], data[4:]
            entry, data = Entry.unmarshal(data[:entry_size]), data[entry_size:]
            entries.append(entry)

        signatures = SignatureList.unmarshal(data)

        return DirectoryBlockState(
            timestamp=timestamp,
            directory_block=directory_block,
            admin_block=admin_block,
            factoid_block=factoid_block,
            entry_credit_block=entry_credit_block,
            entry_blocks=entry_blocks,
            entries=entries,
            signatures=signatures,
        )

    def __str__(self):
        return '{}()'.format(self.__class__.__name__)


class DirectoryBlockStateRequest(Message):
    """
    A request for missing DBState objects.
    """

    TYPE = 21

    def __init__(self, timestamp: bytes, block_height_start: int, block_height_end: int):
        # TODO: type/value assertions
        self.timestamp = timestamp
        self.block_height_start = block_height_start
        self.block_height_end = block_height_end
        self.is_p2p = True
        super().__init__()

    def marshal(self) -> bytes:
        """
        Marshal the message into the following representation:
        - first byte is the message type (always 21)
        - next 6 bytes are the timestamp
        - next 4 bytes are the block height start
        - next 4 bytes are the block height end

        :return: byte representation of the message
        """
        buf = bytearray()
        buf.append(self.TYPE)
        buf.extend(self.timestamp)
        buf.extend(struct.pack('>I', self.block_height_start))
        buf.extend(struct.pack('>I', self.block_height_end))
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw:  bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))

        timestamp, data = data[:6], data[6:]
        block_height_start, data = struct.unpack('>I', data[:4])[0], data[4:]
        block_height_end, data = struct.unpack('>I', data[:4])[0], data[4:]

        return DirectoryBlockStateRequest(
            timestamp=timestamp,
            block_height_start=block_height_start,
            block_height_end=block_height_end,
        )

    def __str__(self):

        return '{}()'.format(self.__class__.__name__)


class BlockRequest(Message):
    """
    An unimplemented message. I assume for requesting single blocks of any type.
    """

    TYPE = 14

    def __init__(self, timestamp: bytes):
        # TODO: type/value assertions
        self.timestamp = timestamp
        super().__init__()

    def marshal(self) -> bytes:
        """
        Marshal the message into the following representation:
        - first byte is the message type (always 14)
        - next 6 bytes are a timestamp

        :return: byte representation of the message
        """
        buf = bytearray()
        buf.append(self.TYPE)
        buf.extend(self.timestamp)
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw:  bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))
        timestamp, data = data[:6], data[6:]
        assert len(data) == 0, 'Extra bytes remaining!'
        return BlockRequest(timestamp=timestamp)
