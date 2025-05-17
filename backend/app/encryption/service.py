import os
import base64
import json
import logging
from typing import Dict, Tuple, Optional, Any
from uuid import UUID

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import SHA256

logger = logging.getLogger(__name__)

class EncryptionService:
    """
    Service for handling encryption and decryption operations in the XAAM platform.
    Uses asymmetric encryption (RSA) for key exchange and symmetric encryption (AES) for data.
    """
    
    def __init__(self, key_storage_dir: str = None):
        """
        Initialize the encryption service.
        
        Args:
            key_storage_dir: Directory to store keys. If None, keys will not be persisted.
        """
        self.key_storage_dir = key_storage_dir
        if key_storage_dir and not os.path.exists(key_storage_dir):
            os.makedirs(key_storage_dir, exist_ok=True)
    
    def generate_key_pair(self, key_size: int = 2048) -> Tuple[str, str]:
        """
        Generate a new RSA key pair.
        
        Args:
            key_size: Size of the RSA key in bits
            
        Returns:
            Tuple of (public_key, private_key) as PEM strings
        """
        key = RSA.generate(key_size)
        private_key = key.export_key().decode('utf-8')
        public_key = key.publickey().export_key().decode('utf-8')
        
        return public_key, private_key
    
    def store_private_key(self, agent_id: UUID, private_key: str) -> bool:
        """
        Store a private key securely.
        
        Args:
            agent_id: ID of the agent
            private_key: Private key as PEM string
            
        Returns:
            True if successful, False otherwise
        """
        if not self.key_storage_dir:
            logger.warning("Key storage directory not set, cannot store private key")
            return False
        
        try:
            key_path = os.path.join(self.key_storage_dir, f"{agent_id}_private.pem")
            with open(key_path, 'w') as f:
                f.write(private_key)
            os.chmod(key_path, 0o600)  # Restrict permissions to owner only
            return True
        except Exception as e:
            logger.error(f"Error storing private key: {e}")
            return False
    
    def retrieve_private_key(self, agent_id: UUID) -> Optional[str]:
        """
        Retrieve a private key.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Private key as PEM string or None if not found
        """
        if not self.key_storage_dir:
            logger.warning("Key storage directory not set, cannot retrieve private key")
            return None
        
        try:
            key_path = os.path.join(self.key_storage_dir, f"{agent_id}_private.pem")
            if not os.path.exists(key_path):
                return None
            
            with open(key_path, 'r') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error retrieving private key: {e}")
            return None
    
    def encrypt_with_public_key(self, public_key: str, data: bytes) -> bytes:
        """
        Encrypt data with a public key.
        
        Args:
            public_key: Public key as PEM string
            data: Data to encrypt
            
        Returns:
            Encrypted data
        """
        try:
            key = RSA.import_key(public_key)
            cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
            
            # RSA can only encrypt data up to a certain size, so we use a hybrid approach:
            # 1. Generate a random AES key
            # 2. Encrypt the data with the AES key
            # 3. Encrypt the AES key with the RSA public key
            # 4. Return the encrypted AES key and the encrypted data
            
            aes_key = get_random_bytes(32)  # 256-bit key
            cipher_aes = AES.new(aes_key, AES.MODE_CBC)
            
            # Pad the data to be a multiple of the block size
            padded_data = pad(data, AES.block_size)
            encrypted_data = cipher_aes.encrypt(padded_data)
            
            # Encrypt the AES key with the RSA public key
            encrypted_aes_key = cipher.encrypt(aes_key)
            
            # Combine the IV, encrypted AES key, and encrypted data
            result = {
                'iv': base64.b64encode(cipher_aes.iv).decode('utf-8'),
                'encrypted_key': base64.b64encode(encrypted_aes_key).decode('utf-8'),
                'encrypted_data': base64.b64encode(encrypted_data).decode('utf-8')
            }
            
            return base64.b64encode(json.dumps(result).encode('utf-8'))
        except Exception as e:
            logger.error(f"Error encrypting with public key: {e}")
            raise
    
    def decrypt_with_private_key(self, private_key: str, encrypted_data: bytes) -> bytes:
        """
        Decrypt data with a private key.
        
        Args:
            private_key: Private key as PEM string
            encrypted_data: Data to decrypt
            
        Returns:
            Decrypted data
        """
        try:
            key = RSA.import_key(private_key)
            cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
            
            # Decode the encrypted data
            encrypted_package = json.loads(base64.b64decode(encrypted_data).decode('utf-8'))
            iv = base64.b64decode(encrypted_package['iv'])
            encrypted_key = base64.b64decode(encrypted_package['encrypted_key'])
            encrypted_data = base64.b64decode(encrypted_package['encrypted_data'])
            
            # Decrypt the AES key with the RSA private key
            aes_key = cipher.decrypt(encrypted_key)
            
            # Decrypt the data with the AES key
            cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv)
            padded_data = cipher_aes.decrypt(encrypted_data)
            
            # Unpad the data
            return unpad(padded_data, AES.block_size)
        except Exception as e:
            logger.error(f"Error decrypting with private key: {e}")
            raise
    
    def encrypt_task_payload(self, payload: Dict[str, Any], judge_public_keys: Dict[str, str]) -> Dict[str, str]:
        """
        Encrypt a task payload for multiple judges.
        
        Args:
            payload: Task payload to encrypt
            judge_public_keys: Dict of judge_id -> public_key
            
        Returns:
            Dict of judge_id -> encrypted_key
        """
        try:
            # Convert payload to JSON and encode as bytes
            payload_bytes = json.dumps(payload).encode('utf-8')
            
            # Generate a random AES key for the payload
            aes_key = get_random_bytes(32)  # 256-bit key
            cipher_aes = AES.new(aes_key, AES.MODE_CBC)
            
            # Encrypt the payload with the AES key
            padded_data = pad(payload_bytes, AES.block_size)
            encrypted_payload = cipher_aes.encrypt(padded_data)
            
            # Create the encrypted payload package
            encrypted_payload_package = {
                'iv': base64.b64encode(cipher_aes.iv).decode('utf-8'),
                'encrypted_data': base64.b64encode(encrypted_payload).decode('utf-8')
            }
            
            # Encrypt the AES key with each judge's public key
            encrypted_keys = {}
            for judge_id, public_key in judge_public_keys.items():
                key = RSA.import_key(public_key)
                cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
                encrypted_key = cipher.encrypt(aes_key)
                encrypted_keys[judge_id] = base64.b64encode(encrypted_key).decode('utf-8')
            
            # Return the encrypted payload package and encrypted keys
            return {
                'encrypted_payload': base64.b64encode(json.dumps(encrypted_payload_package).encode('utf-8')).decode('utf-8'),
                'encrypted_keys': encrypted_keys
            }
        except Exception as e:
            logger.error(f"Error encrypting task payload: {e}")
            raise
    
    def decrypt_task_payload(self, encrypted_payload: str, encrypted_key: str, private_key: str) -> Dict[str, Any]:
        """
        Decrypt a task payload.
        
        Args:
            encrypted_payload: Encrypted payload
            encrypted_key: Encrypted AES key
            private_key: Private key as PEM string
            
        Returns:
            Decrypted payload as a dict
        """
        try:
            # Import the private key
            key = RSA.import_key(private_key)
            cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
            
            # Decrypt the AES key
            encrypted_key_bytes = base64.b64decode(encrypted_key)
            aes_key = cipher.decrypt(encrypted_key_bytes)
            
            # Decode the encrypted payload package
            encrypted_payload_package = json.loads(base64.b64decode(encrypted_payload).decode('utf-8'))
            iv = base64.b64decode(encrypted_payload_package['iv'])
            encrypted_data = base64.b64decode(encrypted_payload_package['encrypted_data'])
            
            # Decrypt the payload with the AES key
            cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv)
            padded_data = cipher_aes.decrypt(encrypted_data)
            payload_bytes = unpad(padded_data, AES.block_size)
            
            # Parse the payload as JSON
            return json.loads(payload_bytes.decode('utf-8'))
        except Exception as e:
            logger.error(f"Error decrypting task payload: {e}")
            raise
    
    def encrypt_deliverable(self, deliverable: Dict[str, Any], judge_public_keys: Dict[str, str]) -> Dict[str, Any]:
        """
        Encrypt a deliverable for multiple judges.
        
        Args:
            deliverable: Deliverable to encrypt
            judge_public_keys: Dict of judge_id -> public_key
            
        Returns:
            Dict with encrypted_content and encrypted_keys
        """
        try:
            # Convert deliverable to JSON and encode as bytes
            deliverable_bytes = json.dumps(deliverable).encode('utf-8')
            
            # Generate a random AES key for the deliverable
            aes_key = get_random_bytes(32)  # 256-bit key
            cipher_aes = AES.new(aes_key, AES.MODE_CBC)
            
            # Encrypt the deliverable with the AES key
            padded_data = pad(deliverable_bytes, AES.block_size)
            encrypted_deliverable = cipher_aes.encrypt(padded_data)
            
            # Create the encrypted deliverable package
            encrypted_deliverable_package = {
                'iv': base64.b64encode(cipher_aes.iv).decode('utf-8'),
                'encrypted_data': base64.b64encode(encrypted_deliverable).decode('utf-8')
            }
            
            # Encrypt the AES key with each judge's public key
            encrypted_keys = {}
            for judge_id, public_key in judge_public_keys.items():
                key = RSA.import_key(public_key)
                cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
                encrypted_key = cipher.encrypt(aes_key)
                encrypted_keys[judge_id] = base64.b64encode(encrypted_key).decode('utf-8')
            
            # Return the encrypted deliverable package and encrypted keys
            return {
                'encrypted_content': base64.b64encode(json.dumps(encrypted_deliverable_package).encode('utf-8')).decode('utf-8'),
                'encrypted_keys': encrypted_keys
            }
        except Exception as e:
            logger.error(f"Error encrypting deliverable: {e}")
            raise
    
    def decrypt_deliverable(self, encrypted_content: str, encrypted_key: str, private_key: str) -> Dict[str, Any]:
        """
        Decrypt a deliverable.
        
        Args:
            encrypted_content: Encrypted deliverable content
            encrypted_key: Encrypted AES key
            private_key: Private key as PEM string
            
        Returns:
            Decrypted deliverable as a dict
        """
        try:
            # Import the private key
            key = RSA.import_key(private_key)
            cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
            
            # Decrypt the AES key
            encrypted_key_bytes = base64.b64decode(encrypted_key)
            aes_key = cipher.decrypt(encrypted_key_bytes)
            
            # Decode the encrypted deliverable package
            encrypted_deliverable_package = json.loads(base64.b64decode(encrypted_content).decode('utf-8'))
            iv = base64.b64decode(encrypted_deliverable_package['iv'])
            encrypted_data = base64.b64decode(encrypted_deliverable_package['encrypted_data'])
            
            # Decrypt the deliverable with the AES key
            cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv)
            padded_data = cipher_aes.decrypt(encrypted_data)
            deliverable_bytes = unpad(padded_data, AES.block_size)
            
            # Parse the deliverable as JSON
            return json.loads(deliverable_bytes.decode('utf-8'))
        except Exception as e:
            logger.error(f"Error decrypting deliverable: {e}")
            raise


# Create a singleton instance
encryption_service = EncryptionService(key_storage_dir=os.environ.get('KEY_STORAGE_DIR', '/tmp/xaam_keys'))