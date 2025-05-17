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

// Task store state
interface TasksState {
  tasks: Task[];
  currentTask: Task | null;
  loading: boolean;
  error: string | null;
  filters: {
    status: string | null;
    search: string;
    sortBy: 'deadline' | 'reward_amount' | 'created_at';
    sortDirection: 'asc' | 'desc';
  };
}

// Initial state
const initialState: TasksState = {
  tasks: [],
  currentTask: null,
  loading: false,
  error: null,
  filters: {
    status: null,
    search: '',
    sortBy: 'deadline',
    sortDirection: 'asc'
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
  }
};