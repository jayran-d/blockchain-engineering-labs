import asyncio
import os

from dotenv import load_dotenv

from ipv8.configuration import ConfigBuilder, Strategy, WalkerDefinition, default_bootstrap_defs
from ipv8_service import IPv8
from ipv8.util import run_forever

import logging

from registration.community import Lab3RegistrationCommunity
from community import BlockchainCommunity

# Load variables from .env into os.environ
load_dotenv()

KEY_FILE = "keys/lab_identity_key.pem"


def init_ipv8():
    builder = ConfigBuilder().clear_keys().clear_overlays()

    builder.add_key("my peer", "curve25519", KEY_FILE)

    # Community 1: used only for registering with the Lab 3 server
    builder.add_overlay(
        "Lab3RegistrationCommunity",
        "my peer",
        [WalkerDefinition(Strategy.RandomWalk, 10, {"timeout": 2.0})],
        default_bootstrap_defs,
        {},
        [],
    )

    # Community 2: actual PoW blockchain community
    builder.add_overlay(
        "BlockchainCommunity",
        "my peer",
        [WalkerDefinition(Strategy.RandomWalk, 10, {"timeout": 2.0})],
        default_bootstrap_defs,
        {},
        [],
    )

    ipv8 = IPv8(
        builder.finalize(),
        extra_communities={
            "Lab3RegistrationCommunity": Lab3RegistrationCommunity,
            "BlockchainCommunity": BlockchainCommunity,
        },
    )

    # Suppress noisy IPv8 packet-handling errors from unrelated peers.
    logging.getLogger("Lab3RegistrationCommunity").setLevel(logging.CRITICAL)
    logging.getLogger("BlockchainCommunity").setLevel(logging.CRITICAL)

    return ipv8


async def main():

    ipv8 = init_ipv8()
    
    await ipv8.start()

    # print("IPv8 started.")
    # print("Searching for server peer...")

    register_community: Lab3RegistrationCommunity = ipv8.get_overlay(
        Lab3RegistrationCommunity)

    blockchain_community: BlockchainCommunity = ipv8.get_overlay(
        BlockchainCommunity)

    try:
        await register_community.find_server_peer()
        register_community.register_blockchain()

        await run_forever()

    finally:
        await ipv8.stop()


if __name__ == "__main__":
    asyncio.run(main())
