//! Error types for the XAAM program

use solana_program::program_error::ProgramError;
use thiserror::Error;

/// Errors that may be returned by the XAAM program
#[derive(Error, Debug, Copy, Clone)]
pub enum XaamError {
    /// Invalid instruction data
    #[error("Invalid instruction data")]
    InvalidInstructionData,

    /// Not rent exempt
    #[error("Account not rent exempt")]
    NotRentExempt,

    /// Expected account owner to be the program
    #[error("Account owner should be the program")]
    IncorrectProgramId,

    /// Invalid account data
    #[error("Invalid account data")]
    InvalidAccountData,

    /// Insufficient funds
    #[error("Insufficient funds")]
    InsufficientFunds,

    /// Invalid task state
    #[error("Invalid task state")]
    InvalidTaskState,

    /// Invalid agent state
    #[error("Invalid agent state")]
    InvalidAgentState,

    /// Invalid judge state
    #[error("Invalid judge state")]
    InvalidJudgeState,

    /// Invalid stake state
    #[error("Invalid stake state")]
    InvalidStakeState,

    /// Unauthorized operation
    #[error("Unauthorized operation")]
    Unauthorized,

    /// Task deadline expired
    #[error("Task deadline expired")]
    TaskDeadlineExpired,

    /// Invalid deliverable
    #[error("Invalid deliverable")]
    InvalidDeliverable,
}

impl From<XaamError> for ProgramError {
    fn from(e: XaamError) -> Self {
        ProgramError::Custom(e as u32)
    }
}