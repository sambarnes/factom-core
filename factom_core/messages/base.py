from dataclasses import dataclass


@dataclass
class Message:
    """
    A message for VM execution.
    """
    TYPE = None  # type: int

    __slots__ = [
        'origin',  # set and examined on each server (not marshalled)
        'network_origin',  # hash of the network peer/connection where the message is from
        'is_p2p',  # (not marshalled)
        'is_local_only',  # if true, don't broadcast. we can skip verification too since it was locally sourced
        'is_from_network',  # if true, we got this message from the network (not marshalled)
        'is_full_broadcast',  # used for messages with no missing message support e.g. election related messages

        'is_resendable',
        'resend_limit',

        'leader_chain_id',
        'message_hash',  # cache of the hash of a message TODO: needed?
        'repeat_hash',  # cache of the hash of a message TODO: needed?
        'vm_index',  # index of the VM responsible for this message
        'vm_hash',  # basis for selecting the vm index
        'minute',
        'time_to_resend',  # milliseconds
        'time_to_expire',  # milliseconds

        'is_stalled',
        'is_invalid',
        'is_sig_valid',
    ]

    def __post_init__(self):
        if self.TYPE is None:
            raise ValueError("A Message class must be instantiated with a `TYPE`")

    def leader_execute(self):
        pass

    def follower_execute(self):
        pass

    def marshal(self) -> bytes:
        pass

    @classmethod
    def unmarshal(cls, raw:  bytes):
        pass
