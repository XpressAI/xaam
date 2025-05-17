import { writable } from 'svelte/store';
import { api } from '$lib/api/client';

// Define Agent type based on backend schema
export interface Agent {
  id: string;
  name: string;
  description: string;
  agent_type: 'WORKER' | 'JUDGE';
  wallet_address: string;
  public_key: string;
  reputation_score: number;
  completed_tasks: number;
  successful_tasks: number;
  social_profiles?: {
    github?: string;
    linkedin?: string;
    twitter?: string;
  };
  portfolio_url?: string;
  created_at: string;
  updated_at: string;
}

// Agent store state
interface AgentsState {
  agents: Agent[];
  currentAgent: Agent | null;
  loading: boolean;
  error: string | null;
}

// Initial state
const initialState: AgentsState = {
  agents: [],
  currentAgent: null,
  loading: false,
  error: null
};

// Create the writable store
const agentStore = writable<AgentsState>(initialState);

// Agent store actions
export const agentsStore = {
  subscribe: agentStore.subscribe,
  
  // Fetch all agents
  fetchAgents: async (agentType?: 'WORKER' | 'JUDGE') => {
    agentStore.update((state) => ({ ...state, loading: true, error: null }));
    
    try {
      const agents = await api.agents.getAll({ agent_type: agentType });
      agentStore.update((state) => ({ ...state, agents, loading: false }));
    } catch (error) {
      console.error('Error fetching agents:', error);
      agentStore.update((state) => ({ 
        ...state, 
        loading: false, 
        error: error instanceof Error ? error.message : 'Failed to fetch agents' 
      }));
    }
  },
  
  // Fetch a single agent by ID
  fetchAgent: async (id: string) => {
    agentStore.update((state) => ({ ...state, loading: true, error: null }));
    
    try {
      const agent = await api.agents.getById(id);
      agentStore.update((state) => ({ ...state, currentAgent: agent, loading: false }));
      return agent;
    } catch (error) {
      console.error(`Error fetching agent ${id}:`, error);
      agentStore.update((state) => ({ 
        ...state, 
        loading: false, 
        error: error instanceof Error ? error.message : `Failed to fetch agent ${id}` 
      }));
      throw error;
    }
  },
  
  // Fetch agent by wallet address
  fetchAgentByWallet: async (walletAddress: string) => {
    agentStore.update((state) => ({ ...state, loading: true, error: null }));
    
    try {
      const agent = await api.agents.getByWallet(walletAddress);
      agentStore.update((state) => ({ ...state, currentAgent: agent, loading: false }));
      return agent;
    } catch (error) {
      console.error(`Error fetching agent by wallet ${walletAddress}:`, error);
      agentStore.update((state) => ({ 
        ...state, 
        loading: false, 
        error: error instanceof Error ? error.message : `Failed to fetch agent by wallet ${walletAddress}` 
      }));
      throw error;
    }
  },
  
  // Create a new agent
  createAgent: async (agentData: Omit<Agent, 'id' | 'created_at' | 'updated_at' | 'reputation_score' | 'completed_tasks' | 'successful_tasks'>) => {
    agentStore.update((state) => ({ ...state, loading: true, error: null }));
    
    try {
      // Ensure wallet is connected
      if (!agentData.wallet_address) {
        throw new Error('Wallet must be connected to create an agent');
      }
      
      // Validate required fields
      if (!agentData.name || !agentData.description || !agentData.agent_type) {
        throw new Error('Name, description, and agent type are required');
      }
      
      const newAgent = await api.agents.create(agentData);
      agentStore.update((state) => ({
        ...state,
        agents: [...state.agents, newAgent],
        currentAgent: newAgent,
        loading: false
      }));
      return newAgent;
    } catch (error) {
      console.error('Error creating agent:', error);
      agentStore.update((state) => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to create agent'
      }));
      throw error;
    }
  },
  
  // Clear current agent
  clearCurrentAgent: () => {
    agentStore.update((state) => ({ ...state, currentAgent: null }));
  }
};