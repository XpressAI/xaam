<script>
  import TaskDetail from '../../../components/TaskDetail.svelte';
  import { goto } from '$app/navigation';
  import { walletStore } from '../../../stores/wallet';
  import { authStore } from '../../../stores/auth';
  import { tasksStore } from '../../../stores/tasks';
  import { onMount } from 'svelte';
  import { api } from '$lib/api/client';
  
  // The task data is loaded by +page.js and passed as a prop
  export let data;
  
  // Check wallet and auth state on mount
  onMount(async () => {
    console.log('TaskDetailPage: Component mounted');
    
    // Log wallet connection state
    console.log('TaskDetailPage: Checking wallet and auth state');
    
    // Try to auto-login if needed
    try {
      // Check if wallet is connected
      let isWalletConnected = false;
      let isAuthenticated = false;
      
      // Get wallet state
      walletStore.subscribe(state => {
        isWalletConnected = state.connected;
        console.log('TaskDetailPage: Wallet connected:', isWalletConnected);
      })();
      
      // Get auth state
      authStore.subscribe(state => {
        isAuthenticated = state.isAuthenticated;
        console.log('TaskDetailPage: Is authenticated:', isAuthenticated);
      })();
      
      // If wallet is connected but not authenticated, try to login
      if (isWalletConnected && !isAuthenticated) {
        console.log('TaskDetailPage: Wallet connected but not authenticated, attempting to login');
        await authStore.loginWithWallet();
        console.log('TaskDetailPage: Auto-login completed');
      }
    } catch (err) {
      console.error('TaskDetailPage: Error during auto-login check:', err);
    }
  });
  
  // Handle stake event
  async function handleStake(event) {
    try {
      // Call the wallet store to stake on the task
      const stakeResult = await walletStore.stakeOnTask(event.detail.taskId, event.detail.amount);
      console.log('Stake result:', stakeResult);
      
      // Directly update the task status in the component state
      // This ensures the UI updates immediately without relying on localStorage
      if (data.task && data.task.id === event.detail.taskId) {
        // Create a new task object with updated status
        data.task = {
          ...data.task,
          status: 'STAKED',
          updated_at: new Date().toISOString()
        };
        
        console.log('Task status updated directly in component state:', data.task);
      }
    } catch (error) {
      console.error('Failed to stake on task:', error);
      alert(`Failed to stake on task: ${error.message || 'Unknown error'}`);
    }
  }
  
  // Handle submit event
  async function handleSubmit(event) {
    try {
      // In a real app, this would call an API to submit the deliverable
      console.log('Submitting deliverable:', event.detail);
      // Reload the page to get updated task data
      window.location.reload();
    } catch (error) {
      console.error('Failed to submit deliverable:', error);
      alert(`Failed to submit deliverable: ${error.message || 'Unknown error'}`);
    }
  }
  
  // Handle back event
  function handleBack() {
    goto('/tasks');
  }
</script>

{#if data.task}
  <TaskDetail
    task={data.task}
    on:stake={handleStake}
    on:submit={handleSubmit}
    on:back={handleBack}
  />
{:else}
  <div class="p-6 text-center">
    <p class="text-destructive mb-4">Task not found</p>
    <a href="/tasks" class="bg-secondary text-secondary-foreground rounded-lg px-4 py-2 hover:bg-secondary/80 transition-colors">
      Back to Tasks
    </a>
  </div>
{/if}