import struct
from dataclasses import dataclass
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
    public_key: bytes
    signature: bytes

    def __post_init__(self):
        # TODO: type/value assertions
        self.is_p2p = True
        super().__init__()

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
        buf.extend(struct.pack('>I', self.salt_number))
        buf.extend(self.message_hash)
        buf.extend(self.full_message_hash)
        buf.extend(self.leader_chain_id)
        buf.extend(struct.pack('>I', self.height))
        buf.extend(struct.pack('>I', self.process_list_height))
        buf.append(self.minute)
        buf.extend(self.serial_hash)
        buf.extend(varint.encode(len(self.data_area)))
        buf.extend(self.data_area)
        buf.extend(self.public_key)
        buf.extend(self.signature)
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw:  bytes):
        msg_type, data = raw[0], raw[1:]
        if msg_type != cls.TYPE:
            raise ValueError("Invalid message type ({})".format(msg_type))

        vm_index, data = data[0], data[1:]
        timestamp, data = data[:6], data[6:]
        salt, data = data[:8], data[8:]
        salt_number, data = struct.unpack('>I', data[:4])[0], data[4:]
        message_hash, data = data[:32], data[32:]
        full_message_hash, data = data[:32], data[32:]
        leader_chain_id, data = data[:32], data[32:]
        height, data = struct.unpack('>I', data[:4])[0], data[4:]
        process_list_height, data = struct.unpack('>I', data[:4])[0], data[4:]
        minute, data = data[0], data[1:]
        serial_hash, data = data[:32], data[32:]
        data_area_size, data = varint.decode(data)
        data_area, data = data[:data_area_size], data[data_area_size:]
        # TODO: unmarshal the data area in Ack message

        public_key, data = data[:32], data[32:]
        signature, data = data[:64], data[64:]

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
            public_key=public_key,
            signature=signature,
        )
