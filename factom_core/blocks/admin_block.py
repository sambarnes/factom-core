import hashlib
from dataclasses import dataclass, field
from typing import List

from factom_core.block_elements.admin_messages import *
from factom_core.utils import varint
from .directory_block import DirectoryBlock


@dataclass
class AdminBlockHeader:

    CHAIN_ID = bytes.fromhex(
        "000000000000000000000000000000000000000000000000000000000000000a"
    )

    back_reference_hash: bytes
    height: int
    expansion_area: bytes
    message_count: int
    body_size: int

    def __post_init__(self):
        # TODO: value assertions
        pass

    def marshal(self) -> bytes:
        buf = bytearray()
        buf.extend(AdminBlockHeader.CHAIN_ID)
        buf.extend(self.back_reference_hash)
        buf.extend(struct.pack(">I", self.height))
        buf.extend(varint.encode(len(self.expansion_area)))
        buf.extend(self.expansion_area)
        buf.extend(struct.pack(">I", self.message_count))
        buf.extend(struct.pack(">I", self.body_size))
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        h, data = AdminBlockHeader.unmarshal_with_remainder(raw)
        assert len(data) == 0, "Extra bytes remaining!"
        return h

    @classmethod
    def unmarshal_with_remainder(cls, raw: bytes):
        chain_id, data = raw[:32], raw[32:]
        assert chain_id == AdminBlockHeader.CHAIN_ID
        back_reference_hash, data = data[:32], data[32:]
        height, data = struct.unpack(">I", data[:4])[0], data[4:]

        expansion_size, data = varint.decode(data)
        expansion_area, data = data[:expansion_size], data[expansion_size:]
        # TODO: unmarshal header expansion area

        message_count, data = struct.unpack(">I", data[:4])[0], data[4:]
        body_size, data = struct.unpack(">I", data[:4])[0], data[4:]
        return (
            AdminBlockHeader(
                back_reference_hash=back_reference_hash,
                height=height,
                expansion_area=expansion_area,
                message_count=message_count,
                body_size=body_size,
            ),
            data,
        )


@dataclass
class AdminBlockBody:

    messages: List[AdminMessage] = field(default_factory=list)

    def __post_init__(self):
        # TODO: value assertions
        pass

    def marshal(self) -> bytes:
        buf = bytearray()
        for message in self.messages:
            if type(message) is int:
                buf.append(message)
                continue
            buf.append(message.__class__.ADMIN_ID)
            buf.extend(message.marshal())
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes, message_count: int):
        body, data = cls.unmarshal_with_remainder(raw, message_count)
        assert len(data) == 0, "Extra bytes remaining!"
        return body

    @classmethod
    def unmarshal_with_remainder(cls, raw: bytes, message_count: int):
        data = raw
        messages = []
        for i in range(message_count):
            admin_id, data = data[0], data[1:]
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

            elif admin_id <= 0x0E:
                msg = admin_id
                print(f"Unsupported admin message type {admin_id} found")

            if msg is not None:
                messages.append(msg)

        assert len(messages) == message_count, "Unexpected message count"

        return AdminBlockBody(messages=messages), data

    def construct_header(
        self, back_reference_hash: bytes, height: int
    ) -> AdminBlockHeader:
        """
        Seals the admin block by constructing and returning its header
        """
        return AdminBlockHeader(
            back_reference_hash=back_reference_hash,
            height=height,
            expansion_area=b"",
            message_count=len(self.messages),
            body_size=len(self.marshal()),
        )


@dataclass
class AdminBlock:

    header: AdminBlockHeader
    body: AdminBlockBody

    _cached_lookup_hash: bytes = None
    _cached_back_reference_hash: bytes = None

    def __post_init__(self):
        # TODO: value assertions
        pass

    @property
    def lookup_hash(self):
        if self._cached_lookup_hash is not None:
            return self._cached_lookup_hash
        self._cached_lookup_hash = hashlib.sha256(self.marshal()).digest()
        return self._cached_lookup_hash

    @property
    def back_reference_hash(self):
        if self._cached_back_reference_hash is not None:
            return self._cached_back_reference_hash
        self._cached_back_reference_hash = hashlib.sha512(self.marshal()).digest()[:256]
        return self._cached_back_reference_hash

    def marshal(self) -> bytes:
        buf = bytearray()
        buf.extend(self.header.marshal())
        buf.extend(self.body.marshal())
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        """Returns a new AdminBlock object, unmarshalling given bytes according to:
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#administrative-block

        Useful for working with a single ablock out of context, pulled directly from a factomd database for instance.

        AdminBlock created will not include contextual metadata, such as timestamp
        """
        block, data = cls.unmarshal_with_remainder(raw)
        assert len(data) == 0, "Extra bytes remaining!"
        return block

    @classmethod
    def unmarshal_with_remainder(cls, raw: bytes):
        header, data = AdminBlockHeader.unmarshal_with_remainder(raw)

        messages = []
        for i in range(header.message_count):
            admin_id, data = data[0], data[1:]
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

            elif admin_id <= 0x0E:
                msg = admin_id
                print(
                    "Unsupported admin message type {} found at Admin Block {}".format(
                        admin_id, header.height
                    )
                )

            if msg is not None:
                messages.append(msg)

        assert (
            len(messages) == header.message_count
        ), "Unexpected message count at Admin Block {}".format(header.height)

        body = AdminBlockBody(messages=messages)
        return AdminBlock(header=header, body=body), data

    def add_context(self, directory_block: DirectoryBlock):
        pass

    def to_dict(self):
        return {
            "lookup_hash": self.lookup_hash.hex(),
            "back_reference_hash": self.header.back_reference_hash.hex(),
            "height": self.header.height,
            "expansion_area": self.header.expansion_area.hex(),
            "message_count": self.header.message_count,
            "body_size": self.header.body_size,
            "messages": [m.to_dict() for m in self.body.messages],
        }

    def __str__(self):
        return "{}(height={}, hash={})".format(
            self.__class__.__name__, self.header.height, self.lookup_hash.hex()
        )
