import pytest
import json
import base64
from unittest.mock import patch, MagicMock
import os
import tempfile
from uuid import UUID, uuid4

from app.encryption.service import EncryptionService
from app.encryption.db_service import KeyManagementService


class TestEncryptionService:
    """Tests for the EncryptionService class"""
    
    @pytest.fixture
    def encryption_service(self):
        """Create a temporary encryption service for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield EncryptionService(key_storage_dir=temp_dir)
    
    def test_generate_key_pair(self, encryption_service):
        """Test generating a key pair"""
        public_key, private_key = encryption_service.generate_key_pair()
        
        # Check that keys are returned as strings
        assert isinstance(public_key, str)
        assert isinstance(private_key, str)
        
        # Check that keys are not empty
        assert public_key
        assert private_key
        
        # Check that keys are different
        assert public_key != private_key
    
    def test_store_and_retrieve_private_key(self, encryption_service):
        """Test storing and retrieving a private key"""
        agent_id = uuid4()
        _, private_key = encryption_service.generate_key_pair()
        
        # Store the private key
        success = encryption_service.store_private_key(agent_id, private_key)
        assert success
        
        # Retrieve the private key
        retrieved_key = encryption_service.retrieve_private_key(agent_id)
        assert retrieved_key == private_key
    
    def test_encrypt_and_decrypt_with_public_key(self, encryption_service):
        """Test encrypting and decrypting data with a public key"""
        public_key, private_key = encryption_service.generate_key_pair()
        
        # Test data
        test_data = b"This is a test message"
        
        # Encrypt the data
        encrypted_data = encryption_service.encrypt_with_public_key(public_key, test_data)
        
        # Decrypt the data
        decrypted_data = encryption_service.decrypt_with_private_key(private_key, encrypted_data)
        
        # Check that the decrypted data matches the original
        assert decrypted_data == test_data
    
    def test_encrypt_and_decrypt_task_payload(self, encryption_service):
        """Test encrypting and decrypting a task payload"""
        # Generate key pairs for judges
        judge1_id = str(uuid4())
        judge1_public_key, judge1_private_key = encryption_service.generate_key_pair()
        
        judge2_id = str(uuid4())
        judge2_public_key, judge2_private_key = encryption_service.generate_key_pair()
        
        # Create a test payload
        payload = {
            "description": "This is a test task",
            "requirements": ["req1", "req2"],
            "data": {"key": "value"}
        }
        
        # Create a map of judge IDs to public keys
        judge_public_keys = {
            judge1_id: judge1_public_key,
            judge2_id: judge2_public_key
        }
        
        # Encrypt the payload
        encryption_result = encryption_service.encrypt_task_payload(payload, judge_public_keys)
        
        # Check that the result contains the expected keys
        assert "encrypted_payload" in encryption_result
        assert "encrypted_keys" in encryption_result
        assert judge1_id in encryption_result["encrypted_keys"]
        assert judge2_id in encryption_result["encrypted_keys"]
        
        # Decrypt the payload with judge1's private key
        decrypted_payload = encryption_service.decrypt_task_payload(
            encryption_result["encrypted_payload"],
            encryption_result["encrypted_keys"][judge1_id],
            judge1_private_key
        )
        
        # Check that the decrypted payload matches the original
        assert decrypted_payload == payload
        
        # Decrypt the payload with judge2's private key
        decrypted_payload = encryption_service.decrypt_task_payload(
            encryption_result["encrypted_payload"],
            encryption_result["encrypted_keys"][judge2_id],
            judge2_private_key
        )
        
        # Check that the decrypted payload matches the original
        assert decrypted_payload == payload
    
    def test_encrypt_and_decrypt_deliverable(self, encryption_service):
        """Test encrypting and decrypting a deliverable"""
        # Generate key pairs for judges
        judge1_id = str(uuid4())
        judge1_public_key, judge1_private_key = encryption_service.generate_key_pair()
        
        judge2_id = str(uuid4())
        judge2_public_key, judge2_private_key = encryption_service.generate_key_pair()
        
        # Create a test deliverable
        deliverable = {
            "content": "This is a test deliverable",
            "files": ["file1.txt", "file2.txt"],
            "metadata": {"author": "Test Agent"}
        }
        
        # Create a map of judge IDs to public keys
        judge_public_keys = {
            judge1_id: judge1_public_key,
            judge2_id: judge2_public_key
        }
        
        # Encrypt the deliverable
        encryption_result = encryption_service.encrypt_deliverable(deliverable, judge_public_keys)
        
        # Check that the result contains the expected keys
        assert "encrypted_content" in encryption_result
        assert "encrypted_keys" in encryption_result
        assert judge1_id in encryption_result["encrypted_keys"]
        assert judge2_id in encryption_result["encrypted_keys"]
        
        # Decrypt the deliverable with judge1's private key
        decrypted_deliverable = encryption_service.decrypt_deliverable(
            encryption_result["encrypted_content"],
            encryption_result["encrypted_keys"][judge1_id],
            judge1_private_key
        )
        
        # Check that the decrypted deliverable matches the original
        assert decrypted_deliverable == deliverable
        
        # Decrypt the deliverable with judge2's private key
        decrypted_deliverable = encryption_service.decrypt_deliverable(
            encryption_result["encrypted_content"],
            encryption_result["encrypted_keys"][judge2_id],
            judge2_private_key
        )
        
        # Check that the decrypted deliverable matches the original
        assert decrypted_deliverable == deliverable


@pytest.mark.asyncio
class TestKeyManagementService:
    """Tests for the KeyManagementService class"""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        db = MagicMock()
        return db
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent"""
        agent = MagicMock()
        agent.id = uuid4()
        agent.public_key = None
        return agent
    
    @patch('backend.app.encryption.db_service.encryption_service')
    async def test_generate_keys_for_agent(self, mock_encryption_service, mock_db, mock_agent):
        """Test generating keys for an agent"""
        # Setup mock
        mock_db.get.return_value = mock_agent
        mock_encryption_service.generate_key_pair.return_value = ("public_key", "private_key")
        mock_encryption_service.store_private_key.return_value = True
        
        # Create service
        service = KeyManagementService()
        
        # Generate keys
        result = await service.generate_keys_for_agent(mock_db, mock_agent.id)
        
        # Check result
        assert result is True
        
        # Check that the agent's public key was updated
        assert mock_agent.public_key == "public_key"
        
        # Check that the private key was stored
        mock_encryption_service.store_private_key.assert_called_once_with(mock_agent.id, "private_key")
    
    @patch('backend.app.encryption.db_service.encryption_service')
    async def test_get_agent_public_key(self, mock_encryption_service, mock_db, mock_agent):
        """Test getting an agent's public key"""
        # Setup mock
        mock_agent.public_key = "test_public_key"
        mock_db.get.return_value = mock_agent
        
        # Create service
        service = KeyManagementService()
        
        # Get public key
        public_key = await service.get_agent_public_key(mock_db, mock_agent.id)
        
        # Check result
        assert public_key == "test_public_key"
    
    @patch('backend.app.encryption.db_service.encryption_service')
    async def test_get_agent_private_key(self, mock_encryption_service, mock_db):
        """Test getting an agent's private key"""
        # Setup mock
        agent_id = uuid4()
        mock_encryption_service.retrieve_private_key.return_value = "test_private_key"
        
        # Create service
        service = KeyManagementService()
        
        # Get private key
        private_key = await service.get_agent_private_key(agent_id)
        
        # Check result
        assert private_key == "test_private_key"
        
        # Check that the private key was retrieved
        mock_encryption_service.retrieve_private_key.assert_called_once_with(agent_id)
    
    @patch('backend.app.encryption.db_service.encryption_service')
    async def test_get_judge_public_keys(self, mock_encryption_service, mock_db):
        """Test getting public keys for multiple judges"""
        # Setup mocks
        judge1_id = uuid4()
        judge2_id = uuid4()
        
        # Create service with a mock for get_agent_public_key
        service = KeyManagementService()
        service.get_agent_public_key = MagicMock()
        service.get_agent_public_key.side_effect = [
            "judge1_public_key",
            "judge2_public_key"
        ]
        
        # Get public keys
        public_keys = await service.get_judge_public_keys(mock_db, [judge1_id, judge2_id])
        
        # Check result
        assert public_keys == {
            str(judge1_id): "judge1_public_key",
            str(judge2_id): "judge2_public_key"
        }