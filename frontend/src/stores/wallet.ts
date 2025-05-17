import { writable, get } from 'svelte/store';
import { api } from '$lib/api/client';
import { connection } from '../utils/wallet';
import { PublicKey, LAMPORTS_PER_SOL } from '@solana/web3.js';

// Define Wallet type based on backend schema
export interface Wallet {
  id?: string;
  address: string;
  agent_id?: string;
  sol_balance: number;
  usdc_balance: number;
  nfts?: string[];
  created_at?: string;
  updated_at?: string;
}

// Wallet store state
interface WalletState {
  wallet: Wallet | null;
  connected: boolean;
  loading: boolean;
  error: string | null;
}

// Initial state
const initialState: WalletState = {
  wallet: null,
  connected: false,
  loading: false,
  error: null
};

// Load initial state from localStorage if available
const loadState = (): WalletState => {
  if (typeof window === 'undefined') {
    return initialState;
  }
  
  const savedState = localStorage.getItem('walletState');
  if (savedState) {
    try {
      const parsedState = JSON.parse(savedState);
      console.log('Loaded wallet state from localStorage:', parsedState);
      return parsedState;
    } catch (e) {
      console.error('Failed to parse wallet state from localStorage:', e);
    }
  }
  
  return initialState;
};

// Create the writable store with persisted state
const store = writable<WalletState>(loadState());

// Subscribe to store changes and save to localStorage
store.subscribe(state => {
  if (typeof window !== 'undefined') {
    console.log('Saving wallet state to localStorage:', state);
    localStorage.setItem('walletState', JSON.stringify(state));
  }
});

// Helper function to get Phantom wallet provider
function getPhantomProvider() {
  if ('phantom' in window) {
    const provider = (window as any).phantom?.solana;
    if (provider?.isPhantom) {
      return provider;
    }
  }
  
  // Fallback to window.solana (older integration)
  const provider = (window as any).solana;
  if (provider?.isPhantom) {
    return provider;
  }
  
  return null;
}

