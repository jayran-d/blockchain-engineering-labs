import hashlib
from dataclasses import dataclass

from ipv8.keyvault.crypto import ECCrypto

# =============================================================================
# Basic byte/hash helpers
# =============================================================================

HASH_SIZE = 32
HEADER_SIZE = 84


def sha256(data: bytes) -> bytes:
    """
    Return SHA-256(data) as raw 32 bytes.
    """
    return hashlib.sha256(data).digest()


def u64_be(value: int) -> bytes:
    """
    Encode an integer as an unsigned 64-bit big-endian value.

    Used for:
    - transaction timestamp
    - block timestamp
    - block nonce
    """
    if value < 0 or value >= 2**64:
        raise ValueError("value does not fit in uint64")

    return value.to_bytes(8, "big")


def u32_be(value: int) -> bytes:
    """
    Encode an integer as an unsigned 32-bit big-endian value.

    Used for:
    - block difficulty
    """
    if value < 0 or value >= 2**32:
        raise ValueError("value does not fit in uint32")

    return value.to_bytes(4, "big")


# =============================================================================
# Transaction
# =============================================================================


@dataclass
class Transaction:
    """
    A transaction received from the Lab 3 server.

    The transaction hash must be:

        SHA256(sender_key || data || timestamp_8byte_be || signature)
    """

    sender_key: bytes
    data: bytes
    timestamp: int
    signature: bytes

    def tx_hash(self) -> bytes:
        """
        Compute the 32-byte transaction hash
        """
        blob = (self.sender_key + self.data + u64_be(self.timestamp) +
                self.signature)

        return sha256(blob)

    def verify_signature(self) -> bool:
        """
        Verify the server transaction signature.

        Signature message:
                sender_key || data || timestamp_8byte_be
        """

        crypto = ECCrypto()

        try:
            public_key = crypto.key_from_public_bin(self.sender_key)

            signed_data = (self.sender_key + self.data +
                           u64_be(self.timestamp))

            return crypto.is_valid_signature(
                public_key,
                signed_data,
                self.signature,
            )

        except Exception as e:
            print(f"Signature verification failed: {e}")
            return False


# =============================================================================
# Block header
# =============================================================================


@dataclass
class BlockHeader:
    """
    Block header format.

    The packed header must be exactly 84 bytes:

        prev_hash   32 bytes
        txs_hash    32 bytes
        timestamp    8 bytes, uint64 big-endian
        difficulty   4 bytes, uint32 big-endian
        nonce        8 bytes, uint64 big-endian
    """

    prev_hash: bytes
    txs_hash: bytes
    timestamp: int
    difficulty: int
    nonce: int

    def pack(self) -> bytes:
        """
        Pack the block header into its exact binary format.
        """
        if len(self.prev_hash) != HASH_SIZE:
            raise ValueError("prev_hash must be exactly 32 bytes")

        if len(self.txs_hash) != HASH_SIZE:
            raise ValueError("txs_hash must be exactly 32 bytes")

        packed = (self.prev_hash + self.txs_hash + u64_be(self.timestamp) +
                  u32_be(self.difficulty) + u64_be(self.nonce))

        if len(packed) != HEADER_SIZE:
            raise ValueError("block header must be exactly 84 bytes")

        return packed

    def block_hash(self) -> bytes:
        """
        Compute the 32-byte hash of this block header.
        """
        return sha256(self.pack())


# =============================================================================
# Block
# =============================================================================


@dataclass
class Block:
    """
    A block consists of:
    - a header
    - the transactions included in the block

    Internally we keep full Transaction objects because that makes validation easy.
    When responding to the server, we only send concatenated transaction hashes.
    """

    header: BlockHeader
    transactions: list[Transaction]

    def block_hash(self) -> bytes:
        """
        Return the SHA-256 hash of the block header.
        """
        return self.header.block_hash()

    def tx_hashes(self) -> list[bytes]:
        """
        Return the list of transaction hashes in block order.
        """
        return [tx.tx_hash() for tx in self.transactions]

    def tx_hashes_bytes(self) -> bytes:
        """
        Return concatenated transaction hashes.

        This is exactly what the server expects in BlockResponsePayload.tx_hashes.
        Empty block => b"".
        """
        return b"".join(self.tx_hashes())

    def validate(self) -> bool:
        """
        Validate this block by checking:
        - prev_hash has correct size
        - txs_hash has correct size
        - txs_hash matches the included transactions
        - block hash satisfies declared PoW difficulty

        This does NOT check whether the block links to a previous block.
        Chain-link validation should be done when appending to the chain.
        """
        if len(self.header.prev_hash) != HASH_SIZE:
            return False

        if len(self.header.txs_hash) != HASH_SIZE:
            return False

        expected_txs_hash = compute_txs_hash(self.tx_hashes())

        if expected_txs_hash != self.header.txs_hash:
            return False

        if not valid_pow(self.block_hash(), self.header.difficulty):
            return False

        return True


