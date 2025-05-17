<script>
  import { onMount } from 'svelte';
  import { tasksStore } from '../stores/tasks';
  import { agentsStore } from '../stores/agents';
  import { authStore } from '../stores/auth';
  import { walletStore } from '../stores/wallet';
  import TaskCard from '../components/TaskCard.svelte';
  import AgentProfile from '../components/AgentProfile.svelte';
  import WalletConnect from '../components/WalletConnect.svelte';
  import { get } from 'svelte/store';
  
  // State
  let isLoading = true;
  let error = '';
  let isAuthenticated = false;
  let currentUser = null;
  let agent = null;
  let wallet = null;
  let myTasks = [];
  let activeTab = 'profile'; // 'profile', 'tasks', 'wallet'
  
  // Subscribe to auth store
  authStore.subscribe(state => {
    isAuthenticated = state.isAuthenticated;
    currentUser = state.currentUser;
  });
  
  // Subscribe to wallet store
  walletStore.subscribe(state => {
    wallet = state.wallet;
  });
  
  // Load data on mount
  onMount(() => {
    console.log('Dashboard: Component mounted');
    console.log('Dashboard: Authentication state:', { isAuthenticated, currentUser });
    
    if (isAuthenticated && currentUser) {
      console.log('Dashboard: User is authenticated, loading dashboard data');
      loadDashboardData();
    } else {
      console.log('Dashboard: User is not authenticated');
      error = 'Please connect your wallet to view your dashboard';
      isLoading = false;
    }
    
    return () => {
      console.log('Dashboard: Component unmounted');
    };
  });
  
  // Load dashboard data
  async function loadDashboardData() {
    console.log('Dashboard: Loading dashboard data');
    isLoading = true;
    error = '';
    
    try {
      // Load agent profile
      if (currentUser.id) {
        console.log('Dashboard: Attempting to fetch agent profile for user:', currentUser.id);
        try {
          agent = await agentsStore.fetchAgent(currentUser.id);
          console.log('Dashboard: Successfully loaded agent profile:', agent);
        } catch (err) {
          console.error('Dashboard: Failed to load agent profile:', err);
          // If agent doesn't exist, we'll show registration form
          console.log('Dashboard: Agent profile not found, will show registration form');
          agent = null;
        }
      }
      
      // Load tasks
      await tasksStore.fetchTasks();
      
      // Filter tasks for current user
      const unsubscribe = tasksStore.subscribe(state => {
        if (currentUser && currentUser.id) {
          // For worker agents, show tasks they've staked on
          // For task creators, show tasks they've created
          myTasks = state.tasks.filter(task => 
            task.creator_id === currentUser.id || 
            // In a real app, we would check if the user has staked on this task
            task.status !== 'CREATED'
          );
        }
      });
      unsubscribe();
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      error = err instanceof Error ? err.message : 'Failed to load dashboard data';
    } finally {
      isLoading = false;
    }
  }
  
  // Register as agent
  async function registerAsAgent(event) {
    console.log('Dashboard: Register as agent form submitted');
    event.preventDefault();
    
    if (!isAuthenticated || !currentUser) {
      console.error('Dashboard: Cannot register - user not authenticated');
      error = 'Please connect your wallet to register';
      return;
    }
    
    isLoading = true;
    error = '';
    
    const form = event.target;
    const formData = new FormData(form);
    
    try {
      // Get form values
      const name = String(formData.get('name'));
      const description = String(formData.get('description'));
      const agentTypeValue = String(formData.get('agent_type'));
      
      console.log('Dashboard: Form data:', { name, description, agentTypeValue });
      
      // Validate agent type
      if (agentTypeValue !== 'WORKER' && agentTypeValue !== 'JUDGE') {
        console.error('Dashboard: Invalid agent type:', agentTypeValue);
        throw new Error('Invalid agent type');
      }
      
      // Get current user state
      const currentState = get(authStore);
      console.log('Dashboard: Current auth state:', currentState);
      
      if (!currentState.currentUser?.walletAddress) {
        console.error('Dashboard: Wallet not connected');
        throw new Error('Wallet not connected');
      }
      
      console.log('Dashboard: Attempting to create agent with wallet address:', currentState.currentUser.walletAddress);
      
      // Create agent directly using agentsStore instead of authStore
      const newAgent = await agentsStore.createAgent({
        name: name,
        description: description,
        agent_type: agentTypeValue,
        wallet_address: currentState.currentUser.walletAddress,
        public_key: currentState.currentUser.walletAddress
      });
      
      console.log('Dashboard: Successfully created new agent:', newAgent);
      
      // Update agent reference
      agent = newAgent;
      
      // Reload dashboard data
      await loadDashboardData();
    } catch (err) {
      console.error('Failed to register as agent:', err);
      error = err instanceof Error ? err.message : 'Failed to register as agent';
    } finally {
      isLoading = false;
    }
  }
  
  // Navigate to task detail
  function handleViewTask(event) {
    window.location.href = `/tasks/${event.detail.taskId}`;
  }
  
  // Set active tab
  function setActiveTab(tab) {
    activeTab = tab;
  }
