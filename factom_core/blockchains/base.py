

class BaseBlockchain:
    """
    The base class for all Blockchain objects
    """
    network_id = None  # type: bytes

    def __init__(self) -> None:
        raise NotImplementedError("Blockchain classes must implement this method")


class Blockchain(BaseBlockchain):
    """
    A Blockchain is a combination of VM classes.  Each VM is associated
    with a range of chains.  The Blockchain class acts as a wrapper around these other
    VM classes, delegating operations to the appropriate VM depending on the
    current block / minute number.
    """
    def __init__(self) -> None:
        if not isinstance(self.network_id, bytes) or len(self.network_id) != 4:
            raise ValueError(
                "The Blockchain class must be instantiated with a `network_id` bytes object of length 4"
            )
