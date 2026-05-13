from ipv8.community import Community
from ipv8.lazy_community import lazy_wrapper
import os

from payloads import (
    RegisterPayload,
    ServerResponsePayload,
    ChallengeRequestPayload,
    ChallengeResponsePayload,
    BundleSubmissionPayload,
    RoundResultPayload,
)

COMMUNITY_ID_HEX = "4c61623247726f75705369676e696e6732303236"

SERVER_PUBLIC_KEY_HEX = (
    "4c69624e61434c504b3a82e33614a342774e084af80835838d6dbdb64a537d3ddb6c1d82011a7f101553cda40cf5fa0e0fc23abd0a9c4f81322282c5b34566f6b8401f5f683031e60c96"
)


class BcECommunity(Community):
    """
    IPv8 community for Lab 2: Coordinated Group Signing.

    This class handles communication with the official Lab 2 server:
    - group registration
    - challenge requests
    - challenge responses
    - bundle submissions
    - round results

    Teammate-to-teammate coordination can be added later with custom payloads.
    """

    community_id = bytes.fromhex(COMMUNITY_ID_HEX)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Server response to RegisterPayload, message_id = 2.
        self.add_message_handler(ServerResponsePayload,
                                 self.on_server_response)

        # Server response to ChallengeRequestPayload, message_id = 4.
        self.add_message_handler(ChallengeResponsePayload,
                                 self.on_challenge_response)

        # Server response to BundleSubmissionPayload, message_id = 6.
        # Also used when a challenge request is rejected early.
        self.add_message_handler(RoundResultPayload, self.on_round_result)

        self.server_peer = None

        # These are filled after server responses.
        self.group_id = None
        self.current_nonce = None
        self.current_round_number = None
        self.deadline = None
        self.rounds_completed = 0

    # ---------------------------------------------------------------------
    # Helper methods
    # ---------------------------------------------------------------------

    def expected_server_public_key(self) -> bytes:
        """
        Return the official Lab 2 server public key as bytes.
        """
        return bytes.fromhex(SERVER_PUBLIC_KEY_HEX)

    def peer_public_key(self, peer) -> bytes:
        """
        Return an IPv8 peer's public key in the same byte format used by the lab.
        """
        return peer.public_key.key_to_bin()

    def is_server_peer(self, peer) -> bool:
        """
        Check whether a peer is the official Lab 2 server.
        """
        return self.peer_public_key(peer) == self.expected_server_public_key()

    def find_server_peer(self):
        """
        Look through discovered peers and find the real Lab 2 server.
        """

        peers = self.get_peers()
        print(f"Discovered {len(peers)} peer(s).")

        for peer in peers:
            try:
                actual_public_key = self.peer_public_key(peer)
            except Exception as error:
                print(f"Skipping peer with unreadable public key: {error}")
                continue

            print(f"Peer public key: {actual_public_key.hex()[:60]}...")

            if actual_public_key == self.expected_server_public_key():
                self.server_peer = peer
                print("Matched Lab 2 server public key.")
                return peer

        print("Server peer not found yet.")
        return None

    def get_server_peer(self):
        """
        Return the cached server peer if available.
        Otherwise, try to discover it.
        """
        if self.server_peer is not None:
            return self.server_peer

        return self.find_server_peer()

    def accept_only_server_response(self, peer) -> bool:
        """
        Safety check for incoming server messages.

        We ignore server-like messages from any peer whose public key does not
        match the official Lab 2 server key.
        """
        if not self.is_server_peer(peer):
            print("Ignored message from non-server peer.")
            return False

        return True

    # ---------------------------------------------------------------------
    # Outgoing messages to server
    # ---------------------------------------------------------------------

    def register_group(self) -> bool:
        """
        Register a group of 3 members with the Lab 2 server.

        The order of these keys becomes the canonical signature order:

        sig1 must belong to member1_key
        sig2 must belong to member2_key
        sig3 must belong to member3_key
        """

        MEMBER1_PUBLIC_KEY = "4c69624e61434c504b3adc31a700de7e0d53fc6c3cfc52e2b8122f35d74def4aaf55b9ccdf81116f5f4f7d8c15de980916c0e953a4f23423ad1ff6abb34dbae4ac3c12bfdb76c0f4e81c"  #DARIAN
        MEMBER2_PUBLIC_KEY = "4c69624e61434c504b3a70597fc8337cce9c703a98ae454aef1ba9a0e9ab61a3b84933a606d1ec44466197b54b27c07d167ddfc134d03247b8290a6013d0b4ccc07817272e846aa51e50"  #JAYRAN
        MEMBER3_PUBLIC_KEY = "4c69624e61434c504b3aea1ebe2bb45bbaef6fd358df15349cf7494ea4c3079bd09876d867e0cd339d5c341269531ea65b0f99daf123b585ebcef5c21d9e17c54d755e5cc5916c024ce4"  #YVES

        member1_key = bytes.fromhex(MEMBER1_PUBLIC_KEY)
        member2_key = bytes.fromhex(MEMBER2_PUBLIC_KEY)
        member3_key = bytes.fromhex(MEMBER3_PUBLIC_KEY)

        server = self.get_server_peer()

        if server is None:
            return False

        print("Sending group registration...")

        payload = RegisterPayload(
            member1_key=member1_key,
            member2_key=member2_key,
            member3_key=member3_key,
        )

        self.ez_send(server, payload)
        return True

    def request_challenge(self, group_id: str | None = None) -> bool:
        """
        Request the next challenge from the Lab 2 server.

        If group_id is not passed, we use self.group_id from registration.
        """

        server = self.get_server_peer()

        if server is None:
            return False

        if group_id is None:
            group_id = self.group_id

        if not group_id:
            print("Cannot request challenge: group_id is missing.")
            return False

        print(f"Requesting challenge for group_id={group_id}...")

        payload = ChallengeRequestPayload(group_id=group_id)
        self.ez_send(server, payload)

        return True

    def submit_bundle_raw(
        self,
        group_id: str,
        round_number: int,
        sig1: bytes,
        sig2: bytes,
        sig3: bytes,
    ) -> bool:
        """
        Submit an already ordered signature bundle to the server.

        Important:
        sig1, sig2, sig3 must match the original registration order.
        """

        server = self.get_server_peer()

        if server is None:
            return False

        print(f"Submitting signature bundle for round {round_number}...")

        payload = BundleSubmissionPayload(
            group_id=group_id,
            round_number=round_number,
            sig1=sig1,
            sig2=sig2,
            sig3=sig3,
        )

        self.ez_send(server, payload)
        return True

    def submit_bundle(
        self,
        round_number: int,
        signatures_by_public_key: dict[bytes, bytes],
        member_public_keys: list[bytes],
        group_id: str | None = None,
    ) -> bool:
        """
        Build and submit a bundle using the canonical member order.

        signatures_by_public_key should look like:

        {
            member1_key: member1_signature,
            member2_key: member2_signature,
            member3_key: member3_signature,
        }

        member_public_keys must be the exact registration order:

        [
            member1_key,
            member2_key,
            member3_key,
        ]
        """

        if group_id is None:
            group_id = self.group_id

        if not group_id:
            print("Cannot submit bundle: group_id is missing.")
            return False

        if len(member_public_keys) != 3:
            print(
                "Cannot submit bundle: expected exactly 3 member public keys.")
            return False

        try:
            sig1 = signatures_by_public_key[member_public_keys[0]]
            sig2 = signatures_by_public_key[member_public_keys[1]]
            sig3 = signatures_by_public_key[member_public_keys[2]]
        except KeyError as error:
            print(f"Cannot submit bundle: missing signature for key {error}.")
            return False

        return self.submit_bundle_raw(
            group_id=group_id,
            round_number=round_number,
            sig1=sig1,
            sig2=sig2,
            sig3=sig3,
        )

    # ---------------------------------------------------------------------
    # Incoming messages from server
    # ---------------------------------------------------------------------

    @lazy_wrapper(ServerResponsePayload)
    def on_server_response(self, peer, payload: ServerResponsePayload):
        """
        Called when the server replies to RegisterPayload.

        Message ID = 2.
        """

        if not self.accept_only_server_response(peer):
            return

        print("\nRegistration response received:")
        print(f"success = {payload.success}")
        print(f"group_id = {payload.group_id}")
        print(f"message = {payload.message}")

        if payload.success:
            self.group_id = payload.group_id
            print(f"Stored group_id: {self.group_id}")
        else:
            print("Group registration failed.")

    @lazy_wrapper(ChallengeResponsePayload)
    def on_challenge_response(self, peer, payload: ChallengeResponsePayload):
        """
        Called when the server sends a challenge nonce.

        Message ID = 4.
        """

        if not self.accept_only_server_response(peer):
            return

        self.current_nonce = payload.nonce
        self.current_round_number = payload.round_number
        self.deadline = payload.deadline

        print("\nChallenge response received:")
        print(f"round_number = {payload.round_number}")
        print(f"nonce = {payload.nonce.hex()}")
        print(f"deadline = {payload.deadline}")

        print("You should now sign the raw nonce bytes, not nonce.hex().")

    @lazy_wrapper(RoundResultPayload)
    def on_round_result(self, peer, payload: RoundResultPayload):
        """
        Called when the server replies to a SignatureBundle.

        Message ID = 6.

        Also called if a ChallengeRequest is rejected early.
        """

        if not self.accept_only_server_response(peer):
            return

        print("\nRound result received:")
        print(f"success = {payload.success}")
        print(f"round_number = {payload.round_number}")
        print(f"rounds_completed = {payload.rounds_completed}")
        print(f"message = {payload.message}")

        if payload.success:
            self.rounds_completed = payload.rounds_completed

            if payload.rounds_completed == 3:
                print("All 3 rounds completed.")
            else:
                print("Round accepted. Next round can start.")
        else:
            print("Round failed or request was rejected.")
