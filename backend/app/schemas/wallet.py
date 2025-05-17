from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from app.schemas.base import BaseSchema


class WalletBase(BaseModel):
    """Base schema for Wallet"""
    address: Optional[str] = None
    agent_id: Optional[UUID] = None
    sol_balance: Optional[float] = 0.0
    usdc_balance: Optional[float] = 0.0
    nfts: Optional[List[str]] = []


class WalletCreate(WalletBase):
    """Schema for creating a Wallet"""
    address: str
    agent_id: UUID


class WalletUpdate(WalletBase):
    """Schema for updating a Wallet"""
    sol_balance: Optional[float] = None
    usdc_balance: Optional[float] = None
    nfts: Optional[List[str]] = None


class Wallet(WalletBase, BaseSchema):
    """Schema for returning a Wallet"""
    pass