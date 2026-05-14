import asyncio
import os

from dotenv import load_dotenv

from ipv8.configuration import ConfigBuilder, Strategy, WalkerDefinition, default_bootstrap_defs
from ipv8_service import IPv8
from ipv8.util import run_forever

import logging

from community import BcECommunity

# Load variables from .env into os.environ
load_dotenv()

KEY_FILE = "keys/lab_identity_key.pem"


def init_ipv8():

    builder = ConfigBuilder().clear_keys().clear_overlays()

    # Load or create our IPv8 identity key.
    builder.add_key("my peer", "curve25519", KEY_FILE)

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


async def challenge_request_loop(community: BcECommunity,
                                 interval: float = 0.03):
    """
    Keep requesting challenges after we know the group_id.
    """

    while not community.round_started:
        if community.group_id is not None:
            community.request_challenge()

        await asyncio.sleep(interval)

    # print("My round has started. Stopping challenge request loop.")


async def main():
    os.makedirs("keys", exist_ok=True)

    ipv8 = init_ipv8()
    await ipv8.start()

    # print("IPv8 started.")
    # print("Searching for server peer...")

    community: BcECommunity = ipv8.get_overlay(BcECommunity)

    try:
        await community.find_server_peer()
        await community.find_teammate_peers()

        asyncio.create_task(challenge_request_loop(community))

        # print("Challenge request loop started.")
        # print("Waiting for group_id from member 1...")

        await run_forever()

    finally:
        await ipv8.stop()


if __name__ == "__main__":
    asyncio.run(main())
