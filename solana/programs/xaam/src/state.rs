//! State definitions for the XAAM program

use borsh::{BorshDeserialize, BorshSerialize};
use solana_program::{
    program_pack::{IsInitialized, Sealed},
    pubkey::Pubkey,
    clock::UnixTimestamp,
};

/// Task status enum
#[derive(BorshSerialize, BorshDeserialize, Clone, Debug, PartialEq)]
pub enum TaskStatus {
    Created,
    Staked,
    InProgress,
    Submitted,
    Judged,
    Completed,
}

/// Agent type enum
#[derive(BorshSerialize, BorshDeserialize, Clone, Debug, PartialEq)]
pub enum AgentType {
    Worker,
    Judge,
}

/// Stake status enum
#[derive(BorshSerialize, BorshDeserialize, Clone, Debug, PartialEq)]
pub enum StakeStatus {
    Active,
    Returned,
    Forfeited,
}

/// Deliverable status enum
#[derive(BorshSerialize, BorshDeserialize, Clone, Debug, PartialEq)]
pub enum DeliverableStatus {
    Submitted,
    Judged,
    Accepted,
    Rejected,
}

/// Task state
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct Task {
    /// Is this account initialized
    pub is_initialized: bool,
    /// Task NFT identifier
    pub nft_id: Pubkey,
    /// Task title
    pub title: String,
    /// Task summary
    pub summary: String,
    /// Encrypted payload URL
    pub encrypted_payload_url: String,
    /// Creator ID
    pub creator_id: Pubkey,
    /// Task status
    pub status: TaskStatus,
    /// Task deadline
    pub deadline: UnixTimestamp,
    /// Reward amount
    pub reward_amount: u64,
    /// Reward currency (default: USDC)
    pub reward_currency: String,
    /// Judges (up to 5)
    pub judges: [Option<Pubkey>; 5],
    /// Created at timestamp
    pub created_at: UnixTimestamp,
    /// Updated at timestamp
    pub updated_at: UnixTimestamp,
}

impl Sealed for Task {}

impl IsInitialized for Task {
    fn is_initialized(&self) -> bool {
        self.is_initialized
    }
}

/// Agent state
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct Agent {
    /// Is this account initialized
    pub is_initialized: bool,
    /// Agent name
    pub name: String,
    /// Agent description
    pub description: String,
    /// Agent type
    pub agent_type: AgentType,
    /// Wallet address
    pub wallet_address: Pubkey,
    /// Public key for encryption
    pub public_key: String,
    /// Reputation score
    pub reputation_score: u64,
    /// Completed tasks count
    pub completed_tasks: u32,
    /// Successful tasks count
    pub successful_tasks: u32,
    /// Created at timestamp
    pub created_at: UnixTimestamp,
    /// Updated at timestamp
    pub updated_at: UnixTimestamp,
}

impl Sealed for Agent {}

impl IsInitialized for Agent {
    fn is_initialized(&self) -> bool {
        self.is_initialized
    }
}

/// Judge state (extends Agent)
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct Judge {
    /// Base agent data
    pub agent: Agent,
    /// Specialization
    pub specialization: String,
    /// Judged tasks count
    pub judged_tasks: u32,
}

impl Sealed for Judge {}

impl IsInitialized for Judge {
    fn is_initialized(&self) -> bool {
        self.agent.is_initialized
    }
}

/// Stake state
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct Stake {
    /// Is this account initialized
    pub is_initialized: bool,
    /// Task ID
    pub task_id: Pubkey,
    /// Agent ID
    pub agent_id: Pubkey,
    /// Stake amount
    pub amount: u64,
    /// Stake status
    pub status: StakeStatus,
    /// Staked at timestamp
    pub staked_at: UnixTimestamp,
    /// Released at timestamp
    pub released_at: Option<UnixTimestamp>,
}

impl Sealed for Stake {}

impl IsInitialized for Stake {
    fn is_initialized(&self) -> bool {
        self.is_initialized
    }
}

/// Wallet state
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct Wallet {
    /// Is this account initialized
    pub is_initialized: bool,
    /// Owner
    pub owner: Pubkey,
    /// SOL balance
    pub sol_balance: u64,
    /// USDC balance
    pub usdc_balance: u64,
    /// NFT count
    pub nft_count: u32,
}

impl Sealed for Wallet {}

impl IsInitialized for Wallet {
    fn is_initialized(&self) -> bool {
        self.is_initialized
    }
}