# =============================================================================
# Transaction commitment
# =============================================================================


def compute_txs_hash(tx_hashes: list[bytes]) -> bytes:
    """
    Compute the block body commitment.

    The lab requires:

        txs_hash = SHA256(tx_hash_1 || tx_hash_2 || ... || tx_hash_n)

    For an empty block:

        txs_hash = SHA256(b"")

    Since b"".join([]) is b"", this works for both normal and empty blocks.
    """
    for tx_hash in tx_hashes:
        if len(tx_hash) != HASH_SIZE:
            raise ValueError("every transaction hash must be exactly 32 bytes")

    return sha256(b"".join(tx_hashes))


# =============================================================================
# Proof of Work
# =============================================================================


def count_leading_zero_bits(data: bytes) -> int:
    """
    Count the number of leading zero bits in a byte string.

    Example:
        b"\\x00\\x7f..." starts with:
        - 8 zero bits from 0x00
        - then 1 zero bit from 0x7f = 01111111
        => total 9 leading zero bits
    """
    total = 0

    for byte in data:
        if byte == 0:
            total += 8
            continue

        # First non-zero byte.
        # Check bits from most significant to least significant.
        for i in range(8):
            bit = (byte >> (7 - i)) & 1

            if bit == 0:
                total += 1
            else:
                return total

    return total


def valid_pow(block_hash: bytes, difficulty: int) -> bool:
    """
    Check whether block_hash satisfies the declared difficulty.

    Difficulty means:
        required number of leading zero bits in block_hash
    """
    if len(block_hash) != HASH_SIZE:
        return False

    if difficulty < 0:
        return False

    # SHA-256 only has 256 bits, so difficulty above 256 is impossible.
    if difficulty > 256:
        return False

    return count_leading_zero_bits(block_hash) >= difficulty


# =============================================================================
# Mempool
# =============================================================================


class Mempool:
    """
    Stores transactions that have been accepted but not yet included in a block.
    """

    def __init__(self):
        self.transactions: dict[bytes, Transaction] = {}

    def add(self, tx: Transaction) -> bytes:
        """
        Add transaction to mempool.

        Returns the transaction hash.
        """
        tx_hash = tx.tx_hash()
        self.transactions[tx_hash] = tx
        return tx_hash

    def contains(self, tx_hash: bytes) -> bool:
        return tx_hash in self.transactions

    def get_all(self) -> list[Transaction]:
        """
        Return all transactions currently waiting to be mined.
        """
        return list(self.transactions.values())

    def remove(self, tx_hash: bytes) -> None:
        self.transactions.pop(tx_hash, None)

    def remove_transactions(self, txs: list[Transaction]) -> None:
        """
        Remove transactions after they are included in a block.
        """
        for tx in txs:
            self.remove(tx.tx_hash())

    def size(self) -> int:
        return len(self.transactions)


# =============================================================================
# Blockchain
# =============================================================================


