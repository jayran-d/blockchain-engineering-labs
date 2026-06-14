import asyncio

from ipv8.community import Community
from ipv8.lazy_community import lazy_wrapper

from config import (
    BLOCKCHAIN_COMMUNITY_ID_HEX,
    REGISTER_SERVER_PUBLIC_KEY_HEX,
    MEMBER_PUBLIC_KEYS_HEX,
    GROUP_ID,
)


class BlockchainCommunity(Community):

    community_id = bytes.fromhex(BLOCKCHAIN_COMMUNITY_ID_HEX)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.group_id = GROUP_ID

        # ------------------------------------------------------------------
        # Message handlers
        # ------------------------------------------------------------------

        # self.add_message_handler...
        # ------------------------------------------------------------------
        # Known peers
        # ------------------------------------------------------------------
        self.server_peer = None

        # Map teammate name -> peer object once discovered.
        self.teammate_peers = {
            "darian": None,
            "jayran": None,
            "yves": None,
        }

        # Do not include our own peer here yet. We filter dynamically using
        # our own public key in is_teammate_peer().
        self.expected_teammate_keys = {
            name.lower(): bytes.fromhex(public_key_hex)
            for name, public_key_hex in MEMBER_PUBLIC_KEYS_HEX.items()
        }

        # TODO: Add blockchain, mempool, and miner state here.

    # ----------------------------------------------------------------------
    # Peer and key helper methods
    # ----------------------------------------------------------------------

    def expected_server_public_key(self) -> bytes:
        """
        Return the official Lab 3 registration/server public key as bytes.
        """
        return bytes.fromhex(REGISTER_SERVER_PUBLIC_KEY_HEX)

    def peer_public_key(self, peer) -> bytes:
        """
        Return an IPv8 peer's public key in the byte format used by the lab.
        """
        return peer.public_key.key_to_bin()

    def own_public_key(self) -> bytes:
        """
        Return this node's public key.
        """
        return self.my_peer.public_key.key_to_bin()

    def is_server_peer(self, peer) -> bool:
        """
        Check whether a peer is the official Lab 3 server.
        """
        return self.peer_public_key(peer) == self.expected_server_public_key()

    def is_own_peer_key(self, public_key: bytes) -> bool:
        """
        Check whether a public key belongs to this node.
        """
        return public_key == self.own_public_key()

    def is_teammate_peer(self, peer) -> bool:
        """
        Check whether a peer is one of the known group members, excluding self.
        """
        peer_key = self.peer_public_key(peer)

        if self.is_own_peer_key(peer_key):
            return False

        return peer_key in self.expected_teammate_keys.values()

    def teammate_name_for_peer(self, peer) -> str | None:
        """
        Return the teammate name for a peer, or None if it is unknown.
        """
        peer_key = self.peer_public_key(peer)

        for name, expected_key in self.expected_teammate_keys.items():
            if peer_key == expected_key:
                return name

        return None

    # ----------------------------------------------------------------------
    # Peer discovery helper methods
    # ----------------------------------------------------------------------

    async def find_server_peer(self):
        """
        Keep looking through discovered peers until the Lab 3 server is found.
        """
        while self.server_peer is None:
            peers = self.get_peers()
            print(f"Discovered {len(peers)} peer(s).")

            for peer in peers:
                try:
                    if self.is_server_peer(peer):
                        self.server_peer = peer
                        print("===== Found Lab 3 server =====")
                        return peer
                except Exception as error:
                    print(f"Skipping peer with unreadable public key: {error}")

            print("Server peer not found yet.")
            await asyncio.sleep(0.25)

    async def find_teammate_peers(self):
        """
        Keep looking through discovered peers until all other teammates are found.
        """
        while True:
            peers = self.get_peers()
            print(f"Discovered {len(peers)} peer(s).")

            for peer in peers:
                try:
                    teammate_name = self.teammate_name_for_peer(peer)
                except Exception as error:
                    print(f"Skipping peer with unreadable public key: {error}")
                    continue

                if teammate_name is None:
                    continue

                # # Do not store ourselves as a teammate.
                # if self.is_own_peer_key(self.peer_public_key(peer)):
                #     continue

                if self.teammate_peers[teammate_name] is None:
                    self.teammate_peers[teammate_name] = peer
                    print(f"===== Found teammate: {teammate_name} =====")

            if self.all_teammates_found():
                print("All teammate peers found.")
                return self.teammate_peers

            await asyncio.sleep(0.25)

    def all_teammates_found(self) -> bool:
        """
        Return True once all teammates except this node have been found.
        """
        own_key = self.own_public_key()

        for name, expected_key in self.expected_teammate_keys.items():
            if expected_key == own_key:
                continue

            if self.teammate_peers[name] is None:
                return False

        return True

    # ----------------------------------------------------------------------
    # Broadcast helper methods
    # ----------------------------------------------------------------------

    def broadcast_to_teammates(self, payload) -> None:
        """
        Send a payload to all currently discovered teammates.
        """
        for teammate_peer in self.teammate_peers.values():
            self.ez_send(teammate_peer, payload)

    # ----------------------------------------------------------------------
    # Lab server query message handlers
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Internal teammate message handlers
    # ----------------------------------------------------------------------
