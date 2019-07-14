from hashlib import sha256


def get_merkle_root(hashes: list) -> bytes:
    merkle_tree = build_merkle_tree(hashes)
    return None if len(merkle_tree) == 0 else merkle_tree[-1]


def build_merkle_tree(hashes: list):
    if len(hashes) == 0 or len(hashes) == 1:
        return hashes

    next_level = []
    for i in range(0, len(hashes), 2):
        left = hashes[i]
        right = hashes[i + 1] if i + 1 != len(hashes) else left
        top = sha256(left + right).digest()
        next_level.append(top)

    next_iteration = build_merkle_tree(next_level)
    hashes.extend(next_iteration)
    return hashes


def calculate_keymr(header: bytes, body_mr: bytes):
    header_hash = sha256(header).digest()
    return sha256(header_hash + body_mr).digest()
