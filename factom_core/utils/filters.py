def is_needed_for_syncing(h: bytes):
    identity_prefix = b"\x88\x88\x88"
    exchange_rate_prefix = b"\x11\x11\x11"
    return h.startswith(identity_prefix) or h.startswith(exchange_rate_prefix)
