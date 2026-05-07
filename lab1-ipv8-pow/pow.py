import hashlib

DIFFICULTY_BITS = 28

# The server accepts nonces from 0 up to 2^63 - 1.
# The wire format is signed int64, so we should not go above this.
MAX_NONCE: int = 2**63 - 1


def hash_submission(email: str, github_url: str, nonce: int) -> bytes:
    """
    Build the exact byte input required by the assignment and hash it with SHA-256.

    The assignment says the hash input must be:

    email_utf8 || "\\n" || github_url_utf8 || "\\n" || nonce_as_8_byte_big_endian
    
    """

    if nonce < 0:
        raise ValueError("Nonce must be non-negative")

    if nonce > MAX_NONCE:
        raise ValueError("Nonce must fit in signed int64 range")

    email_bytes = email.encode("utf-8")

    github_url_bytes = github_url.encode("utf-8")

    # Convert the nonce integer to exactly 8 bytes.
    #
    # Example:
    # nonce = 5 becomes:
    # 00 00 00 00 00 00 00 05
    nonce_bytes = nonce.to_bytes(8, "big", signed=False)

    # Build the exact byte sequence the server will also hash.
    # b"\\n" is the newline separator required by the assignment.
    data = email_bytes + b"\n" + github_url_bytes + b"\n" + nonce_bytes

    # Return the raw SHA-256 digest.
    # .digest() gives bytes
    return hashlib.sha256(data).digest()


def has_28_leading_zero_bits(digest: bytes) -> bool:

    return (digest[0] == 0 and digest[1] == 0 and digest[2] == 0
            and digest[3] < 16)


def mine_nonce(email: str, github_url: str, start_nonce: int = 0) -> int:
    """
    Brute-force nonces until we find one whose SHA-256 hash satisfies the difficulty.

    Returns:
        The first nonce found that satisfies the Proof of Work.
    """

    if start_nonce < 0:
        raise ValueError("Start nonce must be non-negative")

    nonce = start_nonce

    while nonce <= MAX_NONCE:
        # Compute SHA-256(email || "\\n" || github_url || "\\n" || nonce_bytes)
        digest = hash_submission(email, github_url, nonce)

        # Check whether the hash satisfies the Proof of Work difficulty.
        if has_28_leading_zero_bits(digest):
            print(f"Found nonce: {nonce}")
            print(f"Hash: {digest.hex()}")
            return nonce

        # Print progress every 10 million attempts just cause.
        if nonce % 10_000_000 == 0:
            print(f"Tried nonce {nonce:,}")

        nonce += 1

    raise RuntimeError("No valid nonce found")


import hashlib

def mine_nonce_fast(email: str, github_url: str, start_nonce: int = 0) -> int:
    prefix = email.encode() + b"\n" + github_url.encode() + b"\n"
    
    # Hash the constant prefix once, then copy that state per iteration
    prefix_hash = hashlib.sha256(prefix)

    nonce = start_nonce
    while nonce <= MAX_NONCE:
        # copy() is much cheaper than rehashing prefix every time
        h = prefix_hash.copy()
        h.update(nonce.to_bytes(8, "big"))
        digest = h.digest()

        if digest[0] == 0 and digest[1] == 0 and digest[2] == 0 and digest[3] < 16:
            return nonce
        
        # Print progress every 10 million attempts just cause.
        if nonce % 10_000_000 == 0:
            print(f"Tried nonce {nonce:,}")


        nonce += 1