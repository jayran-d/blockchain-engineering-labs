import asyncio
import os

from dotenv import load_dotenv

from ipv8.configuration import ConfigBuilder, Strategy, WalkerDefinition, default_bootstrap_defs
from ipv8_service import IPv8

import logging

from community import Lab1Community
from pow import mine_nonce_fast



# Load variables from .env into os.environ
load_dotenv()

EMAIL: str = os.environ["EMAIL"]
GITHUB_URL: str = os.environ["GITHUB_URL"]

KEY_FILE = "keys/lab1_key.pem"


def compute_proof_of_work():
    print("Mining nonce...")
    nonce = mine_nonce_fast(EMAIL, GITHUB_URL)
    print(f"Using nonce: {nonce}")
    return nonce


def init_ipv8():

    builder = ConfigBuilder().clear_keys().clear_overlays()

    # Load or create our IPv8 identity key.
    # This .pem file is important. Do not delete it after registering.
    builder.add_key("my peer", "curve25519", KEY_FILE)

    # Add our custom Lab1Community overlay.
    # The discovery strategy helps us find peers in this community.
    builder.add_overlay(
        "Lab1Community",
        "my peer",
        [WalkerDefinition(Strategy.RandomWalk, 10, {"timeout": 2.0})],
        default_bootstrap_defs,
        {},
        [],
    )

    ipv8 = IPv8(
        builder.finalize(),
        extra_communities={"Lab1Community": Lab1Community},
    )
    
    # Suppress noisy IPv8 packet-handling errors from unrelated peers.
    logging.getLogger("Lab1Community").setLevel(logging.CRITICAL)
    
    return ipv8


async def main():
    """
    Start the client, mine a valid nonce, connect to IPv8,
    find the server peer, and submit the Proof of Work.
    """

    os.makedirs("keys", exist_ok=True)

    # Mine the nonce before sending anything to the server.
    nonce = compute_proof_of_work()
    # nonce: int = 518866785
    
    
    ipv8 = init_ipv8()

    await ipv8.start()

    print("IPv8 started.")
    print("Searching for server peer...")

    community: Lab1Community = ipv8.get_overlay(Lab1Community)

    submitted = False

    try:
        while True:
            if not submitted:
                submitted = community.send_submission(EMAIL, GITHUB_URL, nonce)

            await asyncio.sleep(1)

    finally:
        await ipv8.stop()


if __name__ == "__main__":
    asyncio.run(main())
