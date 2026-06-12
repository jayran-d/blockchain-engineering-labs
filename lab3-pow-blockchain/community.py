from ipv8.community import Community
from ipv8.lazy_community import lazy_wrapper
import asyncio

from payloads import SubmitTransactionPayload, SubmitTransactionResponsePayload, GetChainHeightPayload, ChainHeightResponsePayload, GetBlockPayload, BlockResponsePayload

from config import (MEMBER1_PUBLIC_KEY_HEX, MEMBER2_PUBLIC_KEY_HEX,
                    MEMBER3_PUBLIC_KEY_HEX, BLOCKCHAIN_COMMUNITY_ID_HEX,
                    LAB3_REGISTER_SERVER_PUBLIC_KEY_HEX)

MEMBER1_PUBLIC_KEY = bytes.fromhex(MEMBER1_PUBLIC_KEY_HEX)  #Darian
MEMBER2_PUBLIC_KEY = bytes.fromhex(MEMBER2_PUBLIC_KEY_HEX)  #Jayran
MEMBER3_PUBLIC_KEY = bytes.fromhex(MEMBER3_PUBLIC_KEY_HEX)  #Yves

TEAMMATE_COUNT = 2


class BlockchainCommunity(Community):

    community_id = bytes.fromhex(BLOCKCHAIN_COMMUNITY_ID_HEX)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_message_handler(SubmitTransactionPayload,
                                 self.on_submit_transaction)
        self.add_message_handler(GetChainHeightPayload,
                                 self.on_get_chain_height)
        self.add_message_handler(GetBlockPayload, self.on_get_block)

        self.server_peer = None
        self.member1_peer = None
        self.member3_peer = None

        self.group_id = "d8c9d397bea2ee37"

    # ---------------------------------------------------------------------
    # Helper methods
    # ---------------------------------------------------------------------

    def expected_server_public_key(self) -> bytes:
        """
        Return the official Lab 2 server public key as bytes.
        """
        return bytes.fromhex(LAB3_REGISTER_SERVER_PUBLIC_KEY_HEX)

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
                    print("=====Found Lab 3 server=====")
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

    # ---------------------------------------------------------------------
    # Lab Server Query Message Handlers
    # ---------------------------------------------------------------------

    @lazy_wrapper(SubmitTransactionPayload)
    def on_submit_transaction(self, peer, payload):

        if not self.is_server_peer(peer):
            print("Ignoring response from non-server peer")
            return

        print("SERVER RESPONSE:")
        print(payload)

    @lazy_wrapper(GetChainHeightPayload)
    def on_get_chain_height(self, peer, payload):

        if not self.is_server_peer(peer):
            print("Ignoring response from non-server peer")
            return

        print("SERVER RESPONSE:")
        print(payload)

    @lazy_wrapper(GetBlockPayload)
    def on_get_block(self, peer, payload):

        if not self.is_server_peer(peer):
            print("Ignoring response from non-server peer")
            return

        print("SERVER RESPONSE:")
        print(payload)
