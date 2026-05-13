from ipv8.community import Community
from ipv8.lazy_community import lazy_wrapper

from payloads import SubmissionPayload, ServerResponsePayload

COMMUNITY_ID_HEX = "4c61623247726f75705369676e696e6732303236"

SERVER_PUBLIC_KEY_HEX = "4c69624e61434c504b3a82e33614a342774e084af80835838d6dbdb64a537d3ddb6c1d82011a7f101553cda40cf5fa0e0fc23abd0a9c4f81322282c5b34566f6b8401f5f683031e60c96"

#Blockchain Engineering Community
class BcECommunity(Community):
    """
    Our custom IPv8 community for the Lab assignments.

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
