from .directory_block import DirectoryBlock
from factom_core.block_elements.admin_messages import *
from factom_core.utils import varint


class AdminBlock:

    CHAIN_ID = bytes.fromhex("000000000000000000000000000000000000000000000000000000000000000a")

    def __init__(self, back_reference_hash: bytes, height: int, header_expansion_area: bytes, messages: list):
        self.back_reference_hash = back_reference_hash
        self.height = height
        self.header_expansion_area = header_expansion_area
        self.messages = messages
        # TODO: assert they're all here
        # TODO: use kwargs for some optional metadata

    def __str__(self):
        pass

    def marshal(self):
        buf = bytearray()
        buf.extend(AdminBlock.CHAIN_ID)
        buf.extend(self.back_reference_hash)
        buf.extend(struct.pack('>I', self.height))
        buf.extend(varint.encode(len(self.header_expansion_area)))
        buf.extend(self.header_expansion_area)
        buf.extend(struct.pack('>I', len(self.messages)))
        bodybuf = bytearray()
        for message in self.messages:
            bodybuf.append(message.__class__.ADMIN_ID)
            bodybuf.extend(message.marshal())
        buf.extend(struct.pack('>I', len(bodybuf)))
        buf.extend(bodybuf)
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        """Returns a new AdminBlock object, unmarshalling given bytes according to:
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#administrative-block

        Useful for working with a single ablock out of context, pulled directly from a factomd database for instance.

        AdminBlock created will not include contextual metadata, such as timestamp
        """
        chain_id, data = raw[:32], raw[32:]
        assert chain_id == AdminBlock.CHAIN_ID
        back_reference_hash, data = data[:32], data[32:]
        height, data = struct.unpack('>I', data[:4])[0], data[4:]

        header_expansion_size, data = varint.decode(data)
        header_expansion_area, data = data[:header_expansion_size], data[header_expansion_size:]
        # TODO: unmarshal header expansion area

        message_count, data = struct.unpack('>I', data[:4])[0], data[4:]
        body_size, data = struct.unpack('>I', data[:4])[0], data[4:]
        assert body_size == len(data)

        messages = []
        for i in range(message_count):
            admin_id, data = data[0], data[1:]
            assert admin_id <= 0x0E, 'Unsupported Admin message type! ({})'.format(admin_id)
            msg = None
            if admin_id == MinuteNumber.ADMIN_ID:  # Deprecated in M2
                size = MinuteNumber.MESSAGE_SIZE
                msg_data, data = data[:size], data[size:]
                msg = MinuteNumber.unmarshal(msg_data)

            elif admin_id == DirectoryBlockSignature.ADMIN_ID:
                size = DirectoryBlockSignature.MESSAGE_SIZE
                msg_data, data = data[:size], data[size:]
                msg = DirectoryBlockSignature.unmarshal(msg_data)

            elif admin_id == MatryoshkaHashReveal.ADMIN_ID:
                size = MatryoshkaHashReveal.MESSAGE_SIZE
                msg_data, data = data[:size], data[size:]
                msg = MatryoshkaHashReveal.unmarshal(msg_data)

            elif admin_id == MatryoshkaHashAddOrReplace.ADMIN_ID:
                size = MatryoshkaHashAddOrReplace.MESSAGE_SIZE
                msg_data, data = data[:size], data[size:]
                msg = MatryoshkaHashAddOrReplace.unmarshal(msg_data)

            elif admin_id == ServerCountIncrease.ADMIN_ID:
                size = ServerCountIncrease.MESSAGE_SIZE
                msg_data, data = data[:size], data[size:]
                msg = ServerCountIncrease.unmarshal(msg_data)

            elif admin_id == AddFederatedServer.ADMIN_ID:
                size = AddFederatedServer.MESSAGE_SIZE
                msg_data, data = data[:size], data[size:]
                msg = AddFederatedServer.unmarshal(msg_data)

            elif admin_id == AddAuditServer.ADMIN_ID:
                size = AddAuditServer.MESSAGE_SIZE
                msg_data, data = data[:size], data[size:]
                msg = AddAuditServer.unmarshal(msg_data)

            elif admin_id == RemoveFederatedServer.ADMIN_ID:
                size = RemoveFederatedServer.MESSAGE_SIZE
                msg_data, data = data[:size], data[size:]
                msg = RemoveFederatedServer.unmarshal(msg_data)

            elif admin_id == AddFederatedServerSigningKey.ADMIN_ID:
                size = AddFederatedServerSigningKey.MESSAGE_SIZE
                msg_data, data = data[:size], data[size:]
                msg = AddFederatedServerSigningKey.unmarshal(msg_data)

            elif admin_id == AddFederatedServerBitcoinAnchorKey.ADMIN_ID:
                size = AddFederatedServerBitcoinAnchorKey.MESSAGE_SIZE
                msg_data, data = data[:size], data[size:]
                msg = AddFederatedServerBitcoinAnchorKey.unmarshal(msg_data)

            elif admin_id == ServerFaultHandoff.ADMIN_ID:
                msg = ServerFaultHandoff()  # No data on chain for message

            elif admin_id == CoinbaseDescriptor.ADMIN_ID:
                msg, data = CoinbaseDescriptor.unmarshal_with_remainder(data)

            elif admin_id == CoinbaseDescriptorCancel.ADMIN_ID:
                msg, data = CoinbaseDescriptorCancel.unmarshal_with_remainder(data)

            elif admin_id == AddAuthorityFactoidAddress.ADMIN_ID:
                size = AddAuthorityFactoidAddress.MESSAGE_SIZE
                msg_data, data = data[:size], data[size:]
                msg = AddAuthorityFactoidAddress.unmarshal(msg_data)

            elif admin_id == AddAuthorityEfficiency.ADMIN_ID:
                size = AddAuthorityEfficiency.MESSAGE_SIZE
                msg_data, data = data[:size], data[size:]
                msg = AddAuthorityFactoidAddress.unmarshal(msg_data)

            if msg is not None:
                messages.append(msg)

        assert len(messages) == message_count, 'Unexpected message count!'
        assert len(data) == 0, 'Extra bytes remaining!'

        return AdminBlock(
            back_reference_hash=back_reference_hash,
            height=height,
            header_expansion_area=header_expansion_area,
            messages=messages
        )

    def add_context(self, directory_block: DirectoryBlock):
        pass

    def to_dict(self):
        pass
