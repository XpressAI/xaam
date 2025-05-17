//! Program state processor

use borsh::{BorshDeserialize, BorshSerialize};
use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint::ProgramResult,
    msg,
    program::{invoke, invoke_signed},
    program_error::ProgramError,
    program_pack::Pack,
    pubkey::Pubkey,
    system_instruction,
    sysvar::{rent::Rent, Sysvar},
    clock::Clock,
};
use crate::{
    error::XaamError,
    instruction::XaamInstruction,
    state::{Agent, AgentType, Judge, Stake, StakeStatus, Task, TaskStatus, Wallet},
};

/// Program state processor
pub struct Processor {}

impl Processor {
    /// Process a XAAM instruction
    pub fn process(
        program_id: &Pubkey,
        accounts: &[AccountInfo],
        instruction: XaamInstruction,
    ) -> ProgramResult {
        match instruction {
            XaamInstruction::InitializeTask {
                title,
                summary,
                encrypted_payload_url,
                deadline,
                reward_amount,
                reward_currency,
                judges,
            } => {
                msg!("Instruction: InitializeTask");
                Self::process_initialize_task(
                    program_id,
                    accounts,
                    title,
                    summary,
                    encrypted_payload_url,
                    deadline,
                    reward_amount,
                    reward_currency,
                    judges,
                )
            }
            XaamInstruction::RegisterAgent {
                name,
                description,
                agent_type,
                public_key,
            } => {
                msg!("Instruction: RegisterAgent");
                Self::process_register_agent(
                    program_id,
                    accounts,
                    name,
                    description,
                    agent_type,
                    public_key,
                )
            }
            XaamInstruction::RegisterJudge {
                name,
                description,
                public_key,
                specialization,
            } => {
                msg!("Instruction: RegisterJudge");
                Self::process_register_judge(
                    program_id,
                    accounts,
                    name,
                    description,
                    public_key,
                    specialization,
                )
            }
            XaamInstruction::StakeOnTask { amount } => {
                msg!("Instruction: StakeOnTask");
                Self::process_stake_on_task(program_id, accounts, amount)
            }
            XaamInstruction::SubmitDeliverable {
                encrypted_content_url,
                encryption_keys,
            } => {
                msg!("Instruction: SubmitDeliverable");
                Self::process_submit_deliverable(
                    program_id,
                    accounts,
                    encrypted_content_url,
                    encryption_keys,
                )
            }
            XaamInstruction::JudgeDeliverable { score, feedback } => {
                msg!("Instruction: JudgeDeliverable");
                Self::process_judge_deliverable(program_id, accounts, score, feedback)
            }
            XaamInstruction::CompleteTask {} => {
                msg!("Instruction: CompleteTask");
                Self::process_complete_task(program_id, accounts)
            }
            XaamInstruction::ReturnStake {} => {
                msg!("Instruction: ReturnStake");
                Self::process_return_stake(program_id, accounts)
            }
            XaamInstruction::BurnTaskNFT {} => {
                msg!("Instruction: BurnTaskNFT");
                Self::process_burn_task_nft(program_id, accounts)
            }
        }
    }

    /// Process InitializeTask instruction
    pub fn process_initialize_task(
        program_id: &Pubkey,
        accounts: &[AccountInfo],
        title: String,
        summary: String,
        encrypted_payload_url: String,
        deadline: i64,
        reward_amount: u64,
        reward_currency: String,
        judges: Vec<Pubkey>,
    ) -> ProgramResult {
        let account_info_iter = &mut accounts.iter();
        
        // Get accounts
        let creator_info = next_account_info(account_info_iter)?;
        let task_info = next_account_info(account_info_iter)?;
        let nft_mint_info = next_account_info(account_info_iter)?;
        let rent_info = next_account_info(account_info_iter)?;
        let token_program_info = next_account_info(account_info_iter)?;
        let system_program_info = next_account_info(account_info_iter)?;
        
        // Verify creator is signer
        if !creator_info.is_signer {
            return Err(ProgramError::MissingRequiredSignature);
        }
        
        // Verify task account is owned by program
        if task_info.owner != program_id {
            return Err(XaamError::IncorrectProgramId.into());
        }
        
        // Get current timestamp
        let clock = Clock::get()?;
        let current_timestamp = clock.unix_timestamp;
        
        // Verify deadline is in the future
        if deadline <= current_timestamp {
            return Err(XaamError::TaskDeadlineExpired.into());
        }
        
        // Verify judges (max 5)
        if judges.len() > 5 {
            return Err(ProgramError::InvalidArgument);
        }
        
        // Create judges array
        let mut judges_array = [None; 5];
        for (i, judge) in judges.iter().enumerate() {
            judges_array[i] = Some(*judge);
        }
        
        // Create task
        let task = Task {
            is_initialized: true,
            nft_id: *nft_mint_info.key,
            title,
            summary,
            encrypted_payload_url,
            creator_id: *creator_info.key,
            status: TaskStatus::Created,
            deadline,
            reward_amount,
            reward_currency,
            judges: judges_array,
            created_at: current_timestamp,
            updated_at: current_timestamp,
        };
        
        // Serialize task data
        task.serialize(&mut *task_info.data.borrow_mut())?;
        
        // TODO: Mint NFT for task (simplified for demo)
        
        msg!("Task initialized successfully");
        Ok(())
    }

