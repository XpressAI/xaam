<script>
  import { createEventDispatcher } from 'svelte';
  import { authStore } from '../stores/auth';
  import { walletStore } from '../stores/wallet';
  import { decryptTaskPayload } from '../utils/encryption';
  
  // Props
  export let task;
  
  // Determine if task is staked based on status
  $: isStaked = task && task.status !== 'CREATED';
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // State
  let stakeAmount = 0.1; // Default stake amount
  let deliverableUrl = '';
  let deliverableContent = '';
  let isSubmitting = false;
  let error = '';
  let successMessage = '';
  let decryptedPayload = null;
  let isDecrypting = false;
  let decryptionError = '';
  let isStaking = false;
  
  // Auth state
  let isAuthenticated = false;
  
  // Subscribe to auth store
  authStore.subscribe(state => {
    isAuthenticated = state.isAuthenticated;
  });
  
  // Format date
  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
  
  // Calculate time remaining
  function getTimeRemaining(dateString) {
    const deadline = new Date(dateString);
    const now = new Date();
    
    if (now > deadline) {
      return 'Expired';
    }
    
    const diffTime = deadline.getTime() - now.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor((diffTime % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    if (diffDays > 0) {
      return `${diffDays} days, ${diffHours} hours`;
    } else {
      return `${diffHours} hours`;
    }
  }
  
  // Handle stake
  async function handleStake() {
    console.log('Stake attempt - Auth state:', { isAuthenticated });
    console.log('Wallet store state:', $walletStore);
    
    // Get current auth state directly
    let currentAuthState = null;
    const unsubAuth = authStore.subscribe(state => {
      currentAuthState = state;
    });
    unsubAuth();
    console.log('TaskDetail: Current auth state from direct check:', currentAuthState);
    
    // Get current wallet state from both stores
    let mainWalletState = null;
    const unsubMainWallet = walletStore.subscribe(state => {
      mainWalletState = state;
    });
    unsubMainWallet();
    
    // Try to get lib wallet store state
    let libWalletState = null;
    try {
      const libWalletModule = await import('../lib/stores/wallet');
      const unsubLibWallet = libWalletModule.walletStore.subscribe(state => {
        libWalletState = state;
      });
      unsubLibWallet();
    } catch (e) {
      console.error('Error getting lib wallet state:', e);
    }
    
    console.log('TaskDetail: Wallet state comparison:', {
      mainWalletStore: mainWalletState,
      libWalletStore: libWalletState
    });
    
    if (!isAuthenticated) {
      console.error('Authentication check failed - user not authenticated in auth store');
      
      // If wallet is connected but auth is not authenticated, try to login
      if ($walletStore?.connected) {
        console.log('TaskDetail: Wallet connected but not authenticated, attempting to login');
        try {
          await authStore.loginWithWallet();
          console.log('TaskDetail: Auto-login successful, retrying stake');
          // Check if now authenticated
          let nowAuthenticated = false;
          const unsubAuth2 = authStore.subscribe(state => {
            nowAuthenticated = state.isAuthenticated;
          });
          unsubAuth2();
          console.log('TaskDetail: Is authenticated after auto-login:', nowAuthenticated);
          
          // If now authenticated, continue with stake
          if (nowAuthenticated) {
            if (stakeAmount <= 0) {
              error = 'Stake amount must be greater than 0';
              return;
            }
            console.log('Proceeding with stake after auto-login:', { taskId: task.id, amount: stakeAmount });
            await performStake();
            return;
          }
        } catch (err) {
          console.error('TaskDetail: Auto-login failed:', err);
        }
      }
      
      error = 'Please connect your wallet to stake on this task';
      return;
    }
    
    if (!$walletStore?.connected) {
      console.error('Wallet connection check failed - wallet not connected in wallet store');
      error = 'Please connect your wallet to stake on this task';
      return;
    }
    
    if (stakeAmount <= 0) {
      error = 'Stake amount must be greater than 0';
      return;
    }
    
    console.log('Proceeding with stake:', { taskId: task.id, amount: stakeAmount });
    await performStake();
  }
  
  // Perform the actual staking operation
  async function performStake() {
    try {
      isStaking = true;
      error = '';
      successMessage = '';
      
      // Dispatch the stake event to the parent component
      // This will trigger the actual staking operation in the parent
      dispatch('stake', { taskId: task.id, amount: stakeAmount });
      
      // Show success message
      successMessage = `Successfully staked ${stakeAmount} SOL on this task!`;
      
      // The parent component will update the task data after staking
      // so we don't need to update it locally anymore
      
    } catch (err) {
      console.error('Error during staking:', err);
      error = err instanceof Error ? err.message : 'Failed to stake on task';
    } finally {
      isStaking = false;
    }
  }
  
  // Decrypt task payload
  async function decryptPayload() {
    if (!task.encrypted_payload_url || !task.encryption_key) {
      decryptionError = 'Missing encrypted payload or encryption key';
      return;
    }
    
    try {
      isDecrypting = true;
      decryptionError = '';
      
      // In a real implementation, we would retrieve the agent's private key from secure storage
      // For demo purposes, we'll use a hardcoded private key (this would never be done in production)
      const mockPrivateKey = 'MC4CAQAwBQYDK2VwBCIEINTuctv5E1hK1bbY8fdp+K06/nwoy/HU++CXqI9EdVhC';
      
      // Decrypt the payload
      decryptedPayload = decryptTaskPayload(
        task.encrypted_payload_url,
        task.encryption_key,
        mockPrivateKey
      );
    } catch (error) {
      console.error('Decryption error:', error);
      decryptionError = `Error decrypting payload: ${error.message || 'Unknown error'}`;
      decryptedPayload = null;
    } finally {
      isDecrypting = false;
    }
  }
  
  // Handle submit deliverable
  function handleSubmit() {
    if (!isAuthenticated) {
      error = 'Please connect your wallet to submit a deliverable';
      return;
    }
    
    if (!deliverableUrl.trim()) {
      error = 'Deliverable URL is required';
      return;
    }
    
    if (!deliverableContent.trim()) {
      error = 'Deliverable content is required';
      return;
    }
    
    error = '';
    isSubmitting = true;
    
    // Parse deliverable content as JSON if possible
    let parsedContent;
    try {
      parsedContent = JSON.parse(deliverableContent);
    } catch (e) {
      // If not valid JSON, use as string
      parsedContent = deliverableContent;
    }
    
    // Simulate submission delay
    setTimeout(() => {
      dispatch('submit', {
        taskId: task.id,
        deliverableUrl,
        deliverableContent: parsedContent
      });
      isSubmitting = false;
    }, 1000);
  }
  
  // Handle back
  function handleBack() {
    dispatch('back');
  }
  
  // Get status badge color
  function getStatusColor(status) {
    switch (status) {
      case 'CREATED':
        return 'bg-blue-100 text-blue-800';
      case 'STAKED':
        return 'bg-purple-100 text-purple-800';
      case 'IN_PROGRESS':
        return 'bg-yellow-100 text-yellow-800';
      case 'SUBMITTED':
        return 'bg-orange-100 text-orange-800';
      case 'JUDGED':
        return 'bg-indigo-100 text-indigo-800';
      case 'COMPLETED':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }
</script>

<div class="bg-card rounded-lg shadow-sm border overflow-hidden">
  <!-- Header -->
  <div class="p-6 border-b">
    <div class="flex justify-between items-start">
      <div>
        <button 
          on:click={handleBack}
          class="text-muted-foreground hover:text-foreground mb-2 flex items-center"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-1">
            <path d="M19 12H5M12 19l-7-7 7-7"></path>
          </svg>
          Back to Tasks
        </button>
        <h2 class="text-2xl font-semibold">{task.title}</h2>
      </div>
      <span class="text-sm rounded-full px-3 py-1 {getStatusColor(task.status)}">
        {task.status}
      </span>
    </div>
  </div>
  
  <!-- Content -->
  <div class="p-6">
    <!-- Summary -->
    <div class="mb-6">
      <h3 class="text-lg font-medium mb-2">Summary</h3>
      <p class="text-muted-foreground">{task.summary}</p>
    </div>
    
    <!-- Details -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
      <div>
        <h3 class="text-lg font-medium mb-2">Details</h3>
        <div class="space-y-2">
          <div class="flex justify-between">
            <span class="text-muted-foreground">Reward:</span>
            <span class="font-medium">{task.reward_amount} {task.reward_currency}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-muted-foreground">Deadline:</span>
            <span class="font-medium">{formatDate(task.deadline)}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-muted-foreground">Time Remaining:</span>
            <span class="font-medium">{getTimeRemaining(task.deadline)}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-muted-foreground">Created:</span>
            <span class="font-medium">{formatDate(task.created_at)}</span>
          </div>
        </div>
      </div>
      
      <div>
        <h3 class="text-lg font-medium mb-2">Task Creator</h3>
        <div class="p-4 border rounded-md">
          <div class="text-sm text-muted-foreground mb-1">Creator ID:</div>
          <div class="font-mono text-sm break-all">{task.creator_id}</div>
        </div>
      </div>
    </div>
    
    <!-- Task Payload (only visible if staked) -->
    {#if isStaked}
      <div class="mb-6">
        <h3 class="text-lg font-medium mb-2">Task Payload</h3>
        <div class="p-4 border rounded-md bg-muted/50">
          <p class="text-muted-foreground mb-2">
            You have staked SOL on this task and can now access the task payload:
          </p>
          
          {#if !decryptedPayload && !isDecrypting}
            <button
              on:click={decryptPayload}
              class="bg-primary text-primary-foreground rounded-md px-4 py-2 hover:bg-primary/90 transition-colors mb-3"
            >
              Decrypt Payload
            </button>
            
            {#if decryptionError}
              <div class="p-3 bg-destructive/10 border border-destructive/20 rounded-md text-destructive text-sm mt-3">
                {decryptionError}
              </div>
            {/if}
            
            <div class="mt-3">
              <div class="text-sm font-medium mb-1">Encrypted Payload:</div>
              <div class="font-mono text-xs break-all bg-muted p-2 rounded">
                {task.encrypted_payload_url}
              </div>
            </div>
          {:else if isDecrypting}
            <div class="flex items-center space-x-2 text-muted-foreground">
              <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Decrypting payload...</span>
            </div>
          {:else}
            <div>
              <div class="text-sm font-medium mb-1">Decrypted Payload:</div>
              <div class="font-mono text-xs break-all bg-muted p-3 rounded max-h-60 overflow-y-auto">
                <pre>{JSON.stringify(decryptedPayload, null, 2)}</pre>
              </div>
            </div>
          {/if}
        </div>
      </div>
      
      <!-- Submit Deliverable (only if staked and not submitted) -->
      {#if task.status === 'STAKED' || task.status === 'IN_PROGRESS'}
        <div class="mb-6">
          <h3 class="text-lg font-medium mb-2">Submit Deliverable</h3>
          <div class="p-4 border rounded-md">
            <div class="space-y-4">
              <div>
                <label for="deliverableUrl" class="text-sm font-medium">Deliverable URL</label>
                <input
                  id="deliverableUrl"
                  type="text"
                  bind:value={deliverableUrl}
                  class="w-full px-3 py-2 border rounded-md bg-background mt-1"
                  placeholder="Enter URL to your encrypted deliverable"
                />
                <p class="text-xs text-muted-foreground mt-1">
                  This should be a URL to your encrypted deliverable. In a real implementation,
                  you would upload and encrypt your deliverable here.
                </p>
              </div>
              
              <div>
                <label for="deliverableContent" class="text-sm font-medium">Deliverable Content</label>
                <textarea
                  id="deliverableContent"
                  bind:value={deliverableContent}
                  class="w-full px-3 py-2 border rounded-md bg-background mt-1 min-h-[150px] font-mono text-sm"
                  placeholder={`{"description": "Deliverable description", "results": ["result1", "result2"], "data": {"key": "value"}}`}
                ></textarea>
                <p class="text-xs text-muted-foreground mt-1">
                  Enter your deliverable content as JSON. This will be encrypted for the judges.
                </p>
              </div>
              
              <button 
                on:click={handleSubmit}
                disabled={isSubmitting}
                class="w-full bg-primary text-primary-foreground rounded-md px-4 py-2 hover:bg-primary/90 transition-colors disabled:opacity-50"
              >
                {#if isSubmitting}
                  Submitting...
                {:else}
                  Submit Deliverable
                {/if}
              </button>
            </div>
          </div>
        </div>
      {/if}
    {:else if task.status === 'CREATED'}
      <!-- Stake to Access -->
      <div class="mb-6">
        <h3 class="text-lg font-medium mb-2">Stake to Access</h3>
        <div class="p-4 border rounded-md">
          <p class="text-muted-foreground mb-4">
            Stake SOL to access the encrypted task details and work on this task.
          </p>
          
          <div class="space-y-4">
            <div>
              <label for="stakeAmount" class="text-sm font-medium">Stake Amount (SOL)</label>
              <input
                id="stakeAmount"
                type="number"
                bind:value={stakeAmount}
                min="0.01"
                step="0.01"
                class="w-full px-3 py-2 border rounded-md bg-background mt-1"
              />
            </div>
            
            <button
              on:click={handleStake}
              disabled={isStaking}
              class="w-full bg-primary text-primary-foreground rounded-md px-4 py-2 hover:bg-primary/90 transition-colors disabled:opacity-50"
            >
              {#if isStaking}
                <span class="flex items-center justify-center">
                  <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Staking...
                </span>
              {:else}
                Stake {stakeAmount} SOL & Access Task
              {/if}
            </button>
          </div>
        </div>
      </div>
    {/if}
    
    <!-- Success message -->
    {#if successMessage}
      <div class="p-3 bg-green-100 border border-green-200 rounded-md text-green-800 text-sm mb-6">
        {successMessage}
      </div>
    {/if}
    
    <!-- Error message -->
    {#if error}
      <div class="p-3 bg-destructive/10 border border-destructive/20 rounded-md text-destructive text-sm mb-6">
        {error}
      </div>
    {/if}
  </div>
</div>