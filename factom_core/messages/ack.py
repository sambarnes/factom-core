import struct
from dataclasses import dataclass

import factom_core.primitives as primitives
from factom_core.blockchains import Blockchain
from factom_core.messages import Message
from factom_core.utils import varint


@dataclass
class Ack(Message):
    """
    A acknowledgement for a given message
    """

    TYPE = 1

    vm_index: int
    timestamp: bytes
    salt: bytes
    salt_number: int
    message_hash: bytes
    full_message_hash: bytes
    leader_chain_id: bytes
    height: int
    process_list_height: int
    minute: int
    serial_hash: bytes
    data_area: bytes
    signature: primitives.FullSignature

    def __post_init__(self):
        # TODO: type/value assertions
        self.is_p2p = True
        super().__post_init__()

    def marshal(self) -> bytes:
        """
        Marshal the message into the following representation:
        - first byte is the message type (always 1)
        - next byte is the vm index
        - next 6 bytes are the timestamp
        - next 8 bytes are the salt
        - next 4 bytes are the salt number
        - next 32 bytes are the message hash being acknowledged
        - next 32 bytes are the full message hash
        - next 32 bytes are the leader chain id
        - next 4 bytes are the directory block height
        - next 4 bytes are the process list height TODO: is this actually the process list height?
        - next byte is the minute
        - next 32 bytes are the serial hash
        - next varint bytes are the data area size
        - next X bytes are the data area:
            - TODO: unmarshal the data area in Ack message
        - next 32 bytes are the public key
        - next 64 bytes are the signature

        :return: byte representation of the message
        """
        buf = bytearray()
        buf.append(self.TYPE)
        buf.append(self.vm_index)
        buf.extend(self.timestamp)
        buf.extend(self.salt)
        buf.extend(struct.pack(">I", self.salt_number))
        buf.extend(self.message_hash)
        buf.extend(self.full_message_hash)
        buf.extend(self.leader_chain_id)
        buf.extend(struct.pack(">I", self.height))
        buf.extend(struct.pack(">I", self.process_list_height))
        buf.append(self.minute)
        buf.extend(self.serial_hash)
        buf.extend(varint.encode(len(self.data_area)))
        buf.extend(self.data_area)
        buf.extend(self.signature.marshal())
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))

        vm_index, data = data[0], data[1:]
        timestamp, data = data[:6], data[6:]
        salt, data = data[:8], data[8:]
        salt_number, data = struct.unpack(">I", data[:4])[0], data[4:]
        message_hash, data = data[:32], data[32:]
        full_message_hash, data = data[:32], data[32:]
        leader_chain_id, data = data[:32], data[32:]
        height, data = struct.unpack(">I", data[:4])[0], data[4:]
        process_list_height, data = struct.unpack(">I", data[:4])[0], data[4:]
        minute, data = data[0], data[1:]
        serial_hash, data = data[:32], data[32:]
        data_area_size, data = varint.decode(data)
        data_area, data = data[:data_area_size], data[data_area_size:]
        # TODO: unmarshal the data area in Ack message

        signature, data = primitives.FullSignature.unmarshal(data[:96]), data[96:]

        return Ack(
            vm_index=vm_index,
            timestamp=timestamp,
            salt=salt,
            salt_number=salt_number,
            message_hash=message_hash,
            full_message_hash=full_message_hash,
            leader_chain_id=leader_chain_id,
            height=height,
            process_list_height=process_list_height,
            minute=minute,
            serial_hash=serial_hash,
            data_area=data_area,
            signature=signature,
        )

    def to_dict(self):
        return {
            "vm_index": self.vm_index,
            "timestamp": self.timestamp.hex(),
            "salt": self.salt.hex(),
            "salt_number": self.salt_number,
            "message_hash": self.message_hash.hex(),
            "full_message_hash": self.full_message_hash.hex(),
            "leader_chain_id": self.leader_chain_id.hex(),
            "height": self.height,
            "process_list_height": self.process_list_height,
            "minute": self.minute,
            "serial_hash": self.serial_hash.hex(),
            "data_area": self.data_area.hex(),
            "signature": self.signature.to_dict(),
        }

    def leader_execute(self, state: Blockchain):
        self.follower_execute(state)

    def follower_execute(self, state: Blockchain):
        pass
