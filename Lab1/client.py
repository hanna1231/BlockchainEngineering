import asyncio
from ipv8.configuration import ConfigBuilder, Strategy, WalkerDefinition, default_bootstrap_defs
from ipv8_service import IPv8
from community import Community
from dotenv import load_dotenv
import os
from nonce_finder import mine


async def main():
    # Configure IPv8: which key to use, which community to join
    builder = ConfigBuilder().clear_keys().clear_overlays()
    
    builder.add_key("my_peer", "curve25519", "my_key.pem")
    
    # Join the Lab 1 community with a random walk peer discovery strategy
    builder.add_overlay(
        "Community",
        "my_peer",
        [WalkerDefinition(Strategy.RandomWalk, 10, {"timeout": 3.0})],
        default_bootstrap_defs,  # standard bootstrapping servers to find initial peers
        {},
        []
    )
    
    # Start IPv8
    ipv8 = IPv8(
        builder.finalize(),
        extra_communities={"Community": Community})
    await ipv8.start()

    # Calculate nonce
    print("Start mining nonce")
    nonce = await asyncio.get_event_loop().run_in_executor(None, mine, EMAIL, GITHUB_URL) # Run_in_executor ensures that it runs concurrently with peer discovery
    
    # Get community instance and submit
    community = ipv8.get_overlay(Community)
    await community.wait_for_server_and_submit(EMAIL, GITHUB_URL, nonce)
    
    # Wait for the response to arrive
    await asyncio.sleep(10)
    
    # Cleanup
    await ipv8.stop()

if __name__ == "__main__":
    load_dotenv()
    EMAIL = os.getenv("EMAIL")
    if not EMAIL:
        raise ValueError("EMAIL not set in .env file")
    GITHUB_URL = "https://github.com/hanna1231/BlockchainEngineering"
    asyncio.run(main())
