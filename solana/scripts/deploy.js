/**
 * XAAM Solana Program Deployment Script
 * 
 * This script deploys the XAAM Solana program to the Solana blockchain.
 * By default, it deploys to the devnet for testing purposes.
 * 
 * Usage:
 * node deploy.js [network]
 * 
 * Where [network] is one of:
 * - localhost (default)
 * - devnet
 * - testnet
 * - mainnet-beta
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const { Connection, Keypair, PublicKey, LAMPORTS_PER_SOL } = require('@solana/web3.js');
const { Program, Provider, web3, utils } = require('@project-serum/anchor');

// Parse command line arguments
const args = process.argv.slice(2);
const network = args[0] || 'localhost';

// Configure network URL
let url;
switch (network) {
  case 'localhost':
    url = 'http://localhost:8899';
    break;
  case 'devnet':
    url = 'https://api.devnet.solana.com';
    break;
  case 'testnet':
    url = 'https://api.testnet.solana.com';
    break;
  case 'mainnet-beta':
    url = 'https://api.mainnet-beta.solana.com';
    break;
  default:
    console.error(`Unknown network: ${network}`);
    process.exit(1);
}

// Load keypair from file or create a new one
let keypair;
const keypairPath = path.resolve(__dirname, '../keypair.json');

if (fs.existsSync(keypairPath)) {
  const keypairData = JSON.parse(fs.readFileSync(keypairPath, 'utf-8'));
  keypair = Keypair.fromSecretKey(new Uint8Array(keypairData));
  console.log(`Loaded keypair from ${keypairPath}`);
} else {
  keypair = Keypair.generate();
  fs.writeFileSync(keypairPath, JSON.stringify(Array.from(keypair.secretKey)));
  console.log(`Generated new keypair and saved to ${keypairPath}`);
}

console.log(`Public key: ${keypair.publicKey.toString()}`);

// Connect to the network
const connection = new Connection(url, 'confirmed');

// Build and deploy the program
async function deploy() {
  try {
    console.log(`Deploying to ${network}...`);
    
    // Build the program
    console.log('Building program...');
    execSync('cargo build-bpf --manifest-path=./programs/xaam/Cargo.toml', { stdio: 'inherit' });
    
    // Get the program ID
    const programId = new PublicKey(keypair.publicKey.toString());
    console.log(`Program ID: ${programId.toString()}`);
    
    // Request airdrop if on devnet or testnet
    if (network === 'devnet' || network === 'testnet') {
      console.log('Requesting airdrop...');
      const signature = await connection.requestAirdrop(keypair.publicKey, 2 * LAMPORTS_PER_SOL);
      await connection.confirmTransaction(signature);
      
      const balance = await connection.getBalance(keypair.publicKey);
      console.log(`Balance: ${balance / LAMPORTS_PER_SOL} SOL`);
    }
    
    // Deploy the program
    console.log('Deploying program...');
    const programPath = path.resolve(__dirname, '../target/deploy/xaam.so');
    
    execSync(
      `solana program deploy --program-id ${keypairPath} ${programPath} --url ${url}`,
      { stdio: 'inherit' }
    );
    
    console.log(`Program deployed successfully to ${network}`);
    console.log(`Program ID: ${programId.toString()}`);
    
    // Save program ID to file
    const programIdPath = path.resolve(__dirname, '../program_id.json');
    fs.writeFileSync(programIdPath, JSON.stringify({ programId: programId.toString() }));
    console.log(`Program ID saved to ${programIdPath}`);
    
    return programId;
  } catch (error) {
    console.error('Deployment failed:', error);
    process.exit(1);
  }
}

// Run deployment
deploy().then(() => {
  console.log('Deployment completed successfully');
}).catch(error => {
  console.error('Deployment failed:', error);
  process.exit(1);
});