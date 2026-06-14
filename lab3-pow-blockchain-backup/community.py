from ipv8.community import Community
from ipv8.lazy_community import lazy_wrapper
import asyncio

from payloads import *

from config import (MEMBER1_PUBLIC_KEY_HEX, MEMBER2_PUBLIC_KEY_HEX,
                    MEMBER3_PUBLIC_KEY_HEX, BLOCKCHAIN_COMMUNITY_ID_HEX,
                    LAB3_REGISTER_SERVER_PUBLIC_KEY_HEX)

from blockchain import *

from miner import Miner

from serialization import serialize_transactions

MEMBER1_PUBLIC_KEY = bytes.fromhex(MEMBER1_PUBLIC_KEY_HEX)  #Darian
MEMBER2_PUBLIC_KEY = bytes.fromhex(MEMBER2_PUBLIC_KEY_HEX)  #Jayran
MEMBER3_PUBLIC_KEY = bytes.fromhex(MEMBER3_PUBLIC_KEY_HEX)  #Yves

TEAMMATE_COUNT = 2


class BlockchainCommunity(Community):

    community_id = bytes.fromhex(BLOCKCHAIN_COMMUNITY_ID_HEX)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Message Handlers
        self.add_message_handler(SubmitTransactionPayload,
                                 self.on_submit_transaction)
        self.add_message_handler(GetChainHeightPayload,
                                 self.on_get_chain_height)
        self.add_message_handler(GetBlockPayload, self.on_get_block)

        self.add_message_handler(TransactionBroadcastPayload,
                                 self.on_transaction_broadcast)

        # Peer instances
        self.server_peer = None
        self.member1_peer = None
        self.member3_peer = None

        self.group_id = "d8c9d397bea2ee37"

        self.blockchain = Blockchain()

        self.miner = Miner(blockchain=self.blockchain,
                           broadcast_block_callback=self.broadcast_block)

    # ---------------------------------------------------------------------
    # Peer & Keys Helper Methods
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
    # Broadcast Helper Methods
    # ---------------------------------------------------------------------

    def broadcast_to_teammates(self, payload) -> None:
        for teammate_peer in [self.member1_peer, self.member3_peer]:
            if teammate_peer is None:
                continue

            self.ez_send(teammate_peer, payload)

    def broadcast_transaction(self, tx: Transaction) -> None:
        """
        Broadcast a transaction to teammates so the miner can include it.
        """
        payload = TransactionBroadcastPayload(
            sender_key=tx.sender_key,
            data=tx.data,
            timestamp=tx.timestamp,
            signature=tx.signature,
        )

        self.broadcast_to_teammates(payload)

        print(f"Broadcasted transaction: {tx.tx_hash().hex()}")

    def broadcast_block(self, block: Block) -> None:
        """
        Broadcast a mined/accepted block to teammates.
        """
        pass

        # block_height = self.blockchain.height()

        # if block_height is None:
        #     print("Cannot broadcast block: block is not in local blockchain")
        #     return

        # payload = BlockBroadcastPayload(
        #     height=block_height,
        #     prev_hash=block.header.prev_hash,
        #     txs_hash=block.header.txs_hash,
        #     timestamp=block.header.timestamp,
        #     difficulty=block.header.difficulty,
        #     nonce=block.header.nonce,
        #     block_hash=block.block_hash(),
        #     tx_hashes=block.tx_hashes_bytes(),
        #     transactions_bytes=serialize_transactions(block.transactions),
        # )

        # self.broadcast_to_teammates(payload)

        # print(f"Broadcasted block at height={block_height}")

    # ---------------------------------------------------------------------
    # Lab Server Query Message Handlers
    # ---------------------------------------------------------------------

    @lazy_wrapper(SubmitTransactionPayload)
    def on_submit_transaction(self, peer, payload: SubmitTransactionPayload):

        if not self.is_server_peer(peer):
            print("Ignoring SubmitTransaction from non-server peer")
            return

        tx = Transaction(
            sender_key=payload.sender_key,
            data=payload.data,
            timestamp=payload.timestamp,
            signature=payload.signature,
        )

        tx_hash = tx.tx_hash()

        if not tx.verify_signature():
            response = SubmitTransactionResponsePayload(
                success=False,
                tx_hash=tx_hash,
                message="Invalid transaction signature",
            )

            self.ez_send(peer, response)

            print(f"Rejected transaction: invalid signature, "
                  f"tx_hash={tx_hash.hex()}")
            return

        if self.blockchain.mempool.contains(tx_hash):
            response = SubmitTransactionResponsePayload(
                success=True,
                tx_hash=tx_hash,
                message="Transaction already in mempool",
            )

            self.ez_send(peer, response)

            print(f"Duplicate transaction already in mempool: {tx_hash.hex()}")
            return

        if tx_hash in self.blockchain.get_canonical_tx_hashes():
            response = SubmitTransactionResponsePayload(
                success=True,
                tx_hash=tx_hash,
                message="Transaction already included in best chain",
            )

            self.ez_send(peer, response)

            print(f"Transaction already in best chain: {tx_hash.hex()}")
            return

        self.blockchain.add_transaction(tx)

        response = SubmitTransactionResponsePayload(
            success=True,
            tx_hash=tx_hash,
            message="Transaction accepted into mempool",
        )

        self.ez_send(peer, response)

        print(f"Accepted transaction: {tx_hash.hex()}")
        print(f"Mempool size: {self.blockchain.mempool.size()}")

        # Share transaction with teammates.
        self.broadcast_transaction(tx)

        print("Broadcasted submitted transaction to teammates")

    @lazy_wrapper(GetChainHeightPayload)
    def on_get_chain_height(self, peer, payload: GetChainHeightPayload):

        if not self.is_server_peer(peer):
            print("Ignoring GetChainHeight from non-server peer")
            return

        height = self.blockchain.height()
        tip_hash = self.blockchain.tip_hash()

        response = ChainHeightResponsePayload(
            request_id=payload.request_id,
            height=height,
            tip_hash=tip_hash,
        )

        self.ez_send(peer, response)

        print(
            f"Sent chain height response: height={height}, tip={tip_hash.hex()}"
        )

    @lazy_wrapper(GetBlockPayload)
    def on_get_block(self, peer, payload: GetBlockPayload):

        if not self.is_server_peer(peer):
            print("Ignoring GetBlock from non-server peer")
            return

        block = self.blockchain.get_block(payload.height)

        if block is None:
            print(f"Requested invalid block height: {payload.height}")
            return

        response = BlockResponsePayload(
            height=payload.height,
            prev_hash=block.header.prev_hash,
            txs_hash=block.header.txs_hash,
            timestamp=block.header.timestamp,
            difficulty=block.header.difficulty,
            nonce=block.header.nonce,
            block_hash=block.block_hash(),
            tx_hashes=block.tx_hashes_bytes(),
        )

        self.ez_send(peer, response)

        print(f"Sent block response for height={payload.height}")
        print(f"block_hash={block.block_hash().hex()}")
        print(f"tx_count={len(block.transactions)}")

    # ---------------------------------------------------------------------
    # Internal Communication Between Nodes/Teammates Message Handlers
    # ---------------------------------------------------------------------

    @lazy_wrapper(TransactionBroadcastPayload)
    def on_transaction_broadcast(self, peer,
                                 payload: TransactionBroadcastPayload):

        if not self.is_teammate_peer(peer):
            print("Ignoring NewTransaction from non-teammate peer")
            return

        tx = Transaction(
            sender_key=payload.sender_key,
            data=payload.data,
            timestamp=payload.timestamp,
            signature=payload.signature,
        )

        tx_hash = tx.tx_hash()

        if not tx.verify_signature():
            print(f"Ignoring invalid propagated transaction: {tx_hash.hex()}")
            return

        if self.blockchain.mempool.contains(tx_hash):
            print(f"Ignoring duplicate transaction: {tx_hash.hex()}")
            return

        self.blockchain.add_transaction(tx)

        print(f"Accepted propagated transaction: {tx_hash.hex()}")
        print(f"Mempool size: {self.blockchain.mempool.size()}")
