from ipv8.community import Community
from ipv8.lazy_community import lazy_wrapper
import asyncio

from payloads import (
    RegisterPayload,
    ServerResponsePayload,
    ChallengeRequestPayload,
    ChallengeResponsePayload,
    BundleSubmissionPayload,
    RoundResultPayload,
)

from config import (MEMBER1_PUBLIC_KEY_HEX, MEMBER2_PUBLIC_KEY_HEX,
                    MEMBER3_PUBLIC_KEY_HEX, COMMUNITY_ID_HEX,
                    SERVER_PUBLIC_KEY_HEX, GROUP_ID)

MEMBER1_PUBLIC_KEY = bytes.fromhex(MEMBER1_PUBLIC_KEY_HEX)  #Darian
MEMBER2_PUBLIC_KEY = bytes.fromhex(MEMBER2_PUBLIC_KEY_HEX)  #Jayran
MEMBER3_PUBLIC_KEY = bytes.fromhex(MEMBER3_PUBLIC_KEY_HEX)  #Yves

TEAMMATE_COUNT = 2


class BcECommunity(Community):
    """
    IPv8 community for Lab 2: Coordinated Group Signing.
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

        #Saving peer vars
        self.server_peer = None
        self.member1_peer = None  #DARIAN
        self.member3_peer = None  #YVES

        self.group_id = GROUP_ID

        # These are filled after server responses.
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

    async def find_server_peer(self):
        """
        Keep looking through discovered peers until the real Lab 2 server is found.
        """

        while self.server_peer is None:
            peers = self.get_peers()
            print(f"Discovered {len(peers)} peer(s).")

            for peer in peers:
                try:
                    actual_public_key = self.peer_public_key(peer)
                except Exception as error:
                    print(f"Skipping peer with unreadable public key: {error}")
                    continue

                if actual_public_key == self.expected_server_public_key():
                    self.server_peer = peer
                    print("Matched Lab 2 server public key.")
                    return peer

            print("Server peer not found yet.")
            await asyncio.sleep(0.25)

    async def find_teammate_peers(self):
        """
        Keep looking through discovered peers until both known teammates are found.
        """

        found_teammates = set()

        while len(found_teammates) < TEAMMATE_COUNT:
            peers = self.get_peers()
            print(f"Discovered {len(peers)} peer(s).")

            for peer in peers:
                try:
                    peer_public_key_hex = self.peer_public_key(peer).hex()
                except Exception as error:
                    print(f"Skipping peer with unreadable public key: {error}")
                    continue

                if (peer_public_key_hex == MEMBER1_PUBLIC_KEY_HEX) and (
                        peer_public_key_hex not in found_teammates):

                    print(f"===========Found Darian===========")
                    self.member1_peer = peer
                    found_teammates.add(peer_public_key_hex)
                    continue

                if (peer_public_key_hex == MEMBER3_PUBLIC_KEY_HEX) and (
                        peer_public_key_hex not in found_teammates):

                    print(f"===========Found Yves===========")
                    self.member3_peer = peer
                    found_teammates.add(peer_public_key_hex)
                    continue

                await asyncio.sleep(0.25)

        print("All teammate peers found.")
        return found_teammates

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

        print("Sending group registration...")

        payload = RegisterPayload(
            member1_key=MEMBER1_PUBLIC_KEY,
            member2_key=MEMBER2_PUBLIC_KEY,
            member3_key=MEMBER3_PUBLIC_KEY,
        )

        self.ez_send(self.server_peer, payload)
        return True

    def request_challenge(self) -> bool:
        """
        Request the next challenge from the Lab 2 server.

        If group_id is not passed, we use self.group_id from registration.
        """

        print(f"Requesting challenge")

        payload = ChallengeRequestPayload(group_id=self.group_id)
        self.ez_send(self.server_peer, payload)

        return True

    def submit_bundle(
        self,
        sig1: bytes,
        sig2: bytes,
        sig3: bytes,
    ) -> bool:
        """
        Submit an already ordered signature bundle to the server.

        Important:
        sig1, sig2, sig3 must match the original registration order.
        """

        print(
            f"Submitting signature bundle for round {self.current_round_number}..."
        )

        payload = BundleSubmissionPayload(
            group_id=self.group_id,
            round_number=self.current_round_number,
            sig1=sig1,
            sig2=sig2,
            sig3=sig3,
        )

        self.ez_send(self.server_peer, payload)
        return True

    # ---------------------------------------------------------------------
    # Incoming messages from server
    # ---------------------------------------------------------------------

    @lazy_wrapper(ServerResponsePayload)
    def on_server_response(self, peer, payload: ServerResponsePayload):
        """
        Called when the server replies to RegisterPayload.

        Message ID = 2.
        """

        if not self.is_server_peer(peer):
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

        if not self.is_server_peer(peer):
            return

        self.current_nonce = payload.nonce
        self.current_round_number = payload.round_number
        self.deadline = payload.deadline

        print("\nChallenge response received:")
        print(f"round_number = {payload.round_number}")
        print(f"nonce = {payload.nonce.hex()}")
        print(f"deadline = {payload.deadline}")

        # print("We should now sign the raw nonce bytes, not nonce.hex().")

    @lazy_wrapper(RoundResultPayload)
    def on_round_result(self, peer, payload: RoundResultPayload):
        """
        Called when the server replies to a SignatureBundle.

        Message ID = 6.

        Also called if a ChallengeRequest is rejected early.
        """

        if not self.is_server_peer(peer):
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
