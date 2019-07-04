from factom_core.blocks import DirectoryBlock, DirectoryBlockHeader


class BaseVM:
    block = None  # type: DirectoryBlock

    def __init__(self, header: DirectoryBlockHeader) -> None:
        pass

    @property
    def header(self) -> DirectoryBlockHeader:
        pass

    @property
    def block(self) -> DirectoryBlock:
        pass


class VM(BaseVM):
    _block = None

    def __init__(self, header: DirectoryBlockHeader) -> None:
        self._initial_header = header

    @property
    def header(self) -> DirectoryBlockHeader:
        if self._block is None:
            return self._initial_header
        else:
            return self._block.header

    @property
    def block(self) -> DirectoryBlock:
        # if self._block is None:
        #     self._block = DirectoryBlock.from_header(header=self._initial_header, chaindb=self.chaindb)
        return self._block
