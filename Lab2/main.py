import asyncio
import multiprocessing
from ipv8.configuration import ConfigBuilder, Strategy, WalkerDefinition, default_bootstrap_defs
from ipv8_service import IPv8
from lab2_community import Lab2Community


KEY_FILE1 = "first_key.txt"
KEY_FILE2 = "second_key.txt"
KEY_FILE3 = "third_key.txt"

 # ─── Main ────────────────────────────────────
 
async def main(): 
    global _member_pubkeys
    # keys = [load_or_create_key(k) for k in [KEY_FILE1, KEY_FILE2, KEY_FILE3]]
    # _member_pubkeys = [k.pub().key_to_bin() for k in keys]
    _member_pubkeys = [
        bytes.fromhex(open(KEY_FILE1).read().strip()),
        bytes.fromhex(open(KEY_FILE2).read().strip()),
        bytes.fromhex(open(KEY_FILE3).read().strip()),
    ]
    
    builder = (
        ConfigBuilder()
        .clear_keys()
        .clear_overlays()
        .add_key("my_key", "curve25519", ".\..\my_key.pem") 
        .add_overlay(
            "Lab2Community",
            "my_key",
            [WalkerDefinition(Strategy.RandomWalk, 50, {"timeout": 3.0})],
            default_bootstrap_defs,
            {},
            [("started",)],
        )
    )
 
    ipv8_instance = IPv8(
        builder.finalize(),
        extra_communities={"Lab2Community": Lab2Community},
    )
    await ipv8_instance.start()
    await asyncio.sleep(5)
    # print("Walkable addresses known:", ipv8_instance.network.get_walkable_addresses())
 
    community: Lab2Community = ipv8_instance.get_overlay(Lab2Community)
 
    print("🌐  IPv8 started — searching for server peer…")
 
    await community.wait_for_response(timeout=600)
 
    await ipv8_instance.stop()
    print("\nDone.")
 


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")
    multiprocessing.freeze_support()
    asyncio.run(main())