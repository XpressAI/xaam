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
  
  // Fetch judge agents by wallet address
  fetchJudgeAgentsByWallet: async (walletAddress: string) => {
    agentStore.update((state) => ({ ...state, loading: true, error: null }));
    
    try {
      console.log('Fetching judge agents for wallet:', walletAddress);
      // First get all agents of type JUDGE
      const allJudges = await api.agents.getAll({ agent_type: 'JUDGE' });
      console.log('Judge agents fetched:', allJudges);
      
      // For demo purposes, return all judges regardless of wallet address
      
      // IMPORTANT: Don't overwrite the entire agents array, just update it with judge agents
      // This ensures we don't lose worker agents when fetching judge agents
      agentStore.update((state) => {
        // Keep any existing agents that aren't judges
        const nonJudgeAgents = state.agents.filter(a => a.agent_type !== 'JUDGE');
        // Combine with the new judge agents
        const updatedAgents = [...nonJudgeAgents, ...allJudges];
        console.log('Updated store with combined agents:', updatedAgents);
        return { ...state, agents: updatedAgents, loading: false };
      });
      
      return allJudges;
    } catch (error) {
      console.error('Error fetching judge agents by wallet:', error);
      agentStore.update((state) => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch judge agents'
      }));
      return [];
    }
  },
  
  // Fetch worker agents by wallet address
  fetchWorkerAgentsByWallet: async (walletAddress: string) => {
    agentStore.update((state) => ({ ...state, loading: true, error: null }));
    
    try {
      console.log('Fetching worker agents for wallet:', walletAddress);
      // First get all agents of type WORKER
      const allWorkers = await api.agents.getAll({ agent_type: 'WORKER' });
      console.log('Worker agents fetched:', allWorkers);
      
      // For demo purposes, return all workers regardless of wallet address
      
      // IMPORTANT: Don't overwrite the entire agents array, just update it with worker agents
      // This ensures we don't lose judge agents when fetching worker agents
      agentStore.update((state) => {
        // Keep any existing agents that aren't workers
        const nonWorkerAgents = state.agents.filter(a => a.agent_type !== 'WORKER');
        // Combine with the new worker agents
        const updatedAgents = [...nonWorkerAgents, ...allWorkers];
        console.log('Updated store with combined agents:', updatedAgents);
        return { ...state, agents: updatedAgents, loading: false };
      });
      
      return allWorkers;
    } catch (error) {
      console.error('Error fetching worker agents by wallet:', error);
      agentStore.update((state) => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch worker agents'
      }));
      return [];
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
  },
  
  // Delete an agent
  deleteAgent: async (agentId: string) => {
    agentStore.update((state) => ({ ...state, loading: true, error: null }));
    
    try {
      console.log('Deleting agent with ID:', agentId);
      
      // For demo purposes, we'll just remove it from the local store
      // In a real app, you would call the API to delete it from the backend
      // await api.agents.delete(agentId);
      
      // Remove the agent from the store
      agentStore.update((state) => {
        const updatedAgents = state.agents.filter(agent => agent.id !== agentId);
        console.log('Agents after deletion:', updatedAgents);
        return { ...state, agents: updatedAgents, loading: false };
      });
      
      return true;
    } catch (error) {
      console.error('Error deleting agent:', error);
      agentStore.update((state) => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to delete agent'
      }));
      return false;
    }
  }
};