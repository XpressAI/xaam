//! Instruction types for the XAAM program

use borsh::{BorshDeserialize, BorshSerialize};
use solana_program::{
    instruction::{AccountMeta, Instruction},
    pubkey::Pubkey,
    system_program,
    sysvar::rent,
};
use crate::state::{TaskStatus, AgentType, StakeStatus};

/// Instructions supported by the XAAM program
#[derive(BorshSerialize, BorshDeserialize, Clone, Debug, PartialEq)]
pub enum XaamInstruction {
    /// Initialize a new task
    ///
    /// Accounts expected:
    /// 0. `[signer]` The account of the person initializing the task
    /// 1. `[writable]` The task account, it will hold all task data
    /// 2. `[writable]` The NFT mint account
    /// 3. `[]` The rent sysvar
    /// 4. `[]` The token program
    /// 5. `[]` The system program
    InitializeTask {
        /// Task title
        title: String,
        /// Task summary
        summary: String,
        /// Encrypted payload URL
        encrypted_payload_url: String,
        /// Task deadline
        deadline: i64,
        /// Reward amount
        reward_amount: u64,
        /// Reward currency (default: USDC)
        reward_currency: String,
        /// Judges (up to 5)
        judges: Vec<Pubkey>,
    },

    /// Register a new agent
    ///
    /// Accounts expected:
    /// 0. `[signer]` The account of the person registering as an agent
    /// 1. `[writable]` The agent account, it will hold all agent data
    /// 2. `[]` The rent sysvar
    /// 3. `[]` The system program
    RegisterAgent {
        /// Agent name
        name: String,
        /// Agent description
        description: String,
        /// Agent type
        agent_type: AgentType,
        /// Public key for encryption
        public_key: String,
    },

    /// Register a new judge (extends agent)
    ///
    /// Accounts expected:
    /// 0. `[signer]` The account of the person registering as a judge
    /// 1. `[writable]` The judge account, it will hold all judge data
    /// 2. `[writable]` The agent account, it will hold base agent data
    /// 3. `[]` The rent sysvar
    /// 4. `[]` The system program
    RegisterJudge {
        /// Agent name
        name: String,
        /// Agent description
        description: String,
        /// Public key for encryption
        public_key: String,
        /// Specialization
        specialization: String,
    },

    /// Stake on a task
    ///
    /// Accounts expected:
    /// 0. `[signer]` The account of the agent staking
    /// 1. `[writable]` The stake account, it will hold all stake data
    /// 2. `[writable]` The task account, it will be updated with stake info
    /// 3. `[writable]` The agent account
    /// 4. `[]` The rent sysvar
    /// 5. `[]` The system program
    StakeOnTask {
        /// Stake amount
        amount: u64,
    },

    /// Submit a deliverable for a task
    ///
    /// Accounts expected:
    /// 0. `[signer]` The account of the agent submitting
    /// 1. `[writable]` The deliverable account, it will hold all deliverable data
    /// 2. `[writable]` The task account, it will be updated with submission info
    /// 3. `[writable]` The agent account
    /// 4. `[]` The rent sysvar
    /// 5. `[]` The system program
    SubmitDeliverable {
        /// Encrypted content URL
        encrypted_content_url: String,
        /// Encryption keys for judges
        encryption_keys: Vec<(Pubkey, String)>,
    },

    /// Judge a deliverable
    ///
    /// Accounts expected:
    /// 0. `[signer]` The account of the judge
    /// 1. `[writable]` The deliverable account, it will be updated with judging info
    /// 2. `[writable]` The task account
    /// 3. `[writable]` The judge account
    /// 4. `[]` The system program
    JudgeDeliverable {
        /// Score (0-100)
        score: u8,
        /// Feedback
        feedback: String,
    },

    /// Complete a task and distribute rewards
    ///
    /// Accounts expected:
    /// 0. `[signer]` The account of the task creator
    /// 1. `[writable]` The task account
    /// 2. `[writable]` The winning agent account
    /// 3. `[writable]` The task wallet account
    /// 4. `[writable]` The agent wallet account
    /// 5. `[]` The token program
    /// 6. `[]` The system program
    CompleteTask {},

    /// Return stake to an agent
    ///
    /// Accounts expected:
    /// 0. `[signer]` The account of the judge approving stake return
    /// 1. `[writable]` The stake account
    /// 2. `[writable]` The agent account
    /// 3. `[]` The system program
    ReturnStake {},

    /// Burn a task NFT
    ///
    /// Accounts expected:
    /// 0. `[signer]` The account of the task creator
    /// 1. `[writable]` The task account
    /// 2. `[writable]` The NFT mint account
    /// 3. `[]` The token program
    /// 4. `[]` The system program
    BurnTaskNFT {},
}

/// Create InitializeTask instruction
pub fn initialize_task(
    program_id: &Pubkey,
    creator: &Pubkey,
    task: &Pubkey,
    nft_mint: &Pubkey,
    title: String,
    summary: String,
    encrypted_payload_url: String,
    deadline: i64,
    reward_amount: u64,
    reward_currency: String,
    judges: Vec<Pubkey>,
) -> Instruction {
    let data = XaamInstruction::InitializeTask {
        title,
        summary,
        encrypted_payload_url,
        deadline,
        reward_amount,
        reward_currency,
        judges,
    };
    
    let accounts = vec![
        AccountMeta::new(*creator, true),
        AccountMeta::new(*task, false),
        AccountMeta::new(*nft_mint, false),
        AccountMeta::new_readonly(rent::id(), false),
        AccountMeta::new_readonly(spl_token::id(), false),
        AccountMeta::new_readonly(system_program::id(), false),
    ];
    
    Instruction {
        program_id: *program_id,
        accounts,
        data: data.try_to_vec().unwrap(),
    }
}

/// Create RegisterAgent instruction
pub fn register_agent(
    program_id: &Pubkey,
    agent_owner: &Pubkey,
    agent_account: &Pubkey,
    name: String,
    description: String,
    agent_type: AgentType,
    public_key: String,
) -> Instruction {
    let data = XaamInstruction::RegisterAgent {
        name,
        description,
        agent_type,
        public_key,
    };
    
    let accounts = vec![
        AccountMeta::new(*agent_owner, true),
        AccountMeta::new(*agent_account, false),
        AccountMeta::new_readonly(rent::id(), false),
        AccountMeta::new_readonly(system_program::id(), false),
    ];
    
    Instruction {
        program_id: *program_id,
        accounts,
        data: data.try_to_vec().unwrap(),
    }
}

/// Create StakeOnTask instruction
pub fn stake_on_task(
    program_id: &Pubkey,
    agent: &Pubkey,
    stake_account: &Pubkey,
    task_account: &Pubkey,
    agent_account: &Pubkey,
    amount: u64,
) -> Instruction {
    let data = XaamInstruction::StakeOnTask {
        amount,
    };
    
    let accounts = vec![
        AccountMeta::new(*agent, true),
        AccountMeta::new(*stake_account, false),
        AccountMeta::new(*task_account, false),
        AccountMeta::new(*agent_account, false),
        AccountMeta::new_readonly(rent::id(), false),
        AccountMeta::new_readonly(system_program::id(), false),
    ];
    
    Instruction {
        program_id: *program_id,
        accounts,
        data: data.try_to_vec().unwrap(),
    }
}