class Blockchain:
    """
    Fork-aware blockchain.

    Stores all valid known blocks and exposes the current canonical chain
    using the longest-chain rule.
    """

    def __init__(self):
        genesis = self.create_genesis_block()
        genesis_hash = genesis.block_hash()

        # All valid known blocks by block hash.
        self.blocks_by_hash: dict[bytes, Block] = {
            genesis_hash: genesis,
        }

        # Height of each known block.
        self.height_by_hash: dict[bytes, int] = {
            genesis_hash: 0,
        }

        # Current best chain tip according to longest-chain rule.
        self.best_tip_hash: bytes = genesis_hash

        # Blocks received before their parent.
        # key = missing parent hash
        # value = blocks waiting for that parent
        self.pending_blocks: dict[bytes, list[Block]] = {}

        self.mempool = Mempool()

    # -------------------------------------------------------------------------
    # Chain info
    # -------------------------------------------------------------------------

    def height(self) -> int:
        """
        Height of the current canonical chain.
        Genesis = 0.
        """
        return self.height_by_hash[self.best_tip_hash]

    def tip_hash(self) -> bytes:
        """
        Hash of the current canonical chain tip.
        """
        return self.best_tip_hash

    def tip(self) -> Block:
        """
        Current canonical tip block.
        """
        return self.blocks_by_hash[self.best_tip_hash]

    def has_block(self, block_hash: bytes) -> bool:
        return block_hash in self.blocks_by_hash

    def get_height_for_hash(self, block_hash: bytes) -> int | None:
        return self.height_by_hash.get(block_hash)

    def get_canonical_chain(self) -> list[Block]:
        """
        Reconstruct the current best chain from genesis to best tip.
        """
        chain: list[Block] = []
        current_hash = self.best_tip_hash

        while True:
            block = self.blocks_by_hash[current_hash]
            chain.append(block)

            if self.height_by_hash[current_hash] == 0:
                break

            current_hash = block.header.prev_hash

        chain.reverse()
        return chain

    def get_block(self, height: int) -> Block | None:
        """
        Return the block at height on the current canonical chain.
        """
        chain = self.get_canonical_chain()

        if height < 0 or height >= len(chain):
            return None

        return chain[height]

    # -------------------------------------------------------------------------
    # Transactions / mempool
    # -------------------------------------------------------------------------

    def add_transaction(self, tx: Transaction) -> bytes:
        return self.mempool.add(tx)

    def get_mempool_transactions(self) -> list[Transaction]:
        return self.mempool.get_all()

    def get_canonical_tx_hashes(self) -> set[bytes]:
        """
        Return all tx hashes already included in the current best chain.
        """
        tx_hashes: set[bytes] = set()

        for block in self.get_canonical_chain():
            for tx in block.transactions:
                tx_hashes.add(tx.tx_hash())

        return tx_hashes

    def get_mineable_transactions(self) -> list[Transaction]:
        """
        Return mempool transactions that are not already in the best chain.
        """
        confirmed_tx_hashes = self.get_canonical_tx_hashes()

        return [
            tx for tx in self.mempool.get_all()
            if tx.tx_hash() not in confirmed_tx_hashes
        ]

    def remove_confirmed_transactions_from_mempool(self) -> None:
        """
        Remove transactions that are already in the current best chain.
        """
        confirmed_tx_hashes = self.get_canonical_tx_hashes()

        for tx_hash in confirmed_tx_hashes:
            self.mempool.remove(tx_hash)

    # -------------------------------------------------------------------------
    # Block handling / fork switching
    # -------------------------------------------------------------------------

    def add_block(self, block: Block) -> bool:
        """
        Add a block to the block tree.

        Handles:
        - duplicate blocks
        - invalid blocks
        - unknown parents
        - side forks
        - longest-chain switching

        Returns True if the block was stored.
        Returns False if duplicate/invalid/pending.
        """
        block_hash = block.block_hash()

        # 1. Ignore duplicates.
        if block_hash in self.blocks_by_hash:
            return False

        # 2. Validate block-local rules:
        #    - txs_hash matches body
        #    - PoW is valid
        #    - header fields have correct sizes
        if not block.validate():
            return False

        parent_hash = block.header.prev_hash

        # 3. Chain-context validation:
        #    prev_hash must link to a known parent.
        #    If parent is unknown, keep it pending for later.
        if parent_hash not in self.blocks_by_hash:
            self.pending_blocks.setdefault(parent_hash, []).append(block)
            print(f"Stored pending block; missing parent={parent_hash.hex()}")
            return False

        parent_height = self.height_by_hash[parent_hash]
        block_height = parent_height + 1

        old_best_tip = self.best_tip_hash
        old_best_height = self.height()

        # 4. Store the valid block.
        self.blocks_by_hash[block_hash] = block
        self.height_by_hash[block_hash] = block_height

        # 5. Longest-chain rule.
        if block_height > old_best_height:
            self.best_tip_hash = block_hash

            print(f"Fork switch / best chain update: "
                  f"height {old_best_height} -> {block_height}")
            print(f"Old tip: {old_best_tip.hex()}")
            print(f"New tip: {block_hash.hex()}")

            # Now that best chain changed, remove txs confirmed in best chain.
            self.remove_confirmed_transactions_from_mempool()

        # If it is a side fork that does not overtake, store it but do not switch.
        else:
            print(f"Stored side-fork block at height {block_height}, "
                  f"current best height is {old_best_height}")

        # 6. Maybe this block unlocks pending children.
        self.process_pending_children(block_hash)

        return True

    def process_pending_children(self, parent_hash: bytes) -> None:
        """
        Try to add blocks that were waiting for this parent.
        """
        pending_children = self.pending_blocks.pop(parent_hash, [])

        for child in pending_children:
            self.add_block(child)

    @staticmethod
    def create_genesis_block() -> Block:
        """
        Create the fixed genesis block.

        All 3 teammates must create EXACTLY the same genesis block.
        Otherwise your chains already disagree at height 0.

        We use:
        - prev_hash = 32 zero bytes
        - no transactions
        - txs_hash = SHA256(b"")
        - timestamp = 0
        - difficulty = 0
        - nonce = 0

        difficulty = 0 means the genesis block is always valid.
        """
        header = BlockHeader(
            prev_hash=b"\x00" * HASH_SIZE,
            txs_hash=compute_txs_hash([]),
            timestamp=0,
            difficulty=0,
            nonce=0,
        )

        return Block(
            header=header,
            transactions=[],
        )

    # -------------------------------------------------------------------------
    # Block handling / fork switching
    # -------------------------------------------------------------------------

    def short_hash(self, h: bytes, chars: int = 8) -> str:
        """
        Short readable hash for debug output.
        """
        return h.hex()[:chars]

    def print_canonical_chain(self) -> None:
        """
        Print the current best/canonical chain from genesis to best tip.
        This is the chain returned to the server by get_block(height).
        """
        chain = self.get_canonical_chain()

        print("\n========== CANONICAL CHAIN ==========")
        print(f"Best height : {self.height()}")
        print(f"Best tip    : {self.tip_hash().hex()}")
        print(f"Chain length: {len(chain)}")

        for height, block in enumerate(chain):
            block_hash = block.block_hash()
            header = block.header

            print(f"\n----- Height {height} -----")
            print(f"Block hash : {block_hash.hex()}")
            print(f"Prev hash  : {header.prev_hash.hex()}")
            print(f"Txs hash   : {header.txs_hash.hex()}")
            print(f"Timestamp  : {header.timestamp}")
            print(f"Difficulty : {header.difficulty}")
            print(f"Nonce      : {header.nonce}")
            print(f"Valid      : {block.validate()}")
            print(f"Tx count   : {len(block.transactions)}")

            for i, tx in enumerate(block.transactions):
                print(f"  TX {i}: {tx.tx_hash().hex()}")

        print("\n=====================================\n")

    def print_block_tree(self) -> None:
        """
        Print all known blocks grouped by height.

        This helps debug forks:
            height 0: genesis
            height 1: block A
            height 2: block B, block C  <- fork
        """
        print("\n========== BLOCK TREE ==========")
        print(f"Known blocks   : {len(self.blocks_by_hash)}")
        print(f"Best height    : {self.height()}")
        print(f"Best tip       : {self.short_hash(self.best_tip_hash)}")
        print(f"Pending parents: {len(self.pending_blocks)}")

        # Group blocks by height.
        blocks_by_height: dict[int, list[tuple[bytes, Block]]] = {}

        for block_hash, block in self.blocks_by_hash.items():
            height = self.height_by_hash[block_hash]
            blocks_by_height.setdefault(height, []).append((block_hash, block))

        canonical_hashes = {
            block.block_hash()
            for block in self.get_canonical_chain()
        }

        for height in sorted(blocks_by_height.keys()):
            print(f"\n----- Height {height} -----")

            for block_hash, block in blocks_by_height[height]:
                marker = "BEST" if block_hash == self.best_tip_hash else ""
                canonical = "canonical" if block_hash in canonical_hashes else "fork"

                print(f"{self.short_hash(block_hash)} "
                      f"prev={self.short_hash(block.header.prev_hash)} "
                      f"txs={len(block.transactions)} "
                      f"valid={block.validate()} "
                      f"{canonical} {marker}")

        if self.pending_blocks:
            print("\n----- Pending blocks -----")

            for missing_parent_hash, blocks in self.pending_blocks.items():
                print(
                    f"Missing parent {self.short_hash(missing_parent_hash)}: "
                    f"{len(blocks)} block(s)")

                for block in blocks:
                    print(
                        f"  pending block={self.short_hash(block.block_hash())} "
                        f"txs={len(block.transactions)} "
                        f"valid={block.validate()}")

        print("\n===============================\n")

    def print_mempool(self) -> None:
        """
        Print current mempool contents.
        """
        print("\n========== MEMPOOL ==========")
        print(f"Size: {self.mempool.size()}")

        for i, tx in enumerate(self.mempool.get_all()):
            print(f"TX {i}: {tx.tx_hash().hex()}")
            print(f"  Sender   : {tx.sender_key.hex()[:32]}...")
            print(f"  Data     : {tx.data!r}")
            print(f"  Timestamp: {tx.timestamp}")

        print("============================\n")

    def print_debug_state(self) -> None:
        """
        Print everything useful for debugging consensus.
        """
        self.print_block_tree()
        self.print_canonical_chain()
        self.print_mempool()
