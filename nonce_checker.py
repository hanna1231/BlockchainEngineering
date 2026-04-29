import hashlib
import struct

EMAIL = "h.h.p.straathof-1@student.tudelft.nl"
GITHUB_URL = "https://github.com/hanna1231/BlockchainEngineering"
NONCE = 78696929  # ← your found nonce

data = EMAIL.encode("utf-8") + b"\n" + GITHUB_URL.encode("utf-8") + b"\n" + struct.pack(">q", NONCE)
digest = hashlib.sha256(data).digest()

print(f"Hash: {digest.hex()}")
print(f"First 4 bytes: {list(digest[:4])}")
print(f"Valid: {digest[0] == 0 and digest[1] == 0 and digest[2] == 0 and digest[3] < 16}")