from dataclasses import dataclass

from ipv8.messaging.payload_dataclass import DataClassPayloadWID


@dataclass
class RegisterBlockchainPayload(DataClassPayloadWID):

    msg_id = 1

    format_list = ["varlenHutf8", "varlenH"]
    names = ["group_id", "community_id"]

    group_id: str
    community_id: bytes


@dataclass
class RegisterResponsePayload(DataClassPayloadWID):

    msg_id = 2

    format_list = ["?", "varlenHutf8"]
    names = ["success", "message"]

    success: bool
    message: str
