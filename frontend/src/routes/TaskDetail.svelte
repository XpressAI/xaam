<script lang="ts">
  import { onMount } from 'svelte';
  import { tasksStore } from '../stores/tasks';
  import { authStore } from '../stores/auth';
  import { walletStore } from '../stores/wallet';
  import Layout from '../components/Layout.svelte';
  import TaskDetailComponent from '../components/TaskDetail.svelte';
  
  // Props
  export let params = { id: '' };
  
  // State
  let isLoading = true;
  let error = '';
  let task: any = null;
  let isStaked = false;
  let isAuthenticated = false;
  
  // Subscribe to auth store
  authStore.subscribe(state => {
    isAuthenticated = state.isAuthenticated;
  });
  
  // Load task on mount
  onMount(() => {
    if (params.id) {
      loadTask(params.id);
    } else {
      error = 'Task ID not provided';
      isLoading = false;
    }
    
    return () => {};
  });
  
  // Load task
  async function loadTask(taskId: string) {
    isLoading = true;
    error = '';
    
    try {
      const loadedTask = await tasksStore.fetchTask(taskId);
      task = loadedTask;
      
      // Check if user has staked on this task
      // In a real app, this would check the blockchain
      if (task.status !== 'CREATED') {
        isStaked = true;
      }
    } catch (err) {
      console.error('Failed to load task:', err);
      error = err instanceof Error ? err.message : 'Failed to load task';
    } finally {
      isLoading = false;
    }
  }
  
  // Handle stake on task
  async function handleStake(event: CustomEvent<{ taskId: string; amount: number }>) {
    if (!isAuthenticated) {
      error = 'Please connect your wallet to stake on this task';
      return;
    }
    
    error = '';
    isLoading = true;
    
    try {
      await walletStore.stakeOnTask(event.detail.taskId, event.detail.amount);
      
      // Reload task to get updated status
      await loadTask(event.detail.taskId);
      
      isStaked = true;
    } catch (err) {
      console.error('Failed to stake on task:', err);
      error = err instanceof Error ? err.message : 'Failed to stake on task';
    } finally {
      isLoading = false;
    }
  }
  
  // Handle submit deliverable
  async function handleSubmit(event: CustomEvent<{ taskId: string; deliverableUrl: string }>) {
    if (!isAuthenticated) {
      error = 'Please connect your wallet to submit a deliverable';
      return;
    }
    
    error = '';
    isLoading = true;
    
    try {
      // Get current user ID
      let agentId = '';
      
      const unsubscribeAuth = authStore.subscribe(state => {
        if (state.currentUser) {
          agentId = state.currentUser.id;
        }
      });
      unsubscribeAuth();
      
      if (!agentId) {
        throw new Error('User ID not found');
      }
      
      // In a real app, this would call the API to submit a deliverable
      console.log('Submitting deliverable:', {
        taskId: event.detail.taskId,
        agentId,
        deliverableUrl: event.detail.deliverableUrl
      });
      
      // Mock successful submission
      setTimeout(async () => {
        // Reload task to get updated status
        await loadTask(event.detail.taskId);
        isLoading = false;
      }, 1000);
    } catch (err) {
      console.error('Failed to submit deliverable:', err);
      error = err instanceof Error ? err.message : 'Failed to submit deliverable';
      isLoading = false;
    }
  }
  
  // Handle back
  function handleBack() {
    window.location.href = '/tasks';
  }
</script>

<Layout>
  <div class="max-w-4xl mx-auto">
    {#if isLoading}
      <!-- Loading state -->
      <div class="flex justify-center items-center h-64">
        <div class="text-xl text-muted-foreground">Loading task details...</div>
      </div>
    {:else if error}
      <!-- Error state -->
      <div class="bg-destructive/10 border border-destructive/20 rounded-lg p-6 text-center">
        <p class="text-destructive mb-4">{error}</p>
        <button 
          on:click={handleBack}
          class="bg-secondary text-secondary-foreground rounded-lg px-4 py-2 hover:bg-secondary/80 transition-colors"
        >
          Back to Tasks
        </button>
      </div>
    {:else if task}
      <!-- Task detail -->
      <TaskDetailComponent 
        task={task} 
        isStaked={isStaked}
        on:stake={handleStake}
        on:submit={handleSubmit}
        on:back={handleBack}
      />
    {:else}
      <!-- Task not found -->
      <div class="bg-destructive/10 border border-destructive/20 rounded-lg p-6 text-center">
        <p class="text-destructive mb-4">Task not found</p>
        <button 
          on:click={handleBack}
          class="bg-secondary text-secondary-foreground rounded-lg px-4 py-2 hover:bg-secondary/80 transition-colors"
        >
          Back to Tasks
        </button>
      </div>
    {/if}
    
    <!-- Loading overlay -->
    {#if isLoading}
      <div class="fixed inset-0 bg-background/80 flex items-center justify-center z-50">
        <div class="bg-card p-6 rounded-lg shadow-lg text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p class="text-lg">Loading...</p>
        </div>
      </div>
    {/if}
  </div>
</Layout>