import { writable, get } from 'svelte/store';
import { walletStore } from './wallet';
import { agentsStore } from './agents';

// Auth store state
interface AuthState {
  isAuthenticated: boolean;
  currentUser: {
    id: string;
    name: string;
    walletAddress: string;
    agentType: 'WORKER' | 'JUDGE' | null;
  } | null;
  loading: boolean;
  error: string | null;
}

// Initial state
const initialState: AuthState = {
  isAuthenticated: false,
  currentUser: null,
  loading: false,
  error: null
};

// Create the writable store
const store = writable<AuthState>(initialState);

// Auth store actions
export const authStore = {
  subscribe: store.subscribe,
  
  // Login with wallet
  loginWithWallet: async () => {
    console.log('Auth store: loginWithWallet called');
    store.update(state => ({ ...state, loading: true, error: null }));
    
    try {
      // Connect wallet
      console.log('Auth store: Attempting to connect wallet');
      await walletStore.connect();
      
      // Get current wallet state
      let walletAddress = '';
      
      walletStore.subscribe(walletState => {
        console.log('Auth store: Wallet state updated:', walletState);
        if (walletState.wallet) {
          walletAddress = walletState.wallet.address;
        }
      })();
      
      console.log('Auth store: Wallet address after connection:', walletAddress);
      
      if (!walletAddress) {
        console.error('Auth store: Failed to get wallet address after connection');
        throw new Error('Failed to connect wallet');
      }
      
      // Try to fetch agent by wallet address
      try {
        const agent = await agentsStore.fetchAgentByWallet(walletAddress);
        
        // Set authenticated user
        store.update(state => ({
          ...state,
          isAuthenticated: true,
          currentUser: {
            id: agent.id,
            name: agent.name,
            walletAddress: agent.wallet_address,
            agentType: agent.agent_type
          },
          loading: false
        }));
      } catch (error) {
        // If agent doesn't exist, create a mock user
        store.update(state => ({
          ...state,
          isAuthenticated: true,
          currentUser: {
            id: 'mock-id',
            name: 'Anonymous User',
            walletAddress,
            agentType: null
          },
          loading: false
        }));
      }
    } catch (error) {
      console.error('Error logging in with wallet:', error);
      store.update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to login with wallet'
      }));
    }
  },
  
  // Register as agent
  registerAsAgent: async (agentData: { name: string; description: string; agent_type: 'WORKER' | 'JUDGE' }) => {
    store.update(state => ({ ...state, loading: true, error: null }));
    
    try {
      const currentState = get(store);
      if (!currentState.currentUser?.walletAddress) {
        throw new Error('Wallet not connected');
      }
      
      const newAgent = await agentsStore.createAgent({
        ...agentData,
        wallet_address: currentState.currentUser.walletAddress,
        public_key: currentState.currentUser.walletAddress // In a real app, this would be different
      });
      
      // Update current user
      store.update(state => ({
        ...state,
        currentUser: {
          ...state.currentUser!,
          id: newAgent.id,
          name: newAgent.name,
          agentType: newAgent.agent_type
        },
        loading: false
      }));
      
      return newAgent;
    } catch (error) {
      console.error('Error registering as agent:', error);
      store.update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to register as agent'
      }));
      throw error;
    }
  },
  
  // Logout
  logout: async () => {
    store.update(state => ({ ...state, loading: true }));
    
    try {
      // Disconnect wallet
      await walletStore.disconnect();
      
      // Reset auth state
      store.update(() => initialState);
    } catch (error) {
      console.error('Error logging out:', error);
      store.update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to logout'
      }));
    }
  }
};