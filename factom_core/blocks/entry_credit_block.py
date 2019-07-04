import struct
from .directory_block import DirectoryBlock
from factom_core.block_elements.balance_increase import BalanceIncrease
from factom_core.block_elements.chain_commit import ChainCommit
from factom_core.block_elements.entry_commit import EntryCommit
from factom_core.utils import varint


class EntryCreditBlock:

    CHAIN_ID = bytes.fromhex("000000000000000000000000000000000000000000000000000000000000000c")

    def __init__(self, body_hash: bytes, prev_header_hash: bytes, prev_full_hash: bytes, height: int,
                 header_expansion_area: bytes, objects: list, **kwargs):
        # Required fields. Must be in every EntryBlock
        self.body_hash = body_hash
        self.prev_header_hash = prev_header_hash
        self.prev_full_hash = prev_full_hash
        self.height = height
        self.header_expansion_area = header_expansion_area
        self.objects = objects
        # TODO: assert they're all here
        # TODO: use kwargs for some optional metadata


    def marshal(self):
        """Marshals the directory block according to the byte-level representation shown at
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#entry-credit-block

        Data returned does not include contextual metadata, such as timestamp or the pointer to the
        next entry-credit block.
        """
        buf = bytearray()
        buf.extend(EntryCreditBlock.CHAIN_ID)
        buf.extend(self.body_hash)
        buf.extend(self.prev_header_hash)
        buf.extend(self.prev_full_hash)
        buf.extend(struct.pack('>I', self.height))
        buf.extend(varint.encode(len(self.header_expansion_area)))
        buf.extend(self.header_expansion_area)
        object_count = 0
        body_buf = bytearray()
        for minute, objects in self.objects.items():
            object_count += len(objects) + 1
            for o in objects:
                if isinstance(object, int):
                    body_buf.append(0x00)
                    body_buf.append(o)
                elif isinstance(o, ChainCommit):
                    body_buf.extend(ChainCommit.ECID)
                    body_buf.extend(o.marshal())
                elif isinstance(o, EntryCommit):
                    body_buf.extend(EntryCommit.ECID)
                    body_buf.extend(o.marshal())
                elif isinstance(o, BalanceIncrease):
                    body_buf.extend(BalanceIncrease.ECID)
                    body_buf.extend(o.marshal())
            body_buf.append(0x01)
            body_buf.append(minute)

        buf.extend(struct.pack('>Q', object_count))
        buf.extend(struct.pack('>Q', len(body_buf)))
        buf.extend(body_buf)
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        """Returns a new EntryCreditBlock object, unmarshalling given bytes according to:
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#entry-credit-block

        Useful for working with a single ecblock out of context, pulled directly from a factomd database for instance.

        EntryCreditBlock created will not include contextual metadata, such as timestamp or the pointer to the
        next entry-credit block.
        """
        chain_id, data = raw[:32], raw[32:]
        assert chain_id == EntryCreditBlock.CHAIN_ID
        body_hash, data = data[:32], data[32:]
        prev_header_hash, data = data[:32], data[32:]
        prev_full_hash, data = data[:32], data[32:]
        height, data = struct.unpack('>I', data[:4])[0], data[4:]

        header_expansion_size, data = varint.decode(data)
        header_expansion_area, data = data[:header_expansion_size], data[header_expansion_size:]

        object_count, data = struct.unpack('>Q', data[:8])[0], data[8:]
        body_size, data = struct.unpack('>Q', data[:8])[0], data[8:]

        objects = {}  # map of minute --> objects array
        current_minute_objects = []
        for i in range(object_count):
            ecid, data = data[:1], data[1:]
            if ecid == b'\x00':
                server_index, data = data[:1], data[1:]
                server_index = int.from_bytes(server_index, byteorder='big')
                current_minute_objects.append(server_index)
            elif ecid == b'\x01':
                minute, data = data[:1], data[1:]
                minute = int.from_bytes(minute, byteorder='big')
                objects[minute] = current_minute_objects
                current_minute_objects = []
            elif ecid == ChainCommit.ECID:
                chain_commit, data = data[:ChainCommit.BITLENGTH], data[ChainCommit.BITLENGTH:]
                chain_commit = ChainCommit.unmarshal(chain_commit)
                current_minute_objects.append(chain_commit)
            elif ecid == EntryCommit.ECID:
                entry_commit, data = data[:EntryCommit.BITLENGTH], data[EntryCommit.BITLENGTH:]
                entry_commit = EntryCommit.unmarshal(entry_commit)
                current_minute_objects.append(entry_commit)
            elif ecid == BalanceIncrease.ECID:
                balance_increace, data = BalanceIncrease.unmarshal_with_remainder(data)
                current_minute_objects.append(balance_increace)
            else:
                raise ValueError

        assert len(data) == 0, 'Extra bytes remaining!'

        return EntryCreditBlock(
            body_hash=body_hash,
            prev_header_hash=prev_header_hash,
            prev_full_hash=prev_full_hash,
            height=height,
            header_expansion_area=header_expansion_area,
            objects=objects
        )

    def add_context(self, directory_block: DirectoryBlock):
        pass

    def to_dict(self):
        pass

    def __str__(self):
        return '{}(height={})'.format(self.__class__.__name__, self.height)

