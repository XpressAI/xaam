/**
 * Solana wallet integration utilities for XAAM frontend
 */

import { writable } from 'svelte/store';
import {
  Connection,
  PublicKey,
  Transaction,
  LAMPORTS_PER_SOL,
  clusterApiUrl
} from '@solana/web3.js';
import { walletStore } from '../stores/wallet';
import { authStore } from '../stores/auth';

// Define wallet adapter interface
export interface WalletAdapter {
  publicKey: PublicKey | null;
  connected: boolean;
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  signTransaction(transaction: Transaction): Promise<Transaction>;
  signAllTransactions(transactions: Transaction[]): Promise<Transaction[]>;
}

// Define wallet interface
export interface Wallet {
  adapter: WalletAdapter | null;
  publicKey: string | null;
  connected: boolean;
}

// Initialize wallet store with default values
const initialWalletState: Wallet = {
  adapter: null,
  publicKey: null,
  connected: false,
};

// Create wallet store
export const wallet = writable<Wallet>(initialWalletState);

// Create a connection to Solana devnet
export const connection = new Connection(clusterApiUrl('devnet'), 'confirmed');

/**
 * Connect to a Solana wallet
 * @returns Promise that resolves when connected
 */
export async function connectWallet(): Promise<void> {
  try {
    console.log('wallet.ts: connectWallet called');
    
    // Check if already connected in the store
    const currentWallet = await getWalletValue();
    console.log('wallet.ts: Current wallet state:', currentWallet);
    
    if (currentWallet.connected && currentWallet.publicKey) {
      console.log('wallet.ts: Wallet already connected:', currentWallet.publicKey);
      
      // Just update the wallet info to refresh balances
      await updateWalletInfo(currentWallet.publicKey);
      return;
    }
    
    // Check if Phantom wallet is available
    const provider = (window as any)?.phantom?.solana || (window as any)?.solana;
    
    // FOR TESTING: Create a mock wallet connection if provider is not available
    if (!provider) {
      console.log('No wallet provider found, using mock wallet for testing');
      
      // Create a mock public key
      const mockPublicKey = '5YNmS1R9nNSCDzb5a7mMJ1dwK9uHeAAF4CmPEwKgVWr8';
      
      // Update wallet store
      wallet.update((state: Wallet) => ({
        ...state,
        adapter: {
          publicKey: { toString: () => mockPublicKey } as unknown as PublicKey,
          connected: true,
          connect: async () => {},
          disconnect: async () => {},
          signTransaction: async (tx: any) => tx,
          signAllTransactions: async (txs: any) => txs,
        },
        publicKey: mockPublicKey,
        connected: true,
      }));
      
      // Update wallet store with mock balance
      await updateWalletInfo(mockPublicKey);
      
      // Also update the main wallet store
      walletStore.updateWalletInfo({
        address: mockPublicKey,
        sol_balance: 14.90,
        usdc_balance: 0
      });
      
      console.log('Mock wallet connected:', mockPublicKey);
      return;
    }
    
    if (!provider.isPhantom) {
      throw new Error('Please use Phantom wallet for this application.');
    }
    
    // Check if already connected in the provider
    if (provider.isConnected) {
      const publicKey = provider.publicKey;
      if (publicKey) {
        // Create wallet adapter for already connected wallet
        const adapter: WalletAdapter = createWalletAdapter(provider, publicKey);
        
        // Update wallet store
        wallet.update((state: Wallet) => ({
          ...state,
          adapter,
          publicKey: publicKey.toString(),
          connected: true,
        }));
        
        // Update wallet store with balance and other info
        await updateWalletInfo(publicKey.toString());
        
        // Set up event listeners
        setupWalletEventListeners(provider);
        
        console.log('Reconnected to existing wallet:', publicKey.toString());
        return;
      }
    }
    
    // Connect to wallet if not already connected
    const response = await provider.connect();
    const publicKey = response.publicKey;
    
    // Create wallet adapter
    const adapter: WalletAdapter = createWalletAdapter(provider, publicKey);
    
    // Update wallet store
    wallet.update((state: Wallet) => ({
      ...state,
      adapter,
      publicKey: publicKey.toString(),
      connected: true,
    }));
    
    // Update wallet store with balance and other info
    await updateWalletInfo(publicKey.toString());
    
    // Set up event listeners
    setupWalletEventListeners(provider);
    
    console.log('Wallet connected:', publicKey.toString());
    
    // Update auth store when wallet is connected
    try {
      await authStore.loginWithWallet();
      console.log('wallet.ts: Successfully logged in with wallet via auth store');
      
      // Check auth store state after login
      const authState = await new Promise(resolve => {
        const unsub = authStore.subscribe(state => {
          unsub();
          resolve(state);
        });
      });
      console.log('wallet.ts: Auth store state after wallet connection:', authState);
    } catch (e) {
      console.error('wallet.ts: Error updating auth store state:', e);
    }
  } catch (error) {
    console.error('Error connecting wallet:', error);
    throw error;
  }
}

