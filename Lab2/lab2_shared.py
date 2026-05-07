import asyncio
import multiprocessing
import os
from ipv8.community import Community, CommunitySettings
from ipv8.configuration import ConfigBuilder, Strategy, WalkerDefinition, default_bootstrap_defs
from ipv8.keyvault.crypto import default_eccrypto
from ipv8.lazy_community import lazy_wrapper
from ipv8.messaging.payload_dataclass import VariablePayload, vp_compile
from ipv8.peer import Peer as PeerType
from ipv8_service import IPv8

COMMUNITY_ID_HEX = "4c61623247726f75705369676e696e6732303236"
SERVER_PUBKEY_HEX = (
    "4c69624e61434c504b3a82e33614a342774e084af80835838d6dbdb64a537d3ddb6c1d82011a7f101553cda40cf5fa0e0fc23abd0a9c4f81322282c5b34566f6b8401f5f683031e60c96"
)
PERSONAL_COMMUNITY_ID_HEX = b'v\x16p\xca\x81L\n\xa2IjX\x84\x0b\x7f\xe7\x83\xc0\xb4\xd0p'

KEY_FILE1 = "first_key.pem"
KEY_FILE2 = "second_key.txt"
KEY_FILE3 = "third_key.pem"

_member_pubkeys: list[bytes] = []
# ─── Message payloads ────────────────────────
 
class RegisterPayload(VariablePayload):
    msg_id = 1
    format_list = ["varlenH", "varlenH", "varlenH"]
    names = ["member1_key", "member2_key", "member3_key"]
 
class ResponsePayload(VariablePayload):
    msg_id = 2
    format_list = ["?", "varlenHutf8", "varlenHutf8"]
    names = ["success", "group_id", "message"]

class ChallengeRequestPayload(VariablePayload):
    msg_id = 3
    format_list = ["varlenHutf8"]
    names = ["group_id"]

class ChallengeResponsePayload(VariablePayload):
    msg_id = 4
    format_list = ["varlenH", "q", "d"]
    names = ["nonce", "round_number", "deadline"]

class SubmissionPayload(VariablePayload):
    msg_id = 5
    format_list = ["varlenH", "q", "VarlenH", "VarlenH", "VarlenH"]
    names = ["group_id", "round_number", "sig1", "sig2", "sig3"]

class RoundResultPayload(VariablePayload):
    msg_id = 6
    format_list = ["?", "q", "q", "VarlenHut8"]
    names = ["success", "round_number", "round_completed", "message"]
 
# Compile for faster (de)serialisation
RegisterPayload = vp_compile(RegisterPayload)
ResponsePayload   = vp_compile(ResponsePayload)
ChallengeRequestPayload = vp_compile(ChallengeRequestPayload)
ChallengeResponsePayload = vp_compile(ChallengeResponsePayload)
SubmissionPayload = vp_compile(SubmissionPayload)
RoundResultPayload = vp_compile(RoundResultPayload)

 
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
        .add_key("my_key", "curve25519", KEY_FILE1) 
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