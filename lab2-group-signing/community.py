from ipv8.community import Community
from ipv8.lazy_community import lazy_wrapper
import asyncio

from payloads import (RegisterPayload, ServerResponsePayload,
                      ChallengeRequestPayload, ChallengeResponsePayload,
                      BundleSubmissionPayload, RoundResultPayload, NonceToSignPayload,
                      SignatureSubmissionPayload)

from config import (MEMBER1_PUBLIC_KEY_HEX, MEMBER2_PUBLIC_KEY_HEX,
                    MEMBER3_PUBLIC_KEY_HEX, COMMUNITY_ID_HEX,
                    SERVER_PUBLIC_KEY_HEX)

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

        self.add_message_handler(NonceToSignPayload, self.on_nonce_to_sign)

        self.add_message_handler(SignatureSubmissionPayload,
                                 self.on_signature_submission)
        # self.my_public_key = self.my_peer.public_key.key_to_bin()

        #Saving peer vars
        self.server_peer = None
        self.member1_peer = None  #DARIAN
        self.member3_peer = None  #YVES

        self.round_started = False
        self.round_signatures = [None, None, None]
        self.bundle_submitted = False
        
        self.group_id = None
        self.current_round_number = None

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

    def is_teammate_peer(self, peer) -> bool:
        peer_public_key = self.peer_public_key(peer)

        return peer_public_key in {
            MEMBER1_PUBLIC_KEY,
            MEMBER3_PUBLIC_KEY,
        }

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
                    print("=====Found Lab 2 server=====")
                    return peer

            print("Server peer not found yet.")
            await asyncio.sleep(0.25)

    async def find_teammate_peers(self):
        """
        Keep looking through discovered peers until both known teammates are found.
        """

        found_teammates = set()

        while len(found_teammates) < 2:
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

    def sign_nonce(self, nonce: bytes) -> bytes:
        """
        Sign the raw 32-byte nonce with my private IPv8 key.
        """

        return self.crypto.create_signature(self.my_peer.key, nonce)

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

        # print("Sending group registration...")

        payload = RegisterPayload(
            member1_key=MEMBER1_PUBLIC_KEY,
            member2_key=MEMBER2_PUBLIC_KEY,
            member3_key=MEMBER3_PUBLIC_KEY,
        )

        try:
            self.ez_send(self.server_peer, payload)
        except:
            print("Failed to send register message.")
            return False

        return True

    def request_challenge(self) -> bool:

        # print(f"Requesting challenge")

        payload = ChallengeRequestPayload(group_id=self.group_id)
        self.ez_send(self.server_peer, payload)

        return True

    def submit_bundle(self) -> bool:

        # print(
        #     f"Submitting signature bundle for round {self.current_round_number}..."
        # )

        payload = BundleSubmissionPayload(
            group_id=self.group_id,
            round_number=self.current_round_number,
            sig1=self.round_signatures[0],
            sig2=self.round_signatures[1],
            sig3=self.round_signatures[2],
        )

        self.ez_send(self.server_peer, payload)
        return True

    # ---------------------------------------------------------------------
    # Incoming messages from server
    # ---------------------------------------------------------------------

    @lazy_wrapper(ServerResponsePayload)
    def on_server_response(self, peer, payload: ServerResponsePayload):

        if not self.is_server_peer(peer):
            return

        # print("\nRegistration response received:")
        # print(f"success = {payload.success}")
        # print(f"group_id = {payload.group_id}")
        # print(f"message = {payload.message}")

        if payload.success:
            self.group_id = payload.group_id
            # print(f"Stored group_id: {self.group_id}")
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

        if payload.round_number != 2:
            # print("It is not my round yet, not starting round.")
            return

        if self.round_started:
            # print("Round already started. Not sending nonce to teammates again.")
            return

        self.round_started = True

        print(
            f"\nChallenge response for round {payload.round_number} received:")
        print(f"round_number = {payload.round_number}")
        print(f"nonce = {payload.nonce.hex()}")
        print(f"deadline = {payload.deadline}")

        self.current_round_number = payload.round_number

        my_signature = self.sign_nonce(payload.nonce)
        self.round_signatures[1] = my_signature

        self.send_nonce_to_teammates(payload.nonce, payload.round_number)

    @lazy_wrapper(RoundResultPayload)
    def on_round_result(self, peer, payload: RoundResultPayload):

        if not self.is_server_peer(peer):
            return

        if payload.round_number != 2:
            # print("Ignoring Round result for not yet started round 2")
            return

        print("\nRound result received:")
        print(f"success = {payload.success}")
        print(f"round_number = {payload.round_number}")
        print(f"rounds_completed = {payload.rounds_completed}")
        print(f"message = {payload.message}")


    # ---------------------------------------------------------------------
    # Internal outgoing messages to teammates
    # ---------------------------------------------------------------------

    def send_sig_to_coord(self, peer, signature, round_number) -> bool:

        # print(f"Sending signature back to coordinator")

        payload = SignatureSubmissionPayload(round_number=round_number,
                                             signature=signature)
        self.ez_send(peer, payload)

        # print(f"Sent signature for round {round_number} back to coordinator.")

        return True

    def send_nonce_to_teammates(self, nonce: bytes, round_number: int):
        
        if self.group_id is None:
            print("Cannot send nonce: group_id is missing.")
            return

        payload = NonceToSignPayload(
            nonce=nonce,
            round_number=round_number,
            group_id=self.group_id,
        )

        for teammate_peer in [self.member1_peer, self.member3_peer]:
            if teammate_peer is None:
                continue

            self.ez_send(teammate_peer, payload)

        # print(f"Sent nonce for round {round_number} to teammates.")

    # ---------------------------------------------------------------------
    # Internal incoming messages from teammates
    # ---------------------------------------------------------------------

    @lazy_wrapper(NonceToSignPayload)
    def on_nonce_to_sign(self, peer, payload: NonceToSignPayload):
        """
        """

        if not self.is_teammate_peer(peer):
            # print("Ignored NonceToSign from non-teammate peer.")
            return

        if payload.round_number == 2:
            # print("Ignored round 2 nonce to sign")
            return

        # print("\nReceived nonce to sign from teammate:")
        # print(f"nonce = {payload.nonce.hex()}")
        # print(f"round_number = {payload.round_number}")
        # print(f"group_id = {payload.group_id}")

        self.group_id = payload.group_id

        signature = self.sign_nonce(payload.nonce)

        self.send_sig_to_coord(peer, signature, payload.round_number)

    @lazy_wrapper(SignatureSubmissionPayload)
    def on_signature_submission(self, peer,
                                payload: SignatureSubmissionPayload):
        """
        """

        if not self.is_teammate_peer(peer):
            # print("Ignored signature submission from non-teammate peer.")
            return

        # print("\nReceived signature submission from teammate:")
        # print(f"round_number = {payload.round_number}")
        # print(f"signature = {payload.signature.hex()}")

        if self.peer_public_key(peer) == MEMBER1_PUBLIC_KEY:
            self.round_signatures[0] = payload.signature
            # print("=====Saved signature from Darian====")
        else:
            self.round_signatures[2] = payload.signature
            # print("=====Saved signature from Yves====")

        if all(self.round_signatures) and not self.bundle_submitted:
            self.bundle_submitted = True
            self.submit_bundle()
