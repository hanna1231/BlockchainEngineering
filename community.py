import asyncio
from ipv8.community import Community, CommunitySettings
from ipv8.lazy_community import lazy_wrapper
from ipv8.peer import Peer
from ipv8.messaging.lazy_payload import VariablePayload

class SubmissionMessage(VariablePayload):
    msg_id = 1
    names = ["email", "github_url", "nonce"]
    format_list = ["varlenHutf8", "varlenHutf8", "q"]

class ServerResponse(VariablePayload):
    msg_id = 2
    names = ["success", "message"]
    format_list = ["?", "varlenHutf8"]

SERVER_PUBLIC_KEY = bytes.fromhex(
    "4c69624e61434c504b3a86b23934a28d669c390e2d1fc0b0870706c4591cc0cb178bc5a811da6d87d27ef319b2638ef60cc8d119724f4c53a1ebfad919c3ac4136c501ce5c09364e0ebb"
)

class Community(Community):
    # This ID tells IPv8 which community to join
    community_id = bytes.fromhex("2c1cc6e35ff484f99ebdfb6108477783c0102881")

    def __init__(self, settings: CommunitySettings):
        super().__init__(settings)
        # IPv8 calls on_response when a msg_id=2 arrives
        self.add_message_handler(2, self.on_response)
        
        # Store server once found
        self.server_peer: Peer | None = None
        # Prevents sending submission twice
        self.submission_sent = False

    def find_server(self) -> Peer | None:
        """
        Looks through all discovered peers and returns the one whose
        public key matches the known server key.
        """
        for peer in self.get_peers():
            if peer.public_key.key_to_bin() == SERVER_PUBLIC_KEY:
                return peer
        return None

    async def wait_for_server_and_submit(self, email: str, github_url: str, nonce: int):
        """
        Poll until we find the server peer, then send the submission.
        IPv8's walker needs a few seconds to discover peers after startup.
        """
        print("Waiting for server peer discovery...")
        for attempt in range(60):  # wait up to 60 seconds
            server = self.find_server()
            if server:
                print(f"Found server peer.")
                self.server_peer = server
                self.send_submission(email, github_url, nonce)
                return
            await asyncio.sleep(1)
            if attempt % 10 == 9:
                known = len(self.get_peers())
                print(f"  Still searching... ({known} peers found so far)")
        
        print("Server not found after 60 seconds")

    def send_submission(self, email: str, github_url: str, nonce: int):
        if self.submission_sent:
            return
        self.submission_sent = True
        print(f"Sending submission: email={email}, nonce={nonce}")
        # ez_send signs the message with my private key and sends it
        self.ez_send(self.server_peer, SubmissionMessage(email, github_url, nonce))
        print("Submission sent. Waiting for response...")
    
    @lazy_wrapper(ServerResponse)
    def on_response(self, peer: Peer, payload: ServerResponse):
        """Called automatically when the server sends back a response."""
        # Only trust responses from the known server key
        if peer.public_key.key_to_bin() != SERVER_PUBLIC_KEY:
            print(f"Ignoring response from unknown peer")
            return
        
        print("\nServer response:")
        print(f"Success: {payload.success}")
        print(f"Message: {payload.message}")