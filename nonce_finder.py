import hashlib
import struct
from dotenv import load_dotenv
import os

def mine(email: str, github_url: str) -> int:
    """
    Find a nonce such that SHA256(email\ngithub_url\nnonce_8bytes) 
    has 28 leading zero bits.
    """
    data_prefix = email.encode("utf-8") + b"\n" + github_url.encode("utf-8") + b"\n"
    
    nonce = 0
    while True:
        # Converts nonce into big-endian (>), signed 64-bit integer (q)
        nonce_bytes = struct.pack(">q", nonce)

        digest = hashlib.sha256(data_prefix + nonce_bytes).digest()
        
        # With 28 leading zero bits, the first 3 bytes are 0x00 and the 4th byte is < 16
        if digest[0] == 0 and digest[1] == 0 and digest[2] == 0 and digest[3] < 16:
            print(f"Found nonce: {nonce}")
            return nonce
        
        # Print progress
        if nonce % 1_000_000 == 0:
            print(f"  Tried {nonce:,} nonces so far...")
        
        nonce += 1

if __name__ == "__main__":
    load_dotenv()
    EMAIL = os.getenv("EMAIL")
    if not EMAIL:
        raise ValueError("EMAIL not set in .env file")
    GITHUB_URL = "https://github.com/hanna1231/BlockchainEngineering"
    
    print(f"Mining for: {EMAIL}, {GITHUB_URL}")
    result = mine(EMAIL, GITHUB_URL)
    print(f"\nFound nonce: {result}")