    /// Process RegisterAgent instruction
    pub fn process_register_agent(
        program_id: &Pubkey,
        accounts: &[AccountInfo],
        name: String,
        description: String,
        agent_type: AgentType,
        public_key: String,
    ) -> ProgramResult {
        let account_info_iter = &mut accounts.iter();
        
        // Get accounts
        let agent_owner_info = next_account_info(account_info_iter)?;
        let agent_account_info = next_account_info(account_info_iter)?;
        let rent_info = next_account_info(account_info_iter)?;
        let system_program_info = next_account_info(account_info_iter)?;
        
        // Verify agent owner is signer
        if !agent_owner_info.is_signer {
            return Err(ProgramError::MissingRequiredSignature);
        }
        
        // Verify agent account is owned by program
        if agent_account_info.owner != program_id {
            return Err(XaamError::IncorrectProgramId.into());
        }
        
        // Get current timestamp
        let clock = Clock::get()?;
        let current_timestamp = clock.unix_timestamp;
        
        // Create agent
        let agent = Agent {
            is_initialized: true,
            name,
            description,
            agent_type,
            wallet_address: *agent_owner_info.key,
            public_key,
            reputation_score: 0,
            completed_tasks: 0,
            successful_tasks: 0,
            created_at: current_timestamp,
            updated_at: current_timestamp,
        };
        
        // Serialize agent data
        agent.serialize(&mut *agent_account_info.data.borrow_mut())?;
        
        msg!("Agent registered successfully");
        Ok(())
    }

    /// Process StakeOnTask instruction
    pub fn process_stake_on_task(
        program_id: &Pubkey,
        accounts: &[AccountInfo],
        amount: u64,
    ) -> ProgramResult {
        let account_info_iter = &mut accounts.iter();
        
        // Get accounts
        let agent_info = next_account_info(account_info_iter)?;
        let stake_account_info = next_account_info(account_info_iter)?;
        let task_account_info = next_account_info(account_info_iter)?;
        let agent_account_info = next_account_info(account_info_iter)?;
        let rent_info = next_account_info(account_info_iter)?;
        let system_program_info = next_account_info(account_info_iter)?;
        
        // Verify agent is signer
        if !agent_info.is_signer {
            return Err(ProgramError::MissingRequiredSignature);
        }
        
        // Verify stake account is owned by program
        if stake_account_info.owner != program_id {
            return Err(XaamError::IncorrectProgramId.into());
        }
        
        // Verify task account is owned by program
        if task_account_info.owner != program_id {
            return Err(XaamError::IncorrectProgramId.into());
        }
        
        // Verify agent account is owned by program
        if agent_account_info.owner != program_id {
            return Err(XaamError::IncorrectProgramId.into());
        }
        
        // Get current timestamp
        let clock = Clock::get()?;
        let current_timestamp = clock.unix_timestamp;
        
        // Deserialize task
        let mut task = Task::try_from_slice(&task_account_info.data.borrow())?;
        
        // Verify task is in Created state
        if task.status != TaskStatus::Created {
            return Err(XaamError::InvalidTaskState.into());
        }
        
        // Verify task deadline has not passed
        if task.deadline <= current_timestamp {
            return Err(XaamError::TaskDeadlineExpired.into());
        }
        
        // Deserialize agent
        let agent = Agent::try_from_slice(&agent_account_info.data.borrow())?;
        
        // Verify agent is a worker
        if agent.agent_type != AgentType::Worker {
            return Err(XaamError::InvalidAgentState.into());
        }
        
        // Create stake
        let stake = Stake {
            is_initialized: true,
            task_id: *task_account_info.key,
            agent_id: *agent_account_info.key,
            amount,
            status: StakeStatus::Active,
            staked_at: current_timestamp,
            released_at: None,
        };
        
        // Serialize stake data
        stake.serialize(&mut *stake_account_info.data.borrow_mut())?;
        
        // Update task status
        task.status = TaskStatus::Staked;
        task.updated_at = current_timestamp;
        
        // Serialize updated task data
        task.serialize(&mut *task_account_info.data.borrow_mut())?;
        
        // TODO: Transfer SOL for staking (simplified for demo)
        
        msg!("Stake on task successful");
        Ok(())
    }

    // Other instruction processors would be implemented here
    // For brevity, we're only implementing the core ones for the demo

    /// Process CompleteTask instruction (simplified)
    pub fn process_complete_task(
        program_id: &Pubkey,
        accounts: &[AccountInfo],
    ) -> ProgramResult {
        let account_info_iter = &mut accounts.iter();
        
        // Get accounts
        let creator_info = next_account_info(account_info_iter)?;
        let task_info = next_account_info(account_info_iter)?;
        let winning_agent_info = next_account_info(account_info_iter)?;
        let task_wallet_info = next_account_info(account_info_iter)?;
        let agent_wallet_info = next_account_info(account_info_iter)?;
        let token_program_info = next_account_info(account_info_iter)?;
        let system_program_info = next_account_info(account_info_iter)?;
        
        // Verify creator is signer
        if !creator_info.is_signer {
            return Err(ProgramError::MissingRequiredSignature);
        }
        
        // Verify task account is owned by program
        if task_info.owner != program_id {
            return Err(XaamError::IncorrectProgramId.into());
        }
        
        // Deserialize task
        let mut task = Task::try_from_slice(&task_info.data.borrow())?;
        
        // Verify task creator
        if task.creator_id != *creator_info.key {
            return Err(XaamError::Unauthorized.into());
        }
        
        // Verify task is in Judged state
        if task.status != TaskStatus::Judged {
            return Err(XaamError::InvalidTaskState.into());
        }
        
        // Get current timestamp
        let clock = Clock::get()?;
        let current_timestamp = clock.unix_timestamp;
        
        // Update task status
        task.status = TaskStatus::Completed;
        task.updated_at = current_timestamp;
        
        // Serialize updated task data
        task.serialize(&mut *task_info.data.borrow_mut())?;
        
        // TODO: Transfer reward to winning agent (simplified for demo)
        
        msg!("Task completed successfully");
        Ok(())
    }
}