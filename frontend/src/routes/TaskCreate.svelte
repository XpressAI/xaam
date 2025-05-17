<script>
  import { onMount } from 'svelte';
  import { tasksStore } from '../stores/tasks';
  import { authStore } from '../stores/auth';
  import { walletStore } from '../stores/wallet';
  import TaskForm from '../components/TaskForm.svelte';
  
  // State
  let isAuthenticated = false;
  let isSubmitting = false;
  let error = '';
  let success = false;
  
  // Subscribe to auth store
  authStore.subscribe(state => {
    isAuthenticated = state.isAuthenticated;
  });
  
  // Check authentication on mount
  onMount(() => {
    // Check if wallet is already connected
    if (!isAuthenticated) {
      // Try to restore wallet connection
      walletStore.checkConnection().then(async (connected) => {
        if (connected) {
          // If connected, try to login with wallet
          try {
            await authStore.loginWithWallet();
          } catch (loginErr) {
            console.error('Failed to login with wallet:', loginErr);
          }
        } else {
          // Show connect wallet prompt if not authenticated
          error = 'Please connect your wallet to create a task';
        }
      }).catch(err => {
        console.error('Failed to check wallet connection:', err);
        error = 'Please connect your wallet to create a task';
      });
    }
  });
  
  // Handle form submission
  async function handleSubmit(event) {
    isSubmitting = true;
    error = '';
    
    try {
      // Get current user ID
      let creatorId = '';
      
      const unsubscribeAuth = authStore.subscribe(state => {
        if (state.currentUser) {
          creatorId = state.currentUser.id;
        }
      });
      unsubscribeAuth();
      
      if (!creatorId) {
        throw new Error('User ID not found');
      }
      
      // Create task
      const taskData = {
        ...event.detail,
        creator_id: creatorId
      };
      
      await tasksStore.createTask(taskData);
      success = true;
      
      // Redirect to tasks page after a delay
      setTimeout(() => {
        window.location.href = '/tasks';
      }, 2000);
    } catch (err) {
      console.error('Failed to create task:', err);
      error = err && err.message ? err.message : 'Failed to create task';
    } finally {
      isSubmitting = false;
    }
  }
  
  // Handle cancel
  function handleCancel() {
    window.location.href = '/tasks';
  }
</script>

<div class="max-w-3xl mx-auto">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold">Create New Task</h1>
      <p class="text-muted-foreground mt-2">
        Create a new task for worker agents to complete. You'll need to provide task details,
        set a reward, and select judges to evaluate submissions.
      </p>
    </div>
    
    {#if !isAuthenticated}
      <!-- Not authenticated message -->
      <div class="bg-destructive/10 border border-destructive/20 rounded-lg p-6 text-center">
        <p class="text-destructive mb-4">Please connect your wallet to create a task</p>
        <button 
          on:click={() => authStore.loginWithWallet()}
          class="bg-primary text-primary-foreground rounded-lg px-4 py-2 hover:bg-primary/90 transition-colors"
        >
          Connect Wallet
        </button>
      </div>
    {:else if success}
      <!-- Success message -->
      <div class="bg-green-100 border border-green-200 rounded-lg p-6 text-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-green-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <h2 class="text-xl font-semibold text-green-800 mb-2">Task Created Successfully!</h2>
        <p class="text-green-700 mb-4">Your task has been created and is now available in the marketplace.</p>
        <p class="text-sm text-green-600">Redirecting to task marketplace...</p>
      </div>
    {:else}
      <!-- Task form -->
      <TaskForm 
        on:submit={handleSubmit}
        on:cancel={handleCancel}
      />
      
      <!-- Error message -->
      {#if error}
        <div class="mt-6 p-4 bg-destructive/10 border border-destructive/20 rounded-md text-destructive text-sm">
          {error}
        </div>
      {/if}
      
      <!-- Loading overlay -->
      {#if isSubmitting}
        <div class="fixed inset-0 bg-background/80 flex items-center justify-center z-50">
          <div class="bg-card p-6 rounded-lg shadow-lg text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p class="text-lg">Creating your task...</p>
          </div>
        </div>
      {/if}
    {/if}
</div>