from dataclasses import dataclass

from ipv8.messaging.payload_dataclass import DataClassPayloadWID


@dataclass
class RegisterPayload(DataClassPayloadWID):
    """
    Message sent from our client to the server.
    """

    msg_id = 1

    format_list = ["varlenH", "varlenH", "varlenH"]
    names = ["member1_key", "member2_key", "member3_key"]

    member1_key: bytes
    member2_key: bytes
    member3_key: bytes


@dataclass
class ServerResponsePayload(DataClassPayloadWID):
    """
    Message sent from the server back to our client after registering
    """
    msg_id = 2

    format_list = ["?", "varlenHutf8", "varlenHutf8"]
    names = ["success", "group_id", "message"]

    success: bool
    group_id: str
    message: str


@dataclass
class ChallengeRequestPayload(DataClassPayloadWID):
    """
    We send this to request a challenge
    """
    msg_id = 3

    format_list = ["varlenHutf8"]
    names = ["group_id"]

    group_id: str


@dataclass
class ChallengeResponsePayload(DataClassPayloadWID):
    """
    The server dends this back as a response to the challenge request
    """
    msg_id = 4

    format_list = ["varlenH", "q", "d"]
    names = ["nonce", "round_number", "deadline"]

    nonce: bytes
    round_number: int
    deadline: float


@dataclass
class BundleSubmissionPayload(DataClassPayloadWID):
    """
    """
    msg_id = 5

    format_list = ["varlenHutf8", "q", "varlenH", "varlenH", "varlenH"]
    names = ["group_id", "round_number", "sig1", "sig2", "sig3"]

    group_id: str
    round_number: int
    sig1: bytes
    sig2: bytes
    sig3: bytes


@dataclass
class RoundResultPayload(DataClassPayloadWID):
    """
    """
    msg_id = 6

    format_list = ["?", "q", "q", "varlenHutf8"]
    names = ["success", "round_number", "rounds_completed", "message"]

    success: bool
    round_number: int
    rounds_completed: int
    message: str


@dataclass
class NonceToSignPayload(DataClassPayloadWID):
    msg_id = 7
    format_list = ["varlenH", "q", "varlenHutf8"]
    names = ["nonce", "round_number", "group_id"]

    nonce: bytes
    round_number: int
    group_id: str


@dataclass
class SignatureSubmissionPayload(DataClassPayloadWID):
    msg_id = 8
    format_list = ["q", "varlenH"]
    names = ["round_number", "signature"]

    round_number: int
    signature: bytes
