from ipv8.community import Community
from ipv8.lazy_community import lazy_wrapper
import asyncio

from .payloads import RegisterBlockchainPayload, RegisterResponsePayload

from config import REGISTER_COMMUNITY_ID_HEX, REGISTER_SERVER_PUBLIC_KEY_HEX, BLOCKCHAIN_COMMUNITY_ID_HEX


class Lab3RegistrationCommunity(Community):

    community_id = bytes.fromhex(REGISTER_COMMUNITY_ID_HEX)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        
        self.add_message_handler(RegisterResponsePayload,
                                 self.on_register_response)

        self.server_peer = None

        self.group_id = "d8c9d397bea2ee37"

        self.blockchain_community_id = bytes.fromhex(BLOCKCHAIN_COMMUNITY_ID_HEX)

    def peer_public_key(self, peer) -> bytes:
        """
        Return an IPv8 peer's public key in the same byte format used by the lab.
        """
        return peer.public_key.key_to_bin()

    def is_server_peer(self, peer) -> bool:
        """
        Check whether a peer is the official Lab 3 server.
        """
        return self.peer_public_key(peer) == self.expected_server_public_key()

    def expected_server_public_key(self) -> bytes:
        """
        Return the official Lab 3 server public key as bytes.
        """
        return bytes.fromhex(REGISTER_SERVER_PUBLIC_KEY_HEX)

    async def find_server_peer(self):
        """
        Keep looking through discovered peers until the real Lab 3 server is found.
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
                    print("=====Found Lab 3 server=====")
                    return peer

            print("Server peer not found yet.")
            await asyncio.sleep(0.25)

    def register_blockchain(self) -> bool:

        payload = RegisterBlockchainPayload(
            group_id=self.group_id, community_id=self.blockchain_community_id)

        try:
            self.ez_send(self.server_peer, payload)
        except Exception as e:
            print(f"Failed to send register message. Error: {e}\n")
            raise

    @lazy_wrapper(RegisterResponsePayload)
    def on_register_response(self, peer, payload: RegisterResponsePayload):

        if not self.is_server_peer(peer):
            return

        print("\nRegistration response received:")
        print(f"success = {payload.success}")
        print(f"message = {payload.message}")
