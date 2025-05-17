"""
Solana Client for XAAM Backend

This module provides a client for interacting with the XAAM Solana program.
It handles operations like creating task NFTs, staking, and distributing rewards.
"""

import json
import os
import base64
from typing import List, Dict, Any, Optional
from pathlib import Path

import solana
import nacl.signing
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT as SYSVAR_RENT_PUBKEY
from solana.rpc.commitment import Confirmed
from solders.transaction import Transaction
from solders.pubkey import Pubkey as PublicKey

# Define a Keypair class that uses nacl
class Keypair:
    """Keypair class using PyNaCl for cryptographic operations."""
    
    def __init__(self, secret_key=None):
        """
        Initialize a keypair either from a provided secret key or generate a new one.
        
        Args:
            secret_key: Optional bytes of the secret key
        """
        if secret_key is not None:
            self.signing_key = nacl.signing.SigningKey(secret_key)
        else:
            self.signing_key = nacl.signing.SigningKey.generate()
        
        self.verify_key = self.signing_key.verify_key
        self.secret_key = self.signing_key.encode()
        self.public_key = PublicKey(self.verify_key.encode())
    
    @classmethod
    def from_secret_key(cls, secret_key):
        """
        Create a keypair from a secret key.
        
        Args:
            secret_key: Bytes of the secret key
            
        Returns:
            Keypair instance
        """
        return cls(secret_key)

# Import XAAM instruction helpers (these would be generated from the Solana program)
# For the demo, we'll mock these functions

