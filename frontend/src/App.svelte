<script lang="ts">
  import { onMount } from 'svelte';
  import { walletStore } from './stores/wallet';
  import { routeStore } from './stores/route';
  import { setMockWalletState, clearWalletState, getWalletStateFromStorage } from './utils/debug';
  
  // Import routes
  import Home from './routes/Home.svelte';
  import Tasks from './routes/Tasks.svelte';
  import TaskCreate from './routes/TaskCreate.svelte';
  import TaskDetail from './routes/TaskDetail.svelte';
  import Dashboard from './routes/Dashboard.svelte';
  
  // Component state
  let isLoading = true;
  let debugMode = false;
  
  // Subscribe to route store
  let currentRoute = '/';
  let params: Record<string, string> = {};
  
  routeStore.subscribe(state => {
    currentRoute = state.currentRoute;
    params = state.params;
  });
  
  // Debug functions
  function toggleDebugMode() {
    debugMode = !debugMode;
  }
  
  function setMockWallet() {
    setMockWalletState();
  }
  
  function clearWallet() {
    clearWalletState();
  }
  
  function checkWalletState() {
    const state = getWalletStateFromStorage();
    console.log('Current wallet state in localStorage:', state);
    walletStore.checkConnection();
  }
  
  onMount(() => {
    // Initialize route store
    routeStore.init();
    
    // Check wallet connection on app initialization
    walletStore.checkConnection();
    
    // Initialize app
    isLoading = false;
    
    // Check for debug mode in URL
    if (window.location.search.includes('debug=true')) {
      debugMode = true;
    }
  });
</script>

{#if isLoading}
  <div class="flex justify-center items-center h-screen bg-background text-foreground">
    <p class="text-xl">Loading XAAM...</p>
  </div>
{:else}
  <!-- Debug Panel -->
  {#if debugMode}
    <div class="fixed top-0 right-0 bg-black/80 text-white p-4 z-50 rounded-bl-lg">
      <h3 class="text-sm font-bold mb-2">Debug Panel</h3>
      <div class="flex flex-col space-y-2">
        <button
          on:click={setMockWallet}
          class="bg-green-600 text-white text-xs px-2 py-1 rounded"
        >
          Set Mock Wallet
        </button>
        <button
          on:click={clearWallet}
          class="bg-red-600 text-white text-xs px-2 py-1 rounded"
        >
          Clear Wallet
        </button>
        <button
          on:click={checkWalletState}
          class="bg-blue-600 text-white text-xs px-2 py-1 rounded"
        >
          Check Wallet State
        </button>
        <div class="text-xs mt-2">
          Current Route: {currentRoute}
        </div>
      </div>
    </div>
  {/if}
  
  <div class="min-h-screen bg-background text-foreground">
    {#if currentRoute === '/' || currentRoute === ''}
      <Home />
    {:else if currentRoute === '/tasks'}
      <Tasks />
    {:else if currentRoute === '/tasks/create'}
      <TaskCreate />
    {:else if currentRoute.startsWith('/tasks/')}
      <TaskDetail params={{ id: params['id'] || '' }} />
    {:else if currentRoute === '/dashboard'}
      <Dashboard />
    {:else}
      <Home />
    {/if}
  </div>
  
  <!-- Debug Mode Toggle -->
  <button
    on:click={toggleDebugMode}
    class="fixed bottom-4 right-4 bg-gray-800 text-white text-xs px-2 py-1 rounded-full opacity-30 hover:opacity-100"
  >
    {debugMode ? 'Hide Debug' : 'Debug'}
  </button>
{/if}

<style>
  :global(html) {
    background-color: theme('colors.background');
  }
</style>