/**
 * Create a wallet adapter for the given provider and public key
 */
function createWalletAdapter(provider: any, publicKey: PublicKey): WalletAdapter {
  return {
    publicKey: publicKey,
    connected: true,
    connect: async () => {
      await provider.connect();
    },
    disconnect: async () => {
      await provider.disconnect();
    },
    signTransaction: async (transaction: Transaction) => {
      return await provider.signTransaction(transaction);
    },
    signAllTransactions: async (transactions: Transaction[]) => {
      return await provider.signAllTransactions(transactions);
    },
  };
}

/**
 * Set up event listeners for wallet connection changes
 */
function setupWalletEventListeners(provider: any): void {
  // Remove any existing listeners first to prevent duplicates
  provider.removeAllListeners?.('connect');
  provider.removeAllListeners?.('disconnect');
  provider.removeAllListeners?.('accountChanged');
  
  // Listen for wallet connection changes
  provider.on('connect', (publicKey: PublicKey) => {
    wallet.update((state: Wallet) => ({
      ...state,
      publicKey: publicKey.toString(),
      connected: true,
    }));
    updateWalletInfo(publicKey.toString());
  });
  
  provider.on('disconnect', () => {
    wallet.update((state: Wallet) => ({
      ...state,
      publicKey: null,
      connected: false,
    }));
    
    // Also disconnect from the main wallet store
    walletStore.disconnect();
  });
  
  provider.on('accountChanged', (publicKey: PublicKey | null) => {
    wallet.update((state: Wallet) => ({
      ...state,
      publicKey: publicKey?.toString() || null,
      connected: !!publicKey,
    }));
    if (publicKey) {
      updateWalletInfo(publicKey.toString());
    }
  });
}

/**
 * Disconnect from the Solana wallet
 */
export async function disconnectWallet(): Promise<void> {
  try {
    const currentWallet = await getWalletValue();
    
    if (currentWallet.adapter) {
      await currentWallet.adapter.disconnect();
    }
    
    // Reset wallet store
    wallet.set(initialWalletState);
    
    // Also disconnect from the main wallet store
    walletStore.disconnect();
    
    console.log('Wallet disconnected');
  } catch (error) {
    console.error('Error disconnecting wallet:', error);
    throw error;
  }
}

/**
 * Get the current wallet value
 * @returns Current wallet value
 */
export function getWalletValue(): Promise<Wallet> {
  return new Promise((resolve) => {
    const unsubscribe = wallet.subscribe((value: Wallet) => {
      unsubscribe();
      resolve(value);
    });
  });
}

/**
 * Update wallet information (balance, etc.)
 * @param publicKey Wallet public key
 */
export async function updateWalletInfo(publicKey: string): Promise<void> {
  try {
    // Get SOL balance from Solana network
    const solBalance = await getSolBalance(publicKey);
    
    // Create wallet info object
    const walletInfo = {
      address: publicKey,
      sol_balance: solBalance,
      usdc_balance: 0, // USDC balance would require token account lookup
      connected: true
    };
    
    // Update the main wallet store with real balance
    walletStore.updateWalletInfo(walletInfo);
    
    console.log('Wallet info updated with balance:', solBalance);
  } catch (error) {
    console.error('Error updating wallet info:', error);
  }
}

/**
 * Get SOL balance for a wallet
 * @param publicKey Wallet public key
 * @returns SOL balance
 */
export async function getSolBalance(publicKey: string): Promise<number> {
  try {
    const pubKey = new PublicKey(publicKey);
    const balance = await connection.getBalance(pubKey);
    return balance / LAMPORTS_PER_SOL; // Convert lamports to SOL
  } catch (error) {
    console.error('Error getting SOL balance:', error);
    return 0;
  }
}

/**
 * Request an airdrop of SOL (only works on devnet and testnet)
 * @param amount Amount of SOL to request
 * @returns Transaction signature
 */
export async function requestAirdrop(amount: number = 1): Promise<string> {
  try {
    const currentWallet = await getWalletValue();
    
    if (!currentWallet.publicKey) {
      throw new Error('Wallet not connected');
    }
    
    // Request airdrop directly from Solana devnet
    const pubKey = new PublicKey(currentWallet.publicKey);
    const lamports = amount * LAMPORTS_PER_SOL;
    
    // Request the airdrop
    const signature = await connection.requestAirdrop(pubKey, lamports);
    
    // Wait for confirmation
    await connection.confirmTransaction(signature);
    
    // Update wallet info
    await updateWalletInfo(currentWallet.publicKey);
    
    console.log('Airdrop successful:', signature);
    
    return signature;
  } catch (error) {
    console.error('Error requesting airdrop:', error);
    throw error;
  }
}