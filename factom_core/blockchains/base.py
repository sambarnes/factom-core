from factom_core.blocks import DirectoryBlock, DirectoryBlockHeader


class BaseBlockchain:
    """
    The base class for all Blockchain objects
    """
    network_id = None  # type: bytes
    vms = None  # type: list

    def __init__(self) -> None:
        raise NotImplementedError("Blockchain classes must implement this method")

    def seal_minute(self) -> None:
        raise NotImplementedError("Blockchain classes must implement this method")

    def rotate_vms(self) -> None:
        raise NotImplementedError("Blockchain classes must implement this method")

    def seal_block(self) -> None:
        raise NotImplementedError("Blockchain classes must implement this method")

    #
    # Validation
    #

    def validate_block(self, block: DirectoryBlock) -> None:
        raise NotImplementedError("Blockchain classes must implement this method")

    def validate_header(self, header: DirectoryBlockHeader) -> None:
        raise NotImplementedError("Blockchain classes must implement this method")

    @classmethod
    def validate_chain(cls, root: DirectoryBlockHeader, descendants: list) -> None:
        """
        Validate that all of the descendents are valid, given that the root header is valid.
        """
        pass


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
        if not isinstance(self.vms, list) or len(self.network_id) == 0:
            raise ValueError(
                "The Blockchain class must be instantiated with a `vms` list of length > 1"
            )

    def seal_minute(self) -> None:
        """
        Finalize the current block minute, inserting minute markers where applicable.
        """
        pass

    def rotate_vms(self) -> None:
        """
        Rotate the responsibilities of the VM set (if more than one VM).
        """
        pass

    def seal_block(self) -> None:
        """
        Finalize the current block.q
        """
        pass

    #
    # Validation
    #

    def validate_block(self, block: DirectoryBlock) -> None:
        pass

    def validate_header(self, header: DirectoryBlockHeader) -> None:
        pass