// Wallet store actions
export const walletStore = {
  subscribe: store.subscribe,
  
  // Check if wallet is already connected
  checkConnection: async () => {
    const provider = getPhantomProvider();
    const currentState = get(store);
    
    console.log('Checking wallet connection, current state:',
      { connected: currentState.connected, hasWallet: !!currentState.wallet, hasProvider: !!provider });
    
    // Check localStorage directly to see what's stored
    const savedState = localStorage.getItem('walletState');
    if (savedState) {
      try {
        const parsedState = JSON.parse(savedState);
        
        // If localStorage has a connected wallet but our state doesn't, restore from localStorage
        if (parsedState.connected && parsedState.wallet && (!currentState.connected || !currentState.wallet)) {
          console.log('Restoring wallet state from localStorage');
          store.update(() => parsedState);
          return true;
        }
      } catch (e) {
        console.error('Failed to parse wallet state from localStorage:', e);
      }
    }
    
    // If we have a stored wallet state and provider is available
    if (currentState.connected && currentState.wallet && provider) {
      try {
        // Check if the provider is actually connected
        const isConnected = provider.isConnected;
        
        if (isConnected) {
          // Refresh the balances to ensure they're up to date
          await walletStore.refreshBalances();
          return true;
        } else {
          // Provider says not connected, but we'll trust our stored state for task creation
          // This prevents the wallet connection from being reset during page navigation
            return true;
        }
      } catch (error) {
        console.error('Error checking wallet connection:', error);
        // Don't reset state on error if we're on the task creation page
        if (typeof window !== 'undefined' && window.location.pathname.includes('/tasks/create')) {
          return currentState.connected;
        } else {
          // Reset state on error for other pages
          store.update(() => ({
            wallet: null,
            connected: false,
            loading: false,
            error: null
          }));
        }
      }
    } else if (provider) {
      // If we don't have a stored wallet state but provider is available and connected
      try {
        if (provider.isConnected && provider.publicKey) {
          console.log('Provider is connected but wallet store is not, reconnecting...');
          
          // Create wallet info from provider
          const publicKey = provider.publicKey.toString();
          const publicKeyObj = new PublicKey(publicKey);
          const lamports = await connection.getBalance(publicKeyObj);
          const solBalance = lamports / LAMPORTS_PER_SOL;
          
          // Update store with wallet info
          store.update((state) => ({
            ...state,
            wallet: {
              address: publicKey,
              sol_balance: solBalance,
              usdc_balance: 0
            },
            connected: true,
            loading: false
          }));
          
          return true;
        }
      } catch (error) {
        console.error('Error reconnecting wallet:', error);
      }
    }
    
    return false;
  },
  
  // Connect to wallet
  connect: async () => {
    store.update((state) => ({ ...state, loading: true, error: null }));
    
    try {
      const provider = getPhantomProvider();
      
      if (!provider) {
        throw new Error('Phantom wallet not installed');
      }
      
      // Request connection to the wallet
      const response = await provider.connect();
      const walletAddress = response.publicKey.toString();
      
      // Get SOL balance from Solana network
      const publicKey = new PublicKey(walletAddress);
      const lamports = await connection.getBalance(publicKey);
      const solBalance = lamports / 1000000000; // Convert lamports to SOL
      
      // Create wallet object with real balance
      const walletInfo: Wallet = {
        address: walletAddress,
        sol_balance: solBalance,
        usdc_balance: 0, // USDC balance would require token account lookup
      };
      
      // Update store with wallet info
      store.update((state) => ({
        ...state,
        wallet: walletInfo,
        connected: true,
        loading: false
      }));
      
      // Set up event listeners for wallet changes
      provider.on('accountChanged', async (publicKey: PublicKey | null) => {
        if (publicKey) {
          await walletStore.refreshBalances();
        } else {
          await walletStore.disconnect();
        }
      });
      
      provider.on('disconnect', async () => {
        await walletStore.disconnect();
      });
      
    } catch (error) {
      console.error('Error connecting to wallet:', error);
      store.update((state) => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to connect to wallet'
      }));
    }
  },
  
  // Disconnect wallet
  disconnect: async () => {
    store.update((state) => ({ ...state, loading: true }));
    
    try {
      const provider = getPhantomProvider();
      
      if (provider) {
        await provider.disconnect();
      }
      
      store.update(() => initialState);
    } catch (error) {
      console.error('Error disconnecting wallet:', error);
      store.update((state) => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to disconnect wallet'
      }));
    }
  },
  
  // Refresh wallet balances
  refreshBalances: async () => {
    const currentState = get(store);
    if (!currentState.wallet) return;
    
    store.update((state) => ({ ...state, loading: true, error: null }));
    
    try {
      // Get SOL balance from Solana network
      const publicKey = new PublicKey(currentState.wallet.address);
      const lamports = await connection.getBalance(publicKey);
      const solBalance = lamports / 1000000000; // Convert lamports to SOL
      
      // Update wallet with new balance
      const updatedWallet = {
        ...currentState.wallet,
        sol_balance: solBalance
      };
      
      store.update((state) => ({
        ...state,
        wallet: updatedWallet,
        loading: false
      }));
    } catch (error) {
      console.error('Error refreshing wallet balances:', error);
      store.update((state) => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to refresh wallet balances'
      }));
    }
  },
  
  // Stake SOL on a task
  stakeOnTask: async (taskId: string, amount: number) => {
    const currentState = get(store);
    if (!currentState.wallet) throw new Error('Wallet not connected');
    
    store.update((state) => ({ ...state, loading: true, error: null }));
    
    try {
      await api.blockchain.stake({
        agent_wallet: currentState.wallet.address,
        task_id: taskId,
        amount
      });
      
      // Refresh wallet balances after staking
      await walletStore.refreshBalances();
      
      return true;
    } catch (error) {
      console.error('Error staking on task:', error);
      store.update((state) => ({
        ...state, 
        loading: false, 
        error: error instanceof Error ? error.message : 'Failed to stake on task' 
      }));
      throw error;
    }
  },
  
  // Update wallet info with provided data
  updateWalletInfo: (walletInfo: Partial<Wallet>) => {
    const currentState = get(store);
    if (!currentState.wallet) return;
    
    const updatedWallet = {
      ...currentState.wallet,
      ...walletInfo
    };
    
    store.update((state) => ({
      ...state,
      wallet: updatedWallet
    }));
  }
};