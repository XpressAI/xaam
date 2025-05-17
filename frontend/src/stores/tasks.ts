import { writable, derived } from 'svelte/store';
import type { Writable } from 'svelte/store';
import { api } from '$lib/api/client';

// Define Task type based on backend schema
export interface Task {
  id: string;
  nft_id: string;
  title: string;
  summary: string;
  encrypted_payload_url: string;
  encryption_key?: string;
  creator_id: string;
  status: 'CREATED' | 'STAKED' | 'IN_PROGRESS' | 'SUBMITTED' | 'JUDGED' | 'COMPLETED';
  deadline: string;
  reward_amount: number;
  reward_currency: string;
  judges: string[];
  created_at: string;
  updated_at: string;
}

// Interface for task with financial outcome
export interface TaskWithFinancialOutcome extends Task {
  financialOutcome: number;
  role: 'WORKER' | 'JUDGE';
  agentStatus: 'CONNECTED' | 'DISCONNECTED';
  agentActivity: 'WORKING' | 'BROWSING' | 'IDLE';
}

// Task store state
interface TasksState {
  tasks: Task[];
  participatedTasks: TaskWithFinancialOutcome[];
  currentTask: Task | null;
  loading: boolean;
  error: string | null;
  filters: {
    status: string | null;
    search: string;
    sortBy: string;
    sortDirection: string;
    role: string;
  };
}

// Initial state
const initialState: TasksState = {
  tasks: [],
  participatedTasks: [],
  currentTask: null,
  loading: false,
  error: null,
  filters: {
    status: null,
    search: '',
    sortBy: 'deadline',
    sortDirection: 'asc',
    role: 'ALL'
  }
};

// Create the writable store
const taskStore: Writable<TasksState> = writable(initialState);

