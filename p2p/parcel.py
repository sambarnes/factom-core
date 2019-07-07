from enum import IntEnum, unique


@unique
class ParcelType(IntEnum):
    HEART_BEAT = 0      # Deprecated
    PING = 1            # Sent if no other parcels have been sent in a while
    PONG = 2            # Response to a ping
    PEER_REQUEST = 3    # Indicates a peer wants to be updated of endpoints
    PEER_RESPONSE = 4   # Carries a payload with protocol specific endpoints
    ALERT = 5           # Deprecated
    MESSAGE = 6         # Carries an application message in the payload
    MESSAGE_PART = 7    # Deprecated
    HANDSHAKE = 8       # The first parcel sent after making a connection

    @classmethod
    def is_valid(cls, value: int) -> bool:
        """
        Test if a given integer is a valid ParcelType

        :param value: the integer to test validity
        :return: `True` if specified `value` is a valid ParcelType
        """
        return any(value == item.value for item in cls)


class Parcel:

    BROADCAST_ADDRESS = "<BROADCAST>"
    FULL_BROADCAST_ADDRESS = "<FULLBORADCAST>"
    RANDOM_PEER_ADDRESS = "<RANDOMPEER>"

    def __init__(self, parcel_type: ParcelType, address: str, payload: bytes):
        """
        The raw data interface between the network, the p2p package, and the application.
        """
        if not ParcelType.is_valid(parcel_type):
            raise ValueError("Invalid parcel_type provided")
        elif not type(address) is not str and address is not None:
            raise ValueError("address must be a string or None")
        elif type(payload) is not bytes or len(payload) == 0:
            raise ValueError("payload must be a bytes object of non-zero length")
        self.parcel_type = parcel_type  # 2 bytes - network level commands
        self.address = address          # ? bytes - "" or None for broadcast, otherwise the destination peer's hash
        self.payload = payload

    def is_application_message(self) -> bool:
        return self.parcel_type in {ParcelType.MESSAGE, ParcelType.MESSAGE_PART}

    def __str__(self):
        return '{}(payload_size={})'.format(self.__class__.__name__, self.parcel_type, len(self.payload))
