import hashlib
from dataclasses import dataclass

import factom_core.primitives as primitives
from factom_core.utils import varint


@dataclass
class FactoidTransaction:

    timestamp: bytes
    inputs: list
    outputs: list
    ec_purchases: list
    rcds: primitives.FullSignatureList

    def __post_init__(self):
        # TODO: assert they're all here
        pass

    def is_coinbase(self):
        # TODO: Coinbase outputs be zero too right? Just matters that everything else is definitely zero
        return (
            len(self.inputs) == 0
            and len(self.ec_purchases) == 0
            and len(self.rcds) == 0
        )

    @property
    def hash(self):
        return hashlib.sha256(self.marshal()).digest()

    def marshal(self):
        """Marshals the FactoidTransaction according to the byte-level representation shown at
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#factoid-transaction
        """
        buf = bytearray()
        buf.extend(self.marshal_for_signature())
        for rcd in self.rcds:
            buf.append(0x01)
            buf.extend(rcd.marshal())
        return bytes(buf)

    def marshal_for_signature(self):
        """Marshals the transaction's header and partial body, in order to be signed by a key"""
        buf = bytearray()
        buf.append(0x02)
        buf.extend(self.timestamp)
        buf.append(len(self.inputs))
        buf.append(len(self.outputs))
        buf.append(len(self.ec_purchases))
        for i in self.inputs:
            value = i.get("value")
            fct_address = i.get("fct_address")
            buf.extend(varint.encode(value) + fct_address)
        for o in self.outputs:
            value = o.get("value")
            fct_address = o.get("fct_address")
            buf.extend(varint.encode(value) + fct_address)
        for purchase in self.ec_purchases:
            value = purchase.get("value")
            ec_public_key = purchase.get("ec_public_key")
            buf.extend(varint.encode(value) + ec_public_key)
        return bytes(buf)

    @classmethod
    def unmarshal(cls, raw: bytes):
        """Returns a new FactoidTransaction object, unmarshalling given bytes according to:
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#factoid-transaction
        """
        obj, data = FactoidTransaction.unmarshal_with_remainder(raw)
        assert len(data) == 0, "Extra bytes remaining!"
        return obj

    @classmethod
    def unmarshal_with_remainder(cls, raw: bytes):
        """Returns a new FactoidTransaction object, unmarshalling given bytes according to:
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#factoid-transaction

        Because FactoidTransaction is variable length, it is useful to pass a "stream" of bytes to be unmarshalled.
        This way, we don't have to know the size in advance. Just return the remainder bytes for the caller to use
        elsewhere.
        """
        data = raw[1:]  # skip single byte version, probably just 0x02 anyways
        timestamp, data = data[:6], data[6:]
        input_count, data = ord(data[:1]), data[1:]
        output_count, data = ord(data[:1]), data[1:]
        ec_purchase_count, data = ord(data[:1]), data[1:]

        inputs = []
        for i in range(input_count):
            value, data = varint.decode(data)
            fct_address, data = data[:32], data[32:]
            inputs.append({"value": value, "fct_address": fct_address})

        outputs = []
        for i in range(output_count):
            value, data = varint.decode(data)
            fct_address, data = data[:32], data[32:]
            outputs.append({"value": value, "fct_address": fct_address})

        ec_purchases = []
        for i in range(ec_purchase_count):
            value, data = varint.decode(data)
            ec_public_key, data = data[:32], data[32:]
            ec_purchases.append({"value": value, "ec_public_key": ec_public_key})

        rcds = primitives.FullSignatureList()
        for i in range(input_count):
            data = data[1:]  # skip 1 byte version number, always 0x01 for now
            signature, data = primitives.FullSignature.unmarshal(data[:96]), data[96:]
            rcds.append(signature)

        return (
            FactoidTransaction(
                timestamp=timestamp,
                inputs=inputs,
                outputs=outputs,
                ec_purchases=ec_purchases,
                rcds=rcds,
            ),
            data,
        )

    def to_dict(self):
        return {
            "timestamp": self.timestamp.hex(),
            "inputs": [
                {"value": r.get("value"), "fct_address": r.get("fct_address").hex()}
                for r in self.inputs
            ],
            "outputs": [
                {"value": r.get("value"), "fct_address": r.get("fct_address").hex()}
                for r in self.outputs
            ],
            "ec_purchases": [
                {"value": r.get("value"), "ec_public_key": r.get("ec_public_key").hex()}
                for r in self.ec_purchases
            ],
            "rcds": [r.to_dict() for r in self.rcds],
        }

    def __str__(self):
        # TODO: convert timestamp to readable
        return "{}(timestamp={}, inputs={}, outputs={}, ec_purchases={})".format(
            self.__class__.__name__,
            self.timestamp,
            len(self.inputs),
            len(self.outputs),
            len(self.ec_purchases),
        )
