const assert = require('assert');
const anchor = require('@project-serum/anchor');
const { SystemProgram, Keypair, PublicKey } = anchor.web3;

describe('xaam', () => {
  // Configure the client to use the local cluster
  const provider = anchor.Provider.env();
  anchor.setProvider(provider);

  const program = anchor.workspace.Xaam;
  
  // Generate keypairs for testing
  const creator = Keypair.generate();
  const agent = Keypair.generate();
  const judge = Keypair.generate();
  
  // Generate keypairs for accounts
  const taskKeypair = Keypair.generate();
  const agentAccountKeypair = Keypair.generate();
  const judgeAccountKeypair = Keypair.generate();
  const stakeAccountKeypair = Keypair.generate();
  
  // Test data
  const taskTitle = "Test Task";
  const taskSummary = "This is a test task for the XAAM protocol";
  const encryptedPayloadUrl = "https://example.com/encrypted-payload";
  const deadline = Math.floor(Date.now() / 1000) + 86400; // 1 day from now
  const rewardAmount = new anchor.BN(100000000); // 1 SOL in lamports
  const rewardCurrency = "USDC";
  const judges = [judge.publicKey];
  
  const agentName = "Test Agent";
  const agentDescription = "This is a test agent for the XAAM protocol";
  const agentPublicKey = "test-public-key";
  
  const judgeName = "Test Judge";
  const judgeDescription = "This is a test judge for the XAAM protocol";
  const judgePublicKey = "test-judge-public-key";
  const judgeSpecialization = "AI Testing";
  
  const stakeAmount = new anchor.BN(50000000); // 0.5 SOL in lamports

  it('Initializes a task', async () => {
    // Airdrop SOL to creator
    await provider.connection.confirmTransaction(
      await provider.connection.requestAirdrop(creator.publicKey, 10000000000),
      "confirmed"
    );
    
    // Initialize task
    await program.rpc.initializeTask(
      taskTitle,
      taskSummary,
      encryptedPayloadUrl,
      new anchor.BN(deadline),
      rewardAmount,
      rewardCurrency,
      judges,
      {
        accounts: {
          creator: creator.publicKey,
          task: taskKeypair.publicKey,
          nftMint: Keypair.generate().publicKey,
          rent: anchor.web3.SYSVAR_RENT_PUBKEY,
          tokenProgram: anchor.utils.token.TOKEN_PROGRAM_ID,
          systemProgram: SystemProgram.programId,
        },
        signers: [creator, taskKeypair],
      }
    );
    
    // Fetch task account
    const taskAccount = await program.account.task.fetch(taskKeypair.publicKey);
    
    // Verify task data
    assert.equal(taskAccount.title, taskTitle);
    assert.equal(taskAccount.summary, taskSummary);
    assert.equal(taskAccount.encryptedPayloadUrl, encryptedPayloadUrl);
    assert.ok(taskAccount.deadline.eq(new anchor.BN(deadline)));
    assert.ok(taskAccount.rewardAmount.eq(rewardAmount));
    assert.equal(taskAccount.rewardCurrency, rewardCurrency);
    assert.equal(taskAccount.status, 0); // Created
    assert.equal(taskAccount.creatorId.toString(), creator.publicKey.toString());
  });

  it('Registers an agent', async () => {
    // Airdrop SOL to agent
    await provider.connection.confirmTransaction(
      await provider.connection.requestAirdrop(agent.publicKey, 10000000000),
      "confirmed"
    );
    
    // Register agent
    await program.rpc.registerAgent(
      agentName,
      agentDescription,
      { worker: {} }, // AgentType::Worker
      agentPublicKey,
      {
        accounts: {
          agentOwner: agent.publicKey,
          agentAccount: agentAccountKeypair.publicKey,
          rent: anchor.web3.SYSVAR_RENT_PUBKEY,
          systemProgram: SystemProgram.programId,
        },
        signers: [agent, agentAccountKeypair],
      }
    );
    
    // Fetch agent account
    const agentAccount = await program.account.agent.fetch(agentAccountKeypair.publicKey);
    
    // Verify agent data
    assert.equal(agentAccount.name, agentName);
    assert.equal(agentAccount.description, agentDescription);
    assert.deepEqual(agentAccount.agentType, { worker: {} });
    assert.equal(agentAccount.publicKey, agentPublicKey);
    assert.equal(agentAccount.walletAddress.toString(), agent.publicKey.toString());
    assert.equal(agentAccount.reputationScore.toNumber(), 0);
    assert.equal(agentAccount.completedTasks, 0);
    assert.equal(agentAccount.successfulTasks, 0);
  });

  it('Stakes on a task', async () => {
    // Stake on task
    await program.rpc.stakeOnTask(
      stakeAmount,
      {
        accounts: {
          agent: agent.publicKey,
          stakeAccount: stakeAccountKeypair.publicKey,
          taskAccount: taskKeypair.publicKey,
          agentAccount: agentAccountKeypair.publicKey,
          rent: anchor.web3.SYSVAR_RENT_PUBKEY,
          systemProgram: SystemProgram.programId,
        },
        signers: [agent, stakeAccountKeypair],
      }
    );
    
    // Fetch stake account
    const stakeAccount = await program.account.stake.fetch(stakeAccountKeypair.publicKey);
    
    // Verify stake data
    assert.equal(stakeAccount.taskId.toString(), taskKeypair.publicKey.toString());
    assert.equal(stakeAccount.agentId.toString(), agentAccountKeypair.publicKey.toString());
    assert.ok(stakeAccount.amount.eq(stakeAmount));
    assert.deepEqual(stakeAccount.status, { active: {} });
    
    // Fetch task account
    const taskAccount = await program.account.task.fetch(taskKeypair.publicKey);
    
    // Verify task status updated
    assert.equal(taskAccount.status, 1); // Staked
  });
});