from hashlib import sha256
from .entry import Entry


class Chain:
    def __init__(self, chain_id: bytes, first_entry: Entry, **kwargs):
        self.chain_id = chain_id
        self.first_entry = first_entry
        # TODO: do we need these safety checks?
        assert self.chain_id == self._calculate_chain_id(), 'chain_id does not match external_ids'
        assert isinstance(self.first_entry, Entry), 'first_entry must be of type models.Entry'
        # TODO: use kwargs for some optional metadata

    def _calculate_chain_id(self):
        """Returns the chain id in bytes. The algorithm used is shown at:
        https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#chainid
        """
        # Chain ID = SHA256(SHA256(ExtIDs[0]) + SHA256(ExtIDs[0]) + ... + SHA256(ExtIDs[N]))
        chain_id = sha256()
        for x in self.first_entry.external_ids:
            chain_id.update(sha256(x).digest())
        return chain_id.digest()

    def to_dict(self):
        return {
            'chain_id': self.chain_id,
            'first_entry': self.first_entry
        }

    def __str__(self):
        return '{}(chain_id={})'.format(
            self.__class__.__name__, self.chain_id.hex())
