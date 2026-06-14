"""
Shared configuration for the Lab 3 PoW blockchain node.

This file should contain only non-secret configuration values that are safe to
commit. Private key files should be stored locally in the keys/ directory and
ignored by Git.
"""

from pathlib import Path


# ---------------------------------------------------------------------------
# Local paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]

# Each group member should place their own private IPv8 key at this path.
# The file itself should NOT be committed.
KEY_FILE = REPO_ROOT / "keys" / "lab_identity_key.pem"


# ---------------------------------------------------------------------------
# Group / blockchain identifiers
# ---------------------------------------------------------------------------

# Group identifier assigned/used for Lab 3.
GROUP_ID = "d8c9d397bea2ee37"

# Community ID for our blockchain overlay.
# Hex-decoded value: "DarianJayranYvesLab3"
BLOCKCHAIN_COMMUNITY_ID_HEX = "44617269616E4A617972616E597665734C616233"


# ---------------------------------------------------------------------------
# Registration server configuration
# ---------------------------------------------------------------------------

# Community ID for the official Lab 3 registration community.
REGISTER_COMMUNITY_ID_HEX = "4c616233426c6f636b636861696e323032365057"

# Public key of the Lab 3 registration server.
REGISTER_SERVER_PUBLIC_KEY_HEX = (
    "4c69624e61434c504b3ae3fc099fb56ca3b5e1de9a1c843387f2acdbb78b1bd4350"
    "ffde518068a0d246344b10d0d8c355fd0d76873e7d7f7838f3715e025af08f791324495e083331ce6"
)


# ---------------------------------------------------------------------------
# Group member public keys
# ---------------------------------------------------------------------------

# Darian
MEMBER_1_PUBLIC_KEY_HEX = (
    "4c69624e61434c504b3adc31a700de7e0d53fc6c3cfc52e2b8122f35d74def4aaf55b"
    "9ccdf81116f5f4f7d8c15de980916c0e953a4f23423ad1ff6abb34dbae4ac3c12bfdb76c0f4e81c"
)

# Jayran
MEMBER_2_PUBLIC_KEY_HEX = (
    "4c69624e61434c504b3a70597fc8337cce9c703a98ae454aef1ba9a0e9ab61a3b849"
    "33a606d1ec44466197b54b27c07d167ddfc134d03247b8290a6013d0b4ccc07817272e846aa51e50"
)

# Yves
MEMBER_3_PUBLIC_KEY_HEX = (
    "4c69624e61434c504b3aea1ebe2bb45bbaef6fd358df15349cf7494ea4c3079bd0987"
    "6d867e0cd339d5c341269531ea65b0f99daf123b585ebcef5c21d9e17c54d755e5cc5916c024ce4"
)

# Optional convenience list for iterating over all teammate keys.
MEMBER_PUBLIC_KEYS_HEX = {
    "darian": MEMBER_1_PUBLIC_KEY_HEX,
    "jayran": MEMBER_2_PUBLIC_KEY_HEX,
    "yves": MEMBER_3_PUBLIC_KEY_HEX,
}


# ---------------------------------------------------------------------------
# Blockchain parameters
# ---------------------------------------------------------------------------

# Number of leading zero bits required in a valid block hash.
BLOCK_DIFFICULTY = 8

# SHA-256 hash size in bytes.
HASH_SIZE = 32

# Serialized block header size in bytes.
HEADER_SIZE = 84

# Mining interval in seconds.
MINE_BLOCK_PER_SECONDS = 15