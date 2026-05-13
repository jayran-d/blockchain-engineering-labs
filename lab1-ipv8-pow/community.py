from ipv8.community import Community
from ipv8.lazy_community import lazy_wrapper

from payloads import SubmissionPayload, ServerResponsePayload

COMMUNITY_ID_HEX = "2c1cc6e35ff484f99ebdfb6108477783c0102881"

SERVER_PUBLIC_KEY_HEX = "4c69624e61434c504b3a86b23934a28d669c390e2d1fc0b0870706c4591cc0cb178bc5a811da6d87d27ef319b2638ef60cc8d119724f4c53a1ebfad919c3ac4136c501ce5c09364e0ebb"


class Lab1Community(Community):
    """
    Our custom IPv8 community for the Lab 1 assignment.

    The community_id tells IPv8 which P2P group to join.
    Peers with a different community_id are ignored.
    """

    community_id = bytes.fromhex(COMMUNITY_ID_HEX)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Register a handler for message_id = 2.
        # This lets our client receive the server response.
        self.add_message_handler(ServerResponsePayload,
                                 self.on_server_response)

        self.server_peer = None

    def find_server_peer(self):
        """
        Look through discovered peers and find the real server.

        Other classmates may also be in the same community, so we only trust
        the peer whose public key exactly matches the assignment server key.
        """

        expected_public_key = bytes.fromhex(SERVER_PUBLIC_KEY_HEX)

        peers = self.get_peers()
        print(f"Discovered {len(peers)} peer(s).")

        for peer in peers:
            try:
                actual_public_key = peer.public_key.key_to_bin()
            except Exception as error:
                print(f"Skipping peer with unreadable public key: {error}")
                continue

            print(f"Peer public key: {actual_public_key.hex()[:40]}...")

            if actual_public_key == expected_public_key:
                self.server_peer = peer
                print("Matched server public key.")
                return peer

        return None

    def send_submission(self, email: str, github_url: str, nonce: int):
        """
        Send the Proof-of-Work submission to the verified server peer.
        """

        server = self.find_server_peer()

        if server is None:
            print("Server peer not found yet.")
            return False

        print("Found server peer. Sending submission...")

        payload = SubmissionPayload(email, github_url, nonce)

        # ez_send sends an authenticated IPv8 message.
        # This is important because the server registers our public key.
        self.ez_send(server, payload)

        return True

    @lazy_wrapper(ServerResponsePayload)
    def on_server_response(self, peer, payload: ServerResponsePayload):
        """
        Called automatically when the server sends message_id = 2.
        """

        # Safety check: only accept a response from the actual server.
        expected_public_key = bytes.fromhex(SERVER_PUBLIC_KEY_HEX)
        actual_public_key = peer.public_key.key_to_bin()

        if actual_public_key != expected_public_key:
            print("Ignored response from non-server peer.")
            return

        print("Server response received:")
        print(f"success = {payload.success}")
        print(f"message = {payload.message}")
