import logging
from typing import Optional, List, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.agent import Agent
from app.encryption.service import encryption_service

logger = logging.getLogger(__name__)

class KeyManagementService:
    """
    Service for managing encryption keys in the database.
    """
    
    async def generate_keys_for_agent(self, db: AsyncSession, agent_id: UUID) -> bool:
        """
        Generate a new key pair for an agent and store the public key in the database.
        The private key is stored securely in the key storage directory.
        
        Args:
            db: Database session
            agent_id: ID of the agent
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the agent
            agent = await db.get(Agent, agent_id)
            if not agent:
                logger.error(f"Agent {agent_id} not found")
                return False
            
            # Generate a new key pair
            public_key, private_key = encryption_service.generate_key_pair()
            
            # Store the public key in the database
            agent.public_key = public_key
            db.add(agent)
            await db.commit()
            
            # Store the private key securely
            success = encryption_service.store_private_key(agent_id, private_key)
            if not success:
                logger.error(f"Failed to store private key for agent {agent_id}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error generating keys for agent {agent_id}: {e}")
            await db.rollback()
            return False
    
    async def get_agent_public_key(self, db: AsyncSession, agent_id: UUID) -> Optional[str]:
        """
        Get the public key for an agent.
        
        Args:
            db: Database session
            agent_id: ID of the agent
            
        Returns:
            Public key as PEM string or None if not found
        """
        try:
            agent = await db.get(Agent, agent_id)
            if not agent:
                logger.error(f"Agent {agent_id} not found")
                return None
            
            return agent.public_key
        except Exception as e:
            logger.error(f"Error getting public key for agent {agent_id}: {e}")
            return None
    
    async def get_agent_private_key(self, agent_id: UUID) -> Optional[str]:
        """
        Get the private key for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Private key as PEM string or None if not found
        """
        return encryption_service.retrieve_private_key(agent_id)
    
    async def get_judge_public_keys(self, db: AsyncSession, judge_ids: List[UUID]) -> Dict[str, str]:
        """
        Get the public keys for multiple judges.
        
        Args:
            db: Database session
            judge_ids: List of judge IDs
            
        Returns:
            Dict of judge_id -> public_key
        """
        try:
            result = {}
            for judge_id in judge_ids:
                public_key = await self.get_agent_public_key(db, judge_id)
                if public_key:
                    result[str(judge_id)] = public_key
            
            return result
        except Exception as e:
            logger.error(f"Error getting public keys for judges: {e}")
            return {}


# Create a singleton instance
key_management_service = KeyManagementService()