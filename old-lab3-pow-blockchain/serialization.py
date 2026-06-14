from blockchain import Transaction
from blockchain import u32_be, u64_be

# =============================================================================
# Transaction serialization
# =============================================================================

def read_u32_be(data: bytes, offset: int) -> tuple[int, int]:
    """
    Read a uint32 big-endian integer from data at offset.

    Returns:
        value, new_offset
    """
    if offset + 4 > len(data):
        raise ValueError("not enough bytes to read uint32")

    value = int.from_bytes(data[offset:offset + 4], "big")
    return value, offset + 4


def read_u64_be(data: bytes, offset: int) -> tuple[int, int]:
    """
    Read a uint64 big-endian integer from data at offset.

    Returns:
        value, new_offset
    """
    if offset + 8 > len(data):
        raise ValueError("not enough bytes to read uint64")

    value = int.from_bytes(data[offset:offset + 8], "big")
    return value, offset + 8


def read_var_bytes(data: bytes, offset: int) -> tuple[bytes, int]:
    """
    Read length-prefixed bytes.

    Format:
        length: 4 bytes big-endian
        value:  length bytes
    """
    length, offset = read_u32_be(data, offset)

    if offset + length > len(data):
        raise ValueError("not enough bytes to read variable bytes")

    value = data[offset:offset + length]
    return value, offset + length


def serialize_transactions(transactions: list[Transaction]) -> bytes:
    """
    Serialize transactions into bytes for BlockBroadcastPayload.

    Format:
        tx_count: 4 bytes

        For each transaction:
            sender_key_len: 4 bytes
            sender_key:     variable bytes

            data_len:       4 bytes
            data:           variable bytes

            timestamp:      8 bytes

            signature_len:  4 bytes
            signature:      variable bytes
    """
    out = bytearray()

    out += u32_be(len(transactions))

    for tx in transactions:
        out += u32_be(len(tx.sender_key))
        out += tx.sender_key

        out += u32_be(len(tx.data))
        out += tx.data

        out += u64_be(tx.timestamp)

        out += u32_be(len(tx.signature))
        out += tx.signature

    return bytes(out)


def deserialize_transactions(data: bytes) -> list[Transaction]:
    """
    Deserialize bytes created by serialize_transactions().
    """
    offset = 0

    tx_count, offset = read_u32_be(data, offset)

    transactions: list[Transaction] = []

    for _ in range(tx_count):
        sender_key, offset = read_var_bytes(data, offset)
        tx_data, offset = read_var_bytes(data, offset)
        timestamp, offset = read_u64_be(data, offset)
        signature, offset = read_var_bytes(data, offset)

        transactions.append(
            Transaction(
                sender_key=sender_key,
                data=tx_data,
                timestamp=timestamp,
                signature=signature,
            ))

    if offset != len(data):
        raise ValueError("extra bytes at end of serialized transactions")

    return transactions
