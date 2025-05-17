from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.wallet import Wallet
from app.schemas.wallet import WalletCreate, WalletUpdate
from app.db.services.base import BaseService


class WalletService(BaseService[Wallet, WalletCreate, WalletUpdate]):
    def __init__(self):
        super().__init__(Wallet)
    
    async def get_by_address(self, db: AsyncSession, address: str) -> Optional[Wallet]:
        """
        Get a wallet by address
        """
        query = select(self.model).where(self.model.address == address)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_by_agent(self, db: AsyncSession, agent_id: UUID) -> Optional[Wallet]:
        """
        Get a wallet by agent ID
        """
        query = select(self.model).where(self.model.agent_id == agent_id)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def update_sol_balance(self, db: AsyncSession, wallet_id: UUID, amount: float, is_addition: bool = True) -> Optional[Wallet]:
        """
        Update a wallet's SOL balance
        """
        wallet = await self.get(db, wallet_id)
        if not wallet:
            return None
        
        if is_addition:
            wallet.sol_balance += amount
        else:
            wallet.sol_balance = max(0, wallet.sol_balance - amount)
        
        db.add(wallet)
        await db.commit()
        await db.refresh(wallet)
        return wallet
    
    async def update_usdc_balance(self, db: AsyncSession, wallet_id: UUID, amount: float, is_addition: bool = True) -> Optional[Wallet]:
        """
        Update a wallet's USDC balance
        """
        wallet = await self.get(db, wallet_id)
        if not wallet:
            return None
        
        if is_addition:
            wallet.usdc_balance += amount
        else:
            wallet.usdc_balance = max(0, wallet.usdc_balance - amount)
        
        db.add(wallet)
        await db.commit()
        await db.refresh(wallet)
        return wallet
    
    async def add_nft(self, db: AsyncSession, wallet_id: UUID, nft_id: str) -> Optional[Wallet]:
        """
        Add an NFT to a wallet
        """
        wallet = await self.get(db, wallet_id)
        if not wallet:
            return None
        
        if not wallet.nfts:
            wallet.nfts = []
        
        if nft_id not in wallet.nfts:
            wallet.nfts.append(nft_id)
        
        db.add(wallet)
        await db.commit()
        await db.refresh(wallet)
        return wallet
    
    async def remove_nft(self, db: AsyncSession, wallet_id: UUID, nft_id: str) -> Optional[Wallet]:
        """
        Remove an NFT from a wallet
        """
        wallet = await self.get(db, wallet_id)
        if not wallet or not wallet.nfts:
            return None
        
        if nft_id in wallet.nfts:
            wallet.nfts.remove(nft_id)
        
        db.add(wallet)
        await db.commit()
        await db.refresh(wallet)
        return wallet


# Create a singleton instance
wallet_service = WalletService()