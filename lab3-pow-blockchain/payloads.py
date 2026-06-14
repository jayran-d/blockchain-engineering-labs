# from ipv8.messaging.lazy_payload import VariablePayload, vp_compile
from dataclasses import dataclass

from ipv8.messaging.payload_dataclass import DataClassPayloadWID

@dataclass
class SubmitTransactionPayload(DataClassPayloadWID):

    msg_id = 1

    format_list = ["varlenH", "varlenH", "q", "varlenH"]
    names = ["sender_key", "data", "timestamp", "signature"]

    sender_key: bytes
    data: bytes
    timestamp: int
    signature: bytes