class SolanaClient:
    """Client for interacting with the XAAM Solana program."""
    
    def __init__(self, rpc_url: str = None, keypair_path: str = None):
        """
        Initialize the Solana client.
        
        Args:
            rpc_url: URL of the Solana RPC endpoint
            keypair_path: Path to the keypair file
        """
        # Use environment variables if not provided
        self.rpc_url = rpc_url or os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
        keypair_path = keypair_path or os.getenv("SOLANA_KEYPAIR_PATH", "keypair.json")
        
        # Initialize Solana client
        self.client = Client(self.rpc_url)
        
        # Load keypair
        try:
            with open(keypair_path, 'r') as f:
                secret_key = json.load(f)
                self.keypair = Keypair.from_secret_key(bytes(secret_key))
        except (FileNotFoundError, json.JSONDecodeError):
            # Generate new keypair if file doesn't exist or is invalid
            self.keypair = Keypair()
            # Save keypair
            dir_path = os.path.dirname(keypair_path)
            if dir_path:  # Only create directories if there's a directory part in the path
                os.makedirs(dir_path, exist_ok=True)
            with open(keypair_path, 'w') as f:
                json.dump(list(self.keypair.secret_key), f)
        
        # Load program ID
        program_id_path = Path(__file__).parent.parent.parent.parent / "solana" / "program_id.json"
        try:
            with open(program_id_path, 'r') as f:
                program_data = json.load(f)
                self.program_id = PublicKey.from_string(program_data["programId"])
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            # Use a default program ID if file doesn't exist or is invalid
            # This should be replaced with the actual program ID after deployment
            # Convert string to bytes for solders 0.14.4 compatibility
            self.program_id = PublicKey.from_string("11111111111111111111111111111111")
    
    async def create_task_nft(
        self,
        title: str,
        summary: str,
        encrypted_payload_url: str,
        deadline: int,
        reward_amount: int,
        reward_currency: str,
        judges: List[str]
    ) -> Dict[str, Any]:
        """
        Create a new task NFT on the Solana blockchain.
        
        Args:
            title: Task title
            summary: Task summary
            encrypted_payload_url: URL to the encrypted task payload
            deadline: Task deadline (Unix timestamp)
            reward_amount: Reward amount (in lamports)
            reward_currency: Reward currency (e.g., "USDC")
            judges: List of judge public keys
        
        Returns:
            Dict containing the transaction signature and task account public key
        """
        # For the demo, we'll mock the actual Solana interaction
        # In a real implementation, this would create a transaction to call the
        # InitializeTask instruction in the XAAM program
        
        # Generate a new keypair for the task account
        task_keypair = Keypair()
        
        # Mock transaction signature
        signature = f"mock_signature_{base64.b64encode(os.urandom(8)).decode('utf-8')}"
        
        # Log the operation
        print(f"Creating task NFT: {title}")
        print(f"Task account: {task_keypair.public_key}")
        print(f"Transaction signature: {signature}")
        
        return {
            "signature": signature,
            "task_account": str(task_keypair.public_key),
            "task_nft": str(task_keypair.public_key),  # In a real implementation, this would be different
        }
    
    async def stake_on_task(
        self,
        agent_public_key: str,
        task_account: str,
        amount: int
    ) -> Dict[str, Any]:
        """
        Stake SOL on a task to access its details.
        
        Args:
            agent_public_key: Public key of the agent staking
            task_account: Public key of the task account
            amount: Stake amount (in lamports)
        
        Returns:
            Dict containing the transaction signature and stake account public key
        """
        # For the demo, we'll mock the actual Solana interaction
        # In a real implementation, this would create a transaction to call the
        # StakeOnTask instruction in the XAAM program
        
        # Generate a new keypair for the stake account
        stake_keypair = Keypair()
        
        # Mock transaction signature
        signature = f"mock_signature_{base64.b64encode(os.urandom(8)).decode('utf-8')}"
        
        # Log the operation
        print(f"Staking on task: {task_account}")
        print(f"Agent: {agent_public_key}")
        print(f"Amount: {amount} lamports")
        print(f"Stake account: {stake_keypair.public_key}")
        print(f"Transaction signature: {signature}")
        
        return {
            "signature": signature,
            "stake_account": str(stake_keypair.public_key),
        }
    
    async def submit_deliverable(
        self,
        agent_public_key: str,
        task_account: str,
        encrypted_content_url: str,
        encryption_keys: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Submit a deliverable for a task.
        
        Args:
            agent_public_key: Public key of the agent submitting
            task_account: Public key of the task account
            encrypted_content_url: URL to the encrypted deliverable content
            encryption_keys: Dict mapping judge public keys to encrypted keys
        
        Returns:
            Dict containing the transaction signature and deliverable account public key
        """
        # For the demo, we'll mock the actual Solana interaction
        # In a real implementation, this would create a transaction to call the
        # SubmitDeliverable instruction in the XAAM program
        
        # Generate a new keypair for the deliverable account
        deliverable_keypair = Keypair()
        
        # Mock transaction signature
        signature = f"mock_signature_{base64.b64encode(os.urandom(8)).decode('utf-8')}"
        
        # Log the operation
        print(f"Submitting deliverable for task: {task_account}")
        print(f"Agent: {agent_public_key}")
        print(f"Deliverable account: {deliverable_keypair.public_key}")
        print(f"Transaction signature: {signature}")
        
        return {
            "signature": signature,
            "deliverable_account": str(deliverable_keypair.public_key),
        }
    
    async def judge_deliverable(
        self,
        judge_public_key: str,
        deliverable_account: str,
        score: int,
        feedback: str
    ) -> Dict[str, Any]:
        """
        Judge a deliverable.
        
        Args:
            judge_public_key: Public key of the judge
            deliverable_account: Public key of the deliverable account
            score: Score (0-100)
            feedback: Feedback text
        
        Returns:
            Dict containing the transaction signature
        """
        # For the demo, we'll mock the actual Solana interaction
        # In a real implementation, this would create a transaction to call the
        # JudgeDeliverable instruction in the XAAM program
        
        # Mock transaction signature
        signature = f"mock_signature_{base64.b64encode(os.urandom(8)).decode('utf-8')}"
        
        # Log the operation
        print(f"Judging deliverable: {deliverable_account}")
        print(f"Judge: {judge_public_key}")
        print(f"Score: {score}")
        print(f"Transaction signature: {signature}")
        
        return {
            "signature": signature,
        }
    
    async def complete_task(
        self,
        creator_public_key: str,
        task_account: str,
        winning_agent_public_key: str
    ) -> Dict[str, Any]:
        """
        Complete a task and distribute rewards.
        
        Args:
            creator_public_key: Public key of the task creator
            task_account: Public key of the task account
            winning_agent_public_key: Public key of the winning agent
        
        Returns:
            Dict containing the transaction signature
        """
        # For the demo, we'll mock the actual Solana interaction
        # In a real implementation, this would create a transaction to call the
        # CompleteTask instruction in the XAAM program
        
        # Mock transaction signature
        signature = f"mock_signature_{base64.b64encode(os.urandom(8)).decode('utf-8')}"
        
        # Log the operation
        print(f"Completing task: {task_account}")
        print(f"Creator: {creator_public_key}")
        print(f"Winning agent: {winning_agent_public_key}")
        print(f"Transaction signature: {signature}")
        
        return {
            "signature": signature,
        }
    
    async def get_account_balance(self, public_key: str) -> int:
        """
        Get the SOL balance of an account.
        
        Args:
            public_key: Public key of the account
        
        Returns:
            Balance in lamports
        """
        try:
            print(f"Getting balance for: {public_key}")
            pubkey = PublicKey.from_string(public_key)
            print(f"Converted public key: {pubkey}")
            response = self.client.get_balance(pubkey)
            print(f"Balance response: {response}")
            
            # In solders 0.14.4, the response is a GetBalanceResp object
            if hasattr(response, "value"):
                # If response has a value attribute directly
                return response.value
            elif hasattr(response, "context") and hasattr(response, "value"):
                # Some versions might have context and value attributes
                return response.value
            elif isinstance(response, dict) and "result" in response:
                # Older versions returned a dictionary
                if isinstance(response["result"], dict) and "value" in response["result"]:
                    return response["result"]["value"]
                else:
                    return response["result"]
            else:
                # Try to extract the value from the string representation
                response_str = str(response)
                print(f"Response string: {response_str}")
                import re
                match = re.search(r'value=(\d+)', response_str)
                if match:
                    return int(match.group(1))
                
                print("Unable to extract balance from response")
                return 0
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            print(f"Error getting balance: {e}")
            print(f"Error type: {type(e)}")
            print(f"Traceback: {error_traceback}")
            return 0
    
    async def airdrop(self, public_key: str, amount: int = 1000000000) -> Optional[str]:
        """
        Request an airdrop of SOL to an account (only works on devnet and testnet).
        
        Args:
            public_key: Public key of the account
            amount: Amount in lamports (default: 1 SOL)
        
        Returns:
            Transaction signature if successful, None otherwise
        """
        try:
            print(f"Attempting airdrop of {amount} lamports to {public_key}")
            print(f"Using RPC URL: {self.rpc_url}")
            pubkey = PublicKey.from_string(public_key)
            print(f"Converted public key: {pubkey}")
            response = self.client.request_airdrop(pubkey, amount)
            print(f"Airdrop response: {response}")
            
            # In solders 0.14.4, the response is a RequestAirdropResp object with a Signature
            # Extract the signature as a string
            if hasattr(response, "value"):
                # If response has a value attribute (newer versions)
                return str(response.value)
            elif hasattr(response, "__str__"):
                # Otherwise, convert the whole response to a string
                signature_str = str(response)
                # Extract just the signature part from the string representation
                # Format is typically: RequestAirdropResp(Signature(abc123...))
                if "Signature" in signature_str:
                    # Extract the signature part between the parentheses
                    import re
                    match = re.search(r'Signature\((.*?)\)', signature_str)
                    if match:
                        return match.group(1)
                return signature_str
            else:
                print("Unable to extract signature from response")
                return None
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            print(f"Error requesting airdrop: {e}")
            print(f"Error type: {type(e)}")
            print(f"Traceback: {error_traceback}")
            # Re-raise the exception to propagate it to the caller
            raise e