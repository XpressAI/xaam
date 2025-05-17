<script lang="ts">
  import { onMount } from 'svelte';
  import { authStore } from '../stores/auth';
  import { walletStore } from '../stores/wallet';
  import { routeStore } from '../stores/route';
  
  // State
  let isMenuOpen = false;
  
  // Toggle mobile menu
  function toggleMenu() {
    isMenuOpen = !isMenuOpen;
  }
  
  // Connect wallet
  async function connectWallet() {
    try {
      await authStore.loginWithWallet();
    } catch (error) {
      console.error('Failed to connect wallet:', error);
    }
  }
  
  // Disconnect wallet
  async function disconnectWallet() {
    try {
      await authStore.logout();
    } catch (error) {
      console.error('Failed to disconnect wallet:', error);
    }
  }
  
  // Auth state
  let isAuthenticated = false;
  let currentUser = null;
  let walletAddress = '';
  let solBalance = 0;
  let usdcBalance = 0;
  let connected = false;
  
  // Subscribe to auth store
  const unsubscribeAuth = authStore.subscribe(state => {
    isAuthenticated = state.isAuthenticated;
    currentUser = state.currentUser;
  });
  
  // Subscribe to wallet store
  const unsubscribeWallet = walletStore.subscribe(state => {
    connected = state.connected;
    if (state.wallet) {
      walletAddress = state.wallet.address;
      solBalance = state.wallet.sol_balance;
      usdcBalance = state.wallet.usdc_balance;
    }
  });
  
  // Subscribe to route store
  const unsubscribeRoute = routeStore.subscribe(state => {
    // When route changes, check wallet connection
    console.log('Layout detected route change to:', state.currentRoute);
    checkWalletConnection();
  });
  
  // Check wallet connection on component mount
  async function checkWalletConnection() {
    try {
      await walletStore.checkConnection();
    } catch (error) {
      console.error('Error checking wallet connection:', error);
    }
  }
  
  // Clean up subscriptions
  onMount(() => {
    // Check for existing wallet connection
    checkWalletConnection();
    
    return () => {
      unsubscribeAuth();
      unsubscribeWallet();
      unsubscribeRoute();
    };
  });
</script>

<div class="min-h-screen flex flex-col bg-background">
  <!-- Header -->
  <header class="bg-card shadow-sm border-b">
    <div class="container mx-auto px-4 py-4 flex justify-between items-center">
      <!-- Logo -->
      <a href="/" class="text-2xl font-bold text-primary">XAAM</a>
      
      <!-- Desktop Navigation -->
      <nav class="hidden md:flex items-center space-x-6">
        <a href="/" class="text-foreground hover:text-primary transition-colors">Home</a>
        <a href="/tasks" class="text-foreground hover:text-primary transition-colors">Tasks</a>
        {#if isAuthenticated}
          <a href="/dashboard" class="text-foreground hover:text-primary transition-colors">Dashboard</a>
        {/if}
        
        <!-- Wallet Connection -->
        {#if connected}
          <div class="flex items-center space-x-2">
            <div class="bg-muted rounded-lg px-3 py-1 text-sm">
              <span class="font-medium">{solBalance.toFixed(2)} SOL</span>
              <span class="mx-1">|</span>
              <span class="font-medium">{usdcBalance.toFixed(2)} USDC</span>
            </div>
            <button
              on:click={disconnectWallet}
              class="bg-destructive text-destructive-foreground rounded-lg px-3 py-1 text-sm hover:bg-destructive/90 transition-colors"
            >
              Disconnect
            </button>
          </div>
        {:else}
          <button
            on:click={connectWallet}
            class="bg-primary text-primary-foreground rounded-lg px-4 py-2 hover:bg-primary/90 transition-colors"
          >
            Connect Wallet
          </button>
        {/if}
      </nav>
      
      <!-- Mobile Menu Button -->
      <button 
        on:click={toggleMenu}
        class="md:hidden text-foreground p-2"
        aria-label="Toggle menu"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          {#if isMenuOpen}
            <path d="M18 6L6 18M6 6l12 12"></path>
          {:else}
            <path d="M4 12h16M4 6h16M4 18h16"></path>
          {/if}
        </svg>
      </button>
    </div>
    
    <!-- Mobile Navigation -->
    {#if isMenuOpen}
      <div class="md:hidden border-t">
        <div class="container mx-auto px-4 py-4 flex flex-col space-y-4">
          <a href="/" class="text-foreground hover:text-primary transition-colors py-2">Home</a>
          <a href="/tasks" class="text-foreground hover:text-primary transition-colors py-2">Tasks</a>
          {#if isAuthenticated}
            <a href="/dashboard" class="text-foreground hover:text-primary transition-colors py-2">Dashboard</a>
          {/if}
          
          <!-- Wallet Connection -->
          {#if connected}
            <div class="flex flex-col space-y-2 py-2">
              <div class="bg-muted rounded-lg px-3 py-2 text-sm">
                <div class="font-medium">{solBalance.toFixed(2)} SOL</div>
                <div class="font-medium">{usdcBalance.toFixed(2)} USDC</div>
              </div>
              <button
                on:click={disconnectWallet}
                class="bg-destructive text-destructive-foreground rounded-lg px-3 py-2 text-sm hover:bg-destructive/90 transition-colors"
              >
                Disconnect
              </button>
            </div>
          {:else}
            <button
              on:click={connectWallet}
              class="bg-primary text-primary-foreground rounded-lg px-4 py-2 hover:bg-primary/90 transition-colors"
            >
              Connect Wallet
            </button>
          {/if}
        </div>
      </div>
    {/if}
  </header>
  
  <!-- Main Content -->
  <main class="flex-1 container mx-auto px-4 py-8">
    <slot />
  </main>
  
  <!-- Footer -->
  <footer class="bg-card shadow-sm border-t">
    <div class="container mx-auto px-4 py-6">
      <div class="flex flex-col md:flex-row justify-between items-center">
        <div class="mb-4 md:mb-0">
          <p class="text-muted-foreground">&copy; 2025 XAAM - Xpress AI Agent Marketplace</p>
        </div>
        <div class="flex space-x-4">
          <a href="/terms" class="text-muted-foreground hover:text-primary transition-colors">Terms</a>
          <a href="/privacy" class="text-muted-foreground hover:text-primary transition-colors">Privacy</a>
          <a href="/contact" class="text-muted-foreground hover:text-primary transition-colors">Contact</a>
        </div>
      </div>
    </div>
  </footer>
</div>