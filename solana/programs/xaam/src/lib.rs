//! XAAM (Xpress AI Agent Marketplace) Solana Program
//!
//! This program implements the core functionality for the XAAM protocol:
//! - Task NFT creation and management
//! - Agent registration and reputation
//! - Judge registration and reputation
//! - Staking for task access
//! - Payment distribution

use borsh::{BorshDeserialize, BorshSerialize};
use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    program_error::ProgramError,
    pubkey::Pubkey,
};

// Import modules
pub mod error;
pub mod instruction;
pub mod processor;
pub mod state;

// Export modules
pub use error::XaamError;
pub use instruction::XaamInstruction;
pub use processor::Processor;
pub use state::{Agent, Judge, Task, Stake, Wallet};

// Program entrypoint
entrypoint!(process_instruction);

// Process instruction entrypoint
pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    msg!("XAAM program entrypoint");
    
    // Deserialize instruction
    let instruction = XaamInstruction::try_from_slice(instruction_data)
        .map_err(|_| ProgramError::InvalidInstructionData)?;
    
    // Process instruction
    Processor::process(program_id, accounts, instruction)
}