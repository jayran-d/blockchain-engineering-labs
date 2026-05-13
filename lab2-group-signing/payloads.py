from dataclasses import dataclass

from ipv8.messaging.payload_dataclass import DataClassPayloadWID


@dataclass
class SubmissionPayload(DataClassPayloadWID):
    """
    Message sent from our client to the server.

    message_id = 1

    Required wire format:
    - email: varlenHutf8
    - github_url: varlenHutf8
    - nonce: q
    """

    msg_id = 1

    format_list = ["varlenHutf8", "varlenHutf8", "q"]
    names = ["email", "github_url", "nonce"]

    # Fields must match names/format_list order, typed as plain Python types
    email: str
    github_url: str
    nonce: int


@dataclass
class ServerResponsePayload(DataClassPayloadWID):
    """
    Message sent from the server back to our client.

    msg_id = 2

    Required wire format:
    - success: ?
    - message: varlenHutf8
    """
    msg_id = 2

    format_list = ["?", "varlenHutf8"]
    names = ["success", "message"]

    success: bool
    message: str
