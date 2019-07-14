# factom-core

A python library for working with the primitives of the Factom blockchain.

Kinda ugly, very alpha. Development is mainly being done to support a light node implementation, however, the data structures should be portable enough to use in other application contexts as well.

## Development

For fetching and working with items from a factomd database, see: `tests/db/test_mainnet_db.py`

For running a p2p listener that gets forwarded all received messages from your factomd node, see: `p2p/utils/p2p_listener.py`
