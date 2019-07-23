from dataclasses import dataclass, field

import factom_core.messages as messages
from factom_core.blockchains import Blockchain


@dataclass
class Message:
    """
    A message for VM execution.
    """

    TYPE = None  # type: int
    is_local: bool = field(init=False, default=False)

    # __slots__ = [
    #     "origin",  # set and examined on each server (not marshalled)
    #     "network_origin",  # hash of the network peer/connection where the message is from
    #     "is_p2p",  # (not marshalled)
    #     "is_local_only",  # if true, don't broadcast. we can skip verification too since it was locally sourced
    #     "is_from_network",  # if true, we got this message from the network (not marshalled)
    #     "is_full_broadcast",  # used for messages with no missing message support e.g. election related messages
    #     "is_resendable",
    #     "resend_limit",
    #     "leader_chain_id",
    #     "message_hash",  # cache of the hash of a message TODO: needed?
    #     "repeat_hash",  # cache of the hash of a message TODO: needed?
    #     "vm_index",  # index of the VM responsible for this message
    #     "vm_hash",  # basis for selecting the vm index
    #     "minute",
    #     "time_to_resend",  # milliseconds
    #     "time_to_expire",  # milliseconds
    #     "is_stalled",
    #     "is_invalid",
    #     "is_sig_valid",
    # ]

    def __post_init__(self):
        if self.TYPE is None:
            raise ValueError("A Message class must be instantiated with a `TYPE`")

    def leader_execute(self, state: Blockchain):
        pass

    def follower_execute(self, state: Blockchain):
        pass

    def marshal(self) -> bytes:
        pass

    @classmethod
    def unmarshal(cls, raw: bytes):
        pass

    def to_dict(self) -> dict:
        return {}


def unmarshal_message(raw: bytes):
    msg_type = raw[0]
    if msg_type == messages.Ack.TYPE:
        return messages.Ack.unmarshal(raw)

    elif msg_type == messages.ChainCommit.TYPE:
        return messages.ChainCommit.unmarshal(raw)

    elif msg_type == messages.EntryCommit.TYPE:
        return messages.EntryCommit.unmarshal(raw)

    elif msg_type == messages.EntryReveal.TYPE:
        return messages.EntryReveal.unmarshal(raw)

    elif msg_type == messages.FactoidTransaction.TYPE:
        return messages.FactoidTransaction.unmarshal(raw)

    elif msg_type == messages.EndOfMinute.TYPE:
        return messages.EndOfMinute.unmarshal(raw)

    elif msg_type == messages.DirectoryBlockSignature.TYPE:
        return messages.DirectoryBlockSignature.unmarshal(raw)

    elif msg_type == messages.DirectoryBlockStateRequest.TYPE:
        return messages.DirectoryBlockStateRequest.unmarshal(raw)

    elif msg_type == messages.DirectoryBlockState.TYPE:
        return messages.DirectoryBlockState.unmarshal(raw)

    elif msg_type == messages.MissingDataRequest.TYPE:
        return messages.MissingDataRequest.unmarshal(raw)

    elif msg_type == messages.MissingDataResponse.TYPE:
        return messages.MissingDataResponse.unmarshal(raw)

    elif msg_type == messages.Heartbeat.TYPE:
        return messages.Heartbeat.unmarshal(raw)

    elif msg_type == messages.AddServer.TYPE:
        return messages.AddServer.unmarshal(raw)

    elif msg_type == messages.ChangeServerKey.TYPE:
        return messages.ChangeServerKey.unmarshal(raw)

    elif msg_type == messages.RemoveServer.TYPE:
        return messages.RemoveServer.unmarshal(raw)

    elif msg_type == messages.BlockRequest.TYPE:
        return messages.BlockRequest.unmarshal(raw)

    elif msg_type == messages.MissingMessageRequest.TYPE:
        return messages.MissingMessageRequest.unmarshal(raw)

    elif msg_type == messages.MissingMessageResponse.TYPE:
        return messages.MissingMessageResponse.unmarshal(raw)

    else:
        raise ValueError("Bad message type")