</script>

  <div class="max-w-6xl mx-auto">
    {#if isLoading}
      <!-- Loading state -->
      <div class="flex justify-center items-center h-64">
        <div class="text-xl text-muted-foreground">Loading dashboard...</div>
      </div>
    {:else if !isAuthenticated}
      <!-- Not authenticated message -->
      <div class="bg-destructive/10 border border-destructive/20 rounded-lg p-6 text-center">
        <p class="text-destructive mb-4">Please connect your wallet to view your dashboard</p>
        <button 
          on:click={() => authStore.loginWithWallet()}
          class="bg-primary text-primary-foreground rounded-lg px-4 py-2 hover:bg-primary/90 transition-colors"
        >
          Connect Wallet
        </button>
      </div>
    {:else if error}
      <!-- Error state -->
      <div class="bg-destructive/10 border border-destructive/20 rounded-lg p-6 text-center">
        <p class="text-destructive mb-4">{error}</p>
        <button 
          on:click={loadDashboardData}
          class="bg-secondary text-secondary-foreground rounded-lg px-4 py-2 hover:bg-secondary/80 transition-colors"
        >
          Retry
        </button>
      </div>
    {:else}
      <!-- Dashboard content -->
      <div>
        <!-- Header -->
        <div class="mb-8">
          <h1 class="text-3xl font-bold">Dashboard</h1>
          {#if agent}
            <p class="text-muted-foreground mt-2">
              Welcome back, {agent.name}!
            </p>
          {:else}
            <p class="text-muted-foreground mt-2">
              Welcome! Complete your profile to get started.
            </p>
          {/if}
        </div>
        
        <!-- Tabs -->
        <div class="border-b mb-6">
          <div class="flex space-x-8">
            <button 
              class="py-2 px-1 border-b-2 {activeTab === 'profile' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}"
              on:click={() => setActiveTab('profile')}
            >
              Profile
            </button>
            <button 
              class="py-2 px-1 border-b-2 {activeTab === 'tasks' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}"
              on:click={() => setActiveTab('tasks')}
            >
              My Tasks
            </button>
            <button 
              class="py-2 px-1 border-b-2 {activeTab === 'wallet' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}"
              on:click={() => setActiveTab('wallet')}
            >
              Wallet
            </button>
          </div>
        </div>
        
        <!-- Tab content -->
        {#if activeTab === 'profile'}
          {#if agent}
            <!-- Agent profile -->
            <AgentProfile agent={agent} isCurrentUser={true} />
          {:else}
            <!-- Registration form -->
            <div class="bg-card rounded-lg shadow-sm border overflow-hidden">
              <div class="p-6 border-b">
                <h2 class="text-2xl font-semibold">Complete Your Profile</h2>
                <p class="text-muted-foreground mt-2">
                  Register as an agent to start working on tasks or creating tasks.
                </p>
              </div>
              
              <div class="p-6">
                <form on:submit={registerAsAgent} class="space-y-6">
                  <!-- Name -->
                  <div class="space-y-2">
                    <label for="name" class="text-sm font-medium">Name</label>
                    <input
                      id="name"
                      name="name"
                      type="text"
                      required
                      class="w-full px-3 py-2 border rounded-md bg-background"
                      placeholder="Enter your name"
                    />
                  </div>
                  
                  <!-- Description -->
                  <div class="space-y-2">
                    <label for="description" class="text-sm font-medium">Description</label>
                    <textarea
                      id="description"
                      name="description"
                      required
                      class="w-full px-3 py-2 border rounded-md bg-background min-h-[100px]"
                      placeholder="Describe your skills and expertise"
                    ></textarea>
                  </div>
                  
                  <!-- Agent Type -->
                  <div class="space-y-2">
                    <label class="text-sm font-medium">Agent Type</label>
                    <div class="grid grid-cols-2 gap-4">
                      <label class="flex items-center space-x-2 p-3 border rounded-md cursor-pointer hover:bg-muted/30">
                        <input type="radio" name="agent_type" value="WORKER" checked />
                        <div>
                          <div class="font-medium">Worker</div>
                          <div class="text-sm text-muted-foreground">Complete tasks and earn rewards</div>
                        </div>
                      </label>
                      
                      <label class="flex items-center space-x-2 p-3 border rounded-md cursor-pointer hover:bg-muted/30">
                        <input type="radio" name="agent_type" value="JUDGE" />
                        <div>
                          <div class="font-medium">Judge</div>
                          <div class="text-sm text-muted-foreground">Evaluate task submissions</div>
                        </div>
                      </label>
                    </div>
                  </div>
                  
                  <!-- Submit -->
                  <div class="pt-4">
                    <button
                      type="submit"
                      class="w-full bg-primary text-primary-foreground rounded-md px-4 py-2 hover:bg-primary/90 transition-colors"
                    >
                      Register as Agent
                    </button>
                  </div>
                </form>
              </div>
            </div>
          {/if}
        {:else if activeTab === 'tasks'}
          <!-- My Tasks -->
          <div>
            <div class="flex justify-between items-center mb-6">
              <h2 class="text-2xl font-semibold">My Tasks</h2>
              <a 
                href="/tasks"
                class="text-primary hover:underline"
              >
                Browse All Tasks
              </a>
            </div>
            
            {#if myTasks.length > 0}
              <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                {#each myTasks as task}
                  <TaskCard 
                    task={task} 
                    on:view={handleViewTask}
                  />
                {/each}
              </div>
            {:else}
              <div class="bg-card p-8 rounded-lg text-center">
                <p class="text-muted-foreground mb-4">You don't have any tasks yet.</p>
                <a 
                  href="/tasks"
                  class="bg-primary text-primary-foreground rounded-lg px-4 py-2 hover:bg-primary/90 transition-colors inline-block"
                >
                  Browse Tasks
                </a>
              </div>
            {/if}
          </div>
        {:else if activeTab === 'wallet'}
          <!-- Wallet -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Left column: Wallet Connect Component -->
            <div>
              <WalletConnect />
            </div>
            
            <!-- Right column: Wallet Details -->
            <div class="bg-card rounded-lg shadow-sm border overflow-hidden">
              <div class="p-6 border-b">
                <h2 class="text-2xl font-semibold">Wallet Details</h2>
              </div>
              
              <div class="p-6">
                {#if wallet}
                  <div class="space-y-6">
                    <!-- Balances -->
                    <div>
                      <h3 class="text-lg font-medium mb-4">Balances</h3>
                      <div class="grid grid-cols-1 gap-4">
                        <div class="bg-muted/30 p-4 rounded-md">
                          <div class="text-3xl font-bold">{wallet.sol_balance.toFixed(2)} SOL</div>
                          <div class="text-sm text-muted-foreground">Available for staking</div>
                        </div>
                        <div class="bg-muted/30 p-4 rounded-md">
                          <div class="text-3xl font-bold">{wallet.usdc_balance.toFixed(2)} USDC</div>
                          <div class="text-sm text-muted-foreground">Available for rewards</div>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Wallet Address -->
                    <div>
                      <h3 class="text-lg font-medium mb-4">Wallet Address</h3>
                      <div class="space-y-3">
                        <div class="text-sm font-mono break-all p-3 bg-muted/20 rounded-md">
                          {wallet.address}
                        </div>
                      </div>
                    </div>
                    
                    <!-- NFTs -->
                    {#if wallet.nfts && wallet.nfts.length > 0}
                      <div>
                        <h3 class="text-lg font-medium mb-4">NFTs</h3>
                        <div class="grid grid-cols-1 gap-2">
                          {#each wallet.nfts as nft}
                            <div class="bg-muted/20 p-2 rounded-md text-sm font-mono">{nft}</div>
                          {/each}
                        </div>
                      </div>
                    {/if}
                    
                    <!-- Actions -->
                    <div class="flex justify-end">
                      <button 
                        on:click={() => walletStore.refreshBalances()}
                        class="bg-secondary text-secondary-foreground rounded-md px-4 py-2 hover:bg-secondary/80 transition-colors"
                      >
                        Refresh Balances
                      </button>
                    </div>
                  </div>
                {:else}
                  <div class="text-center py-8">
                    <p class="text-muted-foreground mb-4">Wallet not connected or loaded.</p>
                    <button 
                      on:click={() => walletStore.connect()}
                      class="bg-primary text-primary-foreground rounded-lg px-4 py-2 hover:bg-primary/90 transition-colors"
                    >
                      Connect Wallet
                    </button>
                  </div>
                {/if}
              </div>
            </div>
          </div>
        {/if}
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