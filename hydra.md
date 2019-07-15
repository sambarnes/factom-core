# Light Node

Project currently named hydra since it has one primary head (directory blockchain) and many secondary heads (admin, factoid, entry-credit, and entry blockchains). If any of the secondary heads get chopped off, the node can continue to operate and provide proofs for the data it does choose to store.

### Status

There is still a lot of logic needed to be built out in the factom-core library, so this is going to be just the skeleton of a project for a while.

Features:
- RPC server for all block types and entries
- RPC client commands from the cli
- Database cli utility to navigate an offline factomd database

### Usage

Ensure the file is executable:

```
$ chmod +x hydra.py
$ ./hydra.py
Usage: hydra.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  get-admin-block
  get-directory-block
  get-entry
  get-entry-block
  get-entry-credit-block
  get-factoid-block
  run                     Main entry point for the node
```


### Run the node

Not much for now, just a RPC server wrapping a local factomd database.

```
$ ./hydra.py run


   _               _           
  | |__  _   _  __| |_ __ __ _ 
  | '_ \| | | |/ _` | '__/ _` |
  | | | | |_| | (_| | | | (_| |
  |_| |_|\__, |\__,_|_|  \__,_|
         |___/                 


Starting Hacky P2P Server...
Bottle v0.12.17 server starting up (using WSGIRefServer())...
Listening on http://localhost:8001/
Hit Ctrl-C to quit.

Starting API Server...
Bottle v0.12.17 server starting up (using WSGIRefServer())...
Listening on http://localhost:8000/
Hit Ctrl-C to quit.

Running node...
```

### Commands to assess the RPC server

Note: don't have this pointing at the database of your *running* factomd node

```
$ ./hydra.py get-directory-block 5 | jq

{
  "keymr": "980ab6d50d9fad574ad4df6dba06a8c02b1c67288ee5beab3fbfde2723f73ef6",
  "network_id": "fa92e5a2",
  "body_mr": "a4d356b711229da3ad9eb20d6c7d5b386ae43031b46df4054fc4588a9859c694",
  "prev_keymr": "d6cf048e6bb80e5c0a7ef5c87948f5ab67dbf593c3d384fc3826f3c66c49d659",
  "prev_full_hash": "2d4be4c20d19c48e910aa05a5f465160d7bf2fb1a4c2ad3695cf40f656f73674",
  "height": 5,
  "admin_block_lookup_hash": "e4ea68c72c9c08808f6a36f5ce95134ccb51f2102aa2cb053cc4009326f2cb3a",
  "entry_credit_block_header_hash": "80fbf1d5d71b28f17dc2c483737f622f8fe8925e23f328a77f1aee3d62cc7cd4",
  "factoid_block_keymr": "751dbaa27e68ec8948547dfea86eb5462ee2a4bec5689143340c88e4eaf0b7f6",
  "entry_blocks": [
    {
      "chain_id": "df3ade9eec4b08d5379cc64270c30ea7315d8a8a1a69efe2b98a60ecdd69e604",
      "keymr": "ae54b982faed02f6ab70d519b89ed2dc3184f4ea0ef38a93f584f2a4dff036e0"
    }
  ]
}

```

### Read from offline factomd databases

Use the `--connection-type db` flag or `-c db` for short.

```
$ ./hydra.py  get-entry-credit-block --connection-type db 25 | jq

{
  "body_hash": "abf2330803379fba925aaa8a2a1bacd85437663e3b546b6511fb6c0f3337a003",
  "prev_header_hash": "9641c5576410c7dba1afcc53f18a551c1636616d72caf211a14e0ffd75703c3e",
  "prev_full_hash": "26c3fefebf91e999f599b9a2a0efb13f70a875d60ad7b2b219192d730b7bd163",
  "height": 25,
  "expansion_area": "",
  "object_count": 14,
  "body_size": 433,
  "objects": {
    "1": [
      0
    ],
    "2": [],
    "3": [
      {
        "timestamp": "014f8b5cdd3c",
        "entry_hash": "c480b681b113118876e2540b1f9791af555dc2cd9b5806451305167816281710",
        "ec_spent": 1,
        "ec_public_key": "17ef7a21d1a616d65e6b73f3c6a7ad5c49340a6c2592872020ec60767ff00d7d",
        "signature": "168645e75e1071241b375fe79d55186aa2b7b6fae3f5711f026c7258882d0c59bff96e66b477b11b8fb51717cfcb357ba081929e515d96821ed8d1f72c78e703"
      },
      {
        "timestamp": "014f8b5cdd60",
        "entry_hash": "c92715fe2262b22b1b6fad0f4fc81ff7ccf5f9d633fb6815db414ec023719a72",
        "ec_spent": 1,
        "ec_public_key": "17ef7a21d1a616d65e6b73f3c6a7ad5c49340a6c2592872020ec60767ff00d7d",
        "signature": "6bb87e6899993cdfffe41e9c5aa326a9a9466e40fbccd85e5359ace8e0e3ac2750106cb61995a72e946237b5ce8ff1e31fa5549f5685ec7a47c89ddbbad3d003"
      },
      {
        "timestamp": "014f8b5cdd66",
        "entry_hash": "c49b069dbc664c2f247b812160c4a902826483df2b47c27dfd2a95c4281dda79",
        "ec_spent": 1,
        "ec_public_key": "17ef7a21d1a616d65e6b73f3c6a7ad5c49340a6c2592872020ec60767ff00d7d",
        "signature": "59d3292ed2dead1cfc36e4fbd0f2b7d7dfba3938855206e1318488d8d73e25624f8b540803b4703011753dae92f4c326a56e4a1d7d58f26eb9f058f9e773ed06"
      }
    ],
    "4": [],
    "5": [],
    "6": [],
    "7": [],
    "8": [],
    "9": [],
    "10": []
  }
}
```
