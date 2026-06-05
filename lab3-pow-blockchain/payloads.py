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


@dataclass
class SubmitTransactionResponsePayload(DataClassPayloadWID):

    msg_id = 2

    format_list = ["?", "varlenH", "varlenHutf8"]
    names = ["success", "tx_hash", "message"]

    success: bool
    tx_hash: bytes
    message: str


@dataclass
class GetChainHeightPayload(DataClassPayloadWID):

    msg_id = 3

    format_list = ["q"]
    names = ["request_id"]

    request_id: int


@dataclass
class ChainHeightResponsePayload(DataClassPayloadWID):

    msg_id = 4

    format_list = ["q", "q", "varlenH"]
    names = ["request_id", "height", "tip_hash"]

    request_id: int
    height: int
    tip_hash: bytes


@dataclass
class GetBlockPayload(DataClassPayloadWID):

    msg_id = 5

    format_list = ["q"]
    names = ["height"]

    height: int


@dataclass
class BlockResponsePayload(DataClassPayloadWID):

    msg_id = 6

    format_list = [
        "q", "varlenH", "varlenH", "q", "q", "q", "varlenH", "varlenH"
    ]
    names = [
        "height", "prev_hash", "txs_hash", "timestamp", "difficulty", "nonce",
        "block_hash", "tx_hashes"
    ]

    height: int
    prev_hash: bytes
    txs_hash: bytes
    timestamp: int
    difficulty: int
    nonce: int
    block_hash: bytes
    tx_hashes: bytes
