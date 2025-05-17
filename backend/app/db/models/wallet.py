from sqlalchemy import Column, String, Float, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.models.base import BaseModel

class Wallet(BaseModel):
    """Wallet model for handling USDC transactions"""
    __tablename__ = "wallets"
    
    address = Column(String, nullable=False, unique=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.id'), nullable=False, unique=True)
    sol_balance = Column(Float, default=0.0, nullable=False)
    usdc_balance = Column(Float, default=0.0, nullable=False)
    nfts = Column(ARRAY(String), default=[], nullable=False)
    
    # Relationships
    agent = relationship("Agent", backref="wallet", uselist=False)
    
    def __repr__(self):
        return f"<Wallet(id={self.id}, address='{self.address}', sol_balance={self.sol_balance}, usdc_balance={self.usdc_balance})>"