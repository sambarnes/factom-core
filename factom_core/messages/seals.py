import struct
from dataclasses import dataclass

import factom_core.primitives as primitives
from factom_core.blockchains import Blockchain
from factom_core.blocks import DirectoryBlockHeader
from factom_core.messages import Message


@dataclass
class EndOfMinute(Message):
    """
    A message for leaders to send out signifying the end of the current block minute
    """

    TYPE = 0
    timestamp: bytes
    chain_id: bytes
    minute: int
    vm_index: int
    factoid_vm: int
    height: int
    system_height: int
    system_hash: bytes
    b: int
    signature: primitives.FullSignature

    def __post_init__(self):
        # TODO: type/value assertions
        self.is_p2p = True
        super().__post_init__()

    def marshal(self) -> bytes:
        """
        Marshal the message into the following representation:
        - first byte is the message type (always 10)
        - next 6 bytes are the timestamp
        - next 32 bytes are the server's identity chain id
        - next byte is the minute number
        - next byte is the vm index
        - next byte is the factoid vm index
        - next 4 bytes are the directory block height
        - next 4 bytes are the system height
        - next 32 bytes are the system hash
        - TODO: next byte is unknown.. but if its greater than 0, then the pubkey + signature must be next
        - next 32 bytes are the signing public key
        - next 64 bytes are the signature

        :return: byte representation of the message
        """
        buf = bytearray()
        buf.append(self.TYPE)
        buf.extend(self.timestamp)
        buf.extend(self.chain_id)
        buf.append(self.vm_index)
        buf.extend(struct.pack(">I", self.height))
        buf.extend(struct.pack(">I", self.system_height))
        buf.append(self.b)
        if self.b > 0:
            buf.extend(self.signature.marshal())
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))

        timestamp, data = data[:6], data[6:]
        chain_id, data = data[:32], data[32:]
        minute, data = data[0], data[1:]
        vm_index, data = data[0], data[1:]
        factoid_vm, data = data[0], data[1:]
        height, data = struct.unpack(">I", data[:4])[0], data[4:]
        system_height, data = struct.unpack(">I", data[:4])[0], data[4:]
        system_hash, data = data[:32], data[32:]
        b, data = data[0], data[1:]
        if b > 0:
            signature, data = primitives.FullSignature.unmarshal(data[:96]), data[96:]
        else:
            signature = primitives.FullSignature(bytes(32), bytes(64))

        return EndOfMinute(
            timestamp=timestamp,
            chain_id=chain_id,
            minute=minute,
            vm_index=vm_index,
            factoid_vm=factoid_vm,
            height=height,
            system_height=system_height,
            system_hash=system_hash,
            b=b,
            signature=signature,
        )

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.hex(),
            "chain_id": self.chain_id.hex(),
            "minute": self.minute,
            "vm_index": self.vm_index,
            "factoid_vm": self.factoid_vm,
            "height": self.height,
            "system_height": self.system_height,
            "system_hash": self.system_hash.hex(),
            "b": self.b,
            "signature": self.signature.to_dict(),
        }

    def leader_execute(self, state: Blockchain):
        pass

    def follower_execute(self, state: Blockchain):
        pass


@dataclass
class DirectoryBlockSignature(Message):
    """
    A message for leaders to send out at the end of a block. Signs the header of the last built block.
    """

    TYPE = 7

    timestamp: bytes
    system_height: int
    system_hash: bytes
    height: int
    vm_index: int
    header: DirectoryBlockHeader
    chain_id: bytes
    header_signature: primitives.FullSignature  # over just dblock header, goes in the admin block
    signature: primitives.FullSignature  # over the message

    def __post_init__(self):
        # TODO: type/value assertions
        self.is_p2p = True
        super().__post_init__()

    def marshal(self) -> bytes:
        """
        Marshal the message into the following representation:
        - first byte is the message type (always 7)
        - next 6 bytes are the timestamp
        - next 4 bytes are the system height
        - next 32 bytes are the system hash
        - next 4 bytes are the directory block height
        - next byte is the vm index
        - next bytes are the marshalled directory block header
        - next 32 bytes are the server's identity chain id
        - next 32 bytes are the header signing public key (actual dbsig, goes in next adminblock)
        - next 64 bytes are the header signature (actual dbsig, goes in next adminblock)
        - next 32 bytes are the signing public key
        - next 64 bytes are the signature

        :return: byte representation of the message
        """
        buf = bytearray()
        buf.append(self.TYPE)
        buf.extend(self.timestamp)
        buf.extend(struct.pack(">I", self.system_height))
        buf.extend(self.system_hash)
        buf.extend(struct.pack(">I", self.height))
        buf.append(self.vm_index)
        buf.extend(self.header.marshal())
        buf.extend(self.chain_id)
        buf.extend(self.header_signature.marshal())
        buf.extend(self.signature.marshal())
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))

        timestamp, data = data[:6], data[6:]
        system_height, data = struct.unpack(">I", data[:4])[0], data[4:]
        system_hash, data = data[:32], data[32:]
        height, data = struct.unpack(">I", data[:4])[0], data[4:]
        vm_index, data = data[0], data[1:]
        header_data, data = (
            data[: DirectoryBlockHeader.LENGTH],
            data[DirectoryBlockHeader.LENGTH :],
        )
        header = DirectoryBlockHeader.unmarshal(header_data)
        chain_id, data = data[:32], data[32:]

        header_signature, data = (
            primitives.FullSignature.unmarshal(data[:96]),
            data[96:],
        )
        signature, data = primitives.FullSignature.unmarshal(data[:96]), data[96:]

        return DirectoryBlockSignature(
            timestamp=timestamp,
            system_height=system_height,
            system_hash=system_hash,
            height=height,
            vm_index=vm_index,
            header=header,
            chain_id=chain_id,
            header_signature=header_signature,
            signature=signature,
        )

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.hex(),
            "system_height": self.system_height,
            "system_hash": self.system_hash.hex(),
            "height": self.height,
            "vm_index": self.vm_index,
            "header": self.header.__str__(),  # TODO: header to_dict() functions
            "chain_id": self.chain_id.hex(),
            "header_signature": self.header_signature.to_dict(),
            "signature": self.signature.to_dict(),
        }

    def leader_execute(self, state: Blockchain):
        pass

    def follower_execute(self, state: Blockchain):
        pass
