import asyncio
import os
import time

from blockchain import Transaction
from community import BlockchainCommunity


async def run_dummy_transaction_test(
    blockchain_community: BlockchainCommunity,
    interval_seconds: int = 3,
) -> None:
    """
    Periodically creates dummy transactions and injects them into this node.

    This is only for local IPv8 testing.

    Flow:
    1. Create fake transaction.
    2. Add it to this node's mempool.
    3. Broadcast it to teammates.
    4. Miner should eventually include it in a block.
    """
    counter = 0

    # print("[TEST] Dummy transaction test started.")

    while True:
        counter += 1

        tx = Transaction(
            sender_key=blockchain_community.my_peer.public_key.key_to_bin(),
            data=f"dummy transaction {counter}".encode(),
            timestamp=int(time.time()),
            signature=os.urandom(64),  # fake signature for local testing
        )

        tx_hash = blockchain_community.blockchain.add_transaction(tx)

        # print(f"\n[TEST] Added dummy tx {counter}: {tx_hash.hex()}")
        # print(
        #     f"[TEST] Mempool size: "
        #     f"{blockchain_community.blockchain.mempool.size()}"
        # )

        # blockchain_community.broadcast_transaction(tx)
        # blockchain_community.blockchain.print_chain()

        await asyncio.sleep(interval_seconds)
        
    