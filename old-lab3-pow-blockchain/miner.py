import asyncio
import time

from blockchain import (
    HASH_SIZE,
    Block,
    BlockHeader,
    Blockchain,
    Transaction,
    compute_txs_hash,
)

BLOCK_INTERVAL_SECONDS = 10
BLOCK_DIFFICULTY = 8
IS_MINER = True


class Miner:
    """
    Mines one block every BLOCK_INTERVAL_SECONDS.

    The miner:
    - copies transactions from the mempool
    - mines a block
    - adds it to the local blockchain
    - broadcasts it if accepted
    """

    def __init__(
        self,
        blockchain: Blockchain,
        broadcast_block_callback,
        is_enabled: bool = IS_MINER,
        difficulty: int = BLOCK_DIFFICULTY,
        block_interval_seconds: int = BLOCK_INTERVAL_SECONDS,
    ):
        self.blockchain = blockchain
        self.broadcast_block_callback = broadcast_block_callback
        self.is_enabled = is_enabled
        self.difficulty = difficulty
        self.block_interval_seconds = block_interval_seconds

        self.running = False
        self.task: asyncio.Task | None = None

    def start(self) -> None:
        if not self.is_enabled:
            print("Mining disabled on this node.")
            return

        if self.running:
            print("Miner already running.")
            return

        self.running = True
        self.task = asyncio.create_task(self.mining_loop())

        print(f"Miner started. Mining every "
              f"{self.block_interval_seconds} seconds.")

    def stop(self) -> None:
        self.running = False

        if self.task is not None:
            self.task.cancel()

    async def mining_loop(self) -> None:
        while self.running:
            try:
                await self.mine_one_block()

                # self.blockchain.print_chain()

                # Wait before creating the next block.
                await asyncio.sleep(self.block_interval_seconds)

            except asyncio.CancelledError:
                break

            except Exception as e:
                print(f"Mining error: {e}")
                await asyncio.sleep(1)

    async def mine_one_block(self) -> None:
        prev_hash = self.blockchain.tip_hash()
        transactions = self.blockchain.get_mineable_transactions()
        timestamp = int(time.time())

        next_height = self.blockchain.height() + 1

        print(f"Mining block at height {next_height} "
              f"with {len(transactions)} tx(s)...")

        block = await asyncio.to_thread(
            mine_block,
            prev_hash=prev_hash,
            transactions=transactions,
            timestamp=timestamp,
            difficulty=self.difficulty,
        )

        added = self.blockchain.add_block(block)

        if not added:
            print("Mined block was not added, probably stale or invalid.")
            return
        
        self.blockchain.print_block_tree()

        block_height = self.blockchain.get_height_for_hash(block.block_hash())

        print(f"Mined block at height {block_height} "
              f"hash={block.block_hash().hex()}")

        self.broadcast_block_callback(block)


# =============================================================================
# Mining helper
# =============================================================================


def mine_block(
    prev_hash: bytes,
    transactions: list[Transaction],
    timestamp: int,
    difficulty: int = BLOCK_DIFFICULTY,
) -> Block:
    """
    Mine a new block.

    Mining means:
    - choose the transactions for the block
    - compute txs_hash
    - build a block header pointing to prev_hash
    - try nonce values until the block hash satisfies the difficulty

    This function returns a full valid Block.
    """
    if len(prev_hash) != HASH_SIZE:
        raise ValueError("prev_hash must be exactly 32 bytes")

    transactions = list(transactions)

    tx_hashes = [tx.tx_hash() for tx in transactions]
    txs_hash = compute_txs_hash(tx_hashes)

    nonce = 0

    while True:
        header = BlockHeader(
            prev_hash=prev_hash,
            txs_hash=txs_hash,
            timestamp=timestamp,
            difficulty=difficulty,
            nonce=nonce,
        )

        block = Block(
            header=header,
            transactions=transactions,
        )

        if block.validate():
            return block

        nonce += 1