// Derived store for filtered tasks
export const filteredTasks = derived(taskStore, ($taskStore) => {
  let result = [...$taskStore.tasks];
  
  // Apply status filter
  if ($taskStore.filters.status) {
    result = result.filter(task => task.status === $taskStore.filters.status);
  }
  
  // Apply search filter
  if ($taskStore.filters.search) {
    const searchLower = $taskStore.filters.search.toLowerCase();
    result = result.filter(task =>
      task.title.toLowerCase().includes(searchLower) ||
      task.summary.toLowerCase().includes(searchLower)
    );
  }
  
  // Apply sorting
  result.sort((a, b) => {
    const sortBy = $taskStore.filters.sortBy;
    const direction = $taskStore.filters.sortDirection === 'asc' ? 1 : -1;
    
    if (sortBy === 'deadline') {
      return direction * (new Date(a.deadline).getTime() - new Date(b.deadline).getTime());
    } else if (sortBy === 'reward_amount') {
      return direction * (a.reward_amount - b.reward_amount);
    } else if (sortBy === 'financialOutcome') {
      return direction * (0 - 0); // Placeholder, will be implemented with financial outcomes
    } else {
      return direction * (new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
    }
  });
  
  return result;
});

// Derived store for filtered participated tasks
export const filteredParticipatedTasks = derived(taskStore, ($taskStore) => {
  let result = [...$taskStore.participatedTasks];
  
  // Apply role filter
  if ($taskStore.filters.role && $taskStore.filters.role !== 'ALL') {
    result = result.filter(task => task.role === $taskStore.filters.role);
  }
  
  // Apply status filter
  if ($taskStore.filters.status) {
    result = result.filter(task => task.status === $taskStore.filters.status);
  }
  
  // Apply search filter
  if ($taskStore.filters.search) {
    const searchLower = $taskStore.filters.search.toLowerCase();
    result = result.filter(task =>
      task.title.toLowerCase().includes(searchLower) ||
      task.summary.toLowerCase().includes(searchLower)
    );
  }
  
  // Apply sorting
  result.sort((a, b) => {
    const sortBy = $taskStore.filters.sortBy;
    const direction = $taskStore.filters.sortDirection === 'asc' ? 1 : -1;
    
    if (sortBy === 'deadline') {
      return direction * (new Date(a.deadline).getTime() - new Date(b.deadline).getTime());
    } else if (sortBy === 'reward_amount') {
      return direction * (a.reward_amount - b.reward_amount);
    } else if (sortBy === 'financialOutcome') {
      return direction * (a.financialOutcome - b.financialOutcome);
    } else {
      return direction * (new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
    }
  });
  
  return result;
});

// Task store actions
export const tasksStore = {
  subscribe: taskStore.subscribe,
  
  // Fetch all tasks
  fetchTasks: async () => {
    taskStore.update(state => ({ ...state, loading: true, error: null }));
    
    try {
      const tasks = await api.tasks.getAll();
      taskStore.update(state => ({ ...state, tasks, loading: false }));
    } catch (error) {
      console.error('Error fetching tasks:', error);
      taskStore.update(state => ({ 
        ...state, 
        loading: false, 
        error: error instanceof Error ? error.message : 'Failed to fetch tasks' 
      }));
    }
  },
  
  // Fetch a single task by ID
  fetchTask: async (id: string) => {
    taskStore.update(state => ({ ...state, loading: true, error: null }));
    
    try {
      const task = await api.tasks.getById(id);
      taskStore.update(state => ({ ...state, currentTask: task, loading: false }));
      return task;
    } catch (error) {
      console.error(`Error fetching task ${id}:`, error);
      taskStore.update(state => ({ 
        ...state, 
        loading: false, 
        error: error instanceof Error ? error.message : `Failed to fetch task ${id}` 
      }));
      throw error;
    }
  },
  
  // Create a new task
  createTask: async (taskData: Omit<Task, 'id' | 'nft_id' | 'created_at' | 'updated_at' | 'status'>) => {
    taskStore.update(state => ({ ...state, loading: true, error: null }));
    
    try {
      const newTask = await api.tasks.create(taskData);
      taskStore.update(state => ({ 
        ...state, 
        tasks: [...state.tasks, newTask],
        currentTask: newTask,
        loading: false 
      }));
      return newTask;
    } catch (error) {
      console.error('Error creating task:', error);
      taskStore.update(state => ({ 
        ...state, 
        loading: false, 
        error: error instanceof Error ? error.message : 'Failed to create task' 
      }));
      throw error;
    }
  },
  
  // Update task filters
  updateFilters: (filters: Partial<TasksState['filters']>) => {
    taskStore.update(state => ({
      ...state,
      filters: { ...state.filters, ...filters }
    }));
  },
  
  // Reset filters
  resetFilters: () => {
    taskStore.update(state => ({
      ...state,
      filters: initialState.filters
    }));
  },
  
  // Clear current task
  clearCurrentTask: () => {
    taskStore.update(state => ({ ...state, currentTask: null }));
  },
  
  // Fetch tasks by agent wallet address
  fetchTasksByAgentWallet: async (walletAddress: string) => {
    taskStore.update(state => ({ ...state, loading: true, error: null }));
    
    try {
      // In a real implementation, we would fetch tasks from the backend
      // For now, we'll use mock data
      const tasks = await api.tasks.getAll();
      
      // Get all agents for this wallet
      const workerAgents = await api.agents.getAll({ agent_type: 'WORKER' });
      const judgeAgents = await api.agents.getAll({ agent_type: 'JUDGE' });
      
      const userWorkerAgents = workerAgents.filter(agent => agent.wallet_address === walletAddress);
      const userJudgeAgents = judgeAgents.filter(agent => agent.wallet_address === walletAddress);
      
      // Calculate financial outcomes for each task
      const participatedTasks: TaskWithFinancialOutcome[] = [];
      
      // For worker agents, they earn the reward amount if the task is completed
      for (const agent of userWorkerAgents) {
        const workerTasks = tasks.filter(task =>
          task.status === 'COMPLETED' &&
          // In a real implementation, we would check if the agent worked on this task
          // For now, we'll assume the agent worked on tasks they created
          task.creator_id === agent.id
        );
        
        for (const task of workerTasks) {
          // Calculate financial outcome (reward minus stake)
          // In a real implementation, this would be calculated based on actual stakes and rewards
          const financialOutcome = task.reward_amount;
          
          // Randomly assign connected/disconnected status and activity for demo purposes
          // In a real implementation, this would come from the MCP server
          const isConnected = Math.random() > 0.3; // 70% chance of being connected
          const activities = ['WORKING', 'BROWSING', 'IDLE'];
          const randomActivity = activities[Math.floor(Math.random() * activities.length)];
          
          participatedTasks.push({
            ...task,
            financialOutcome,
            role: 'WORKER',
            agentStatus: isConnected ? 'CONNECTED' : 'DISCONNECTED',
            agentActivity: randomActivity as 'WORKING' | 'BROWSING' | 'IDLE'
          });
        }
      }
      
      // For judge agents, they earn a percentage of the reward amount
      for (const agent of userJudgeAgents) {
        const judgeTasks = tasks.filter(task =>
          (task.status === 'JUDGED' || task.status === 'COMPLETED') &&
          task.judges.includes(agent.id)
        );
        
        for (const task of judgeTasks) {
          // Calculate financial outcome (percentage of reward)
          // In a real implementation, this would be calculated based on actual judge compensation
          const financialOutcome = task.reward_amount * 0.1; // Assume judges get 10% of reward
          
          // Randomly assign connected/disconnected status and activity for demo purposes
          // In a real implementation, this would come from the MCP server
          const isConnected = Math.random() > 0.3; // 70% chance of being connected
          const activities = ['WORKING', 'BROWSING', 'IDLE'];
          const randomActivity = activities[Math.floor(Math.random() * activities.length)];
          
          participatedTasks.push({
            ...task,
            financialOutcome,
            role: 'JUDGE',
            agentStatus: isConnected ? 'CONNECTED' : 'DISCONNECTED',
            agentActivity: randomActivity as 'WORKING' | 'BROWSING' | 'IDLE'
          });
        }
      }
      
      taskStore.update(state => ({
        ...state,
        participatedTasks,
        loading: false
      }));
      
      return participatedTasks;
    } catch (error) {
      console.error('Error fetching tasks by agent:', error);
      taskStore.update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch tasks by agent'
      }));
      return [];
    }
  }
};