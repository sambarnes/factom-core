import struct
from dataclasses import dataclass


@dataclass
class FullSignature:
    public_key: bytes
    signature: bytes

    def __post_init__(self):
        if type(self.public_key) is not bytes or len(self.public_key) != 32:
            raise ValueError("public_key must be a bytes object of length 32")
        if type(self.signature) is not bytes or len(self.signature) != 64:
            raise ValueError("signature must be a bytes object of length 64")

    def marshal(self):
        buf = bytearray()
        buf.extend(self.public_key)
        buf.extend(self.signature)
        return buf

    @classmethod
    def unmarshal(cls, raw: bytes):
        public_key, data = raw[:32], raw[32:]
        signature, data = data[:64], data[64:]
        return FullSignature(public_key=public_key, signature=signature)

    def to_dict(self):
        return {"public_key": self.public_key.hex(), "signature": self.signature.hex()}


class FullSignatureList(list):
    def marshal(self) -> bytes:
        buf = bytearray()
        buf.extend(struct.pack(">I", len(self)))
        for signature in self:
            buf.extend(signature.marshal())
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        length, data = struct.unpack(">I", raw[:4])[0], raw[4:]
        signatures = []
        for i in range(length):
            signature, data = FullSignature.unmarshal(data[:96]), data[96:]
            signatures.append(signature)
        assert len(data) == 0, "Extra bytes remaining!"
        return FullSignatureList(signatures)
