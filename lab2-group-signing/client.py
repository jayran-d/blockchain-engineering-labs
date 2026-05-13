import asyncio
import os

from dotenv import load_dotenv

from ipv8.configuration import ConfigBuilder, Strategy, WalkerDefinition, default_bootstrap_defs
from ipv8_service import IPv8

import logging

from community import BcECommunity

# Load variables from .env into os.environ
load_dotenv()

KEY_FILE = "keys/lab_identity_key.pem"


def init_ipv8():

    builder = ConfigBuilder().clear_keys().clear_overlays()

    # Load or create our IPv8 identity key.
    # This .pem file is important. Do not delete it after registering.
    builder.add_key("my peer", "curve25519", KEY_FILE)

    # Add our custom BcECommunity overlay.
    # The discovery strategy helps us find peers in this community.
    builder.add_overlay(
        "BcECommunity",
        "my peer",
        [WalkerDefinition(Strategy.RandomWalk, 10, {"timeout": 2.0})],
        default_bootstrap_defs,
        {},
        [],
    )

    ipv8 = IPv8(
        builder.finalize(),
        extra_communities={"BcECommunity": BcECommunity},
    )

    # Suppress noisy IPv8 packet-handling errors from unrelated peers.
    logging.getLogger("BcECommunity").setLevel(logging.CRITICAL)

    return ipv8


async def main():
    """
    Start the client, mine a valid nonce, connect to IPv8,
    find the server peer, and submit the Proof of Work.
    """

    os.makedirs("keys", exist_ok=True)

    ipv8 = init_ipv8()

    await ipv8.start()

    print("IPv8 started.")
    print("Searching for server peer...")

    community: BcECommunity = ipv8.get_overlay(BcECommunity)

    registered = False

    try:

        await community.find_server_peer()

        while True:

            if not registered:
                registered = community.register_group()

            await asyncio.sleep(0.25)

    finally:
        await ipv8.stop()


if __name__ == "__main__":
    asyncio.run(main())
