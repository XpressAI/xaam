<script>
  import { onMount, onDestroy } from 'svelte';
  import { walletStore } from '../stores/wallet';
  import { authStore } from '../stores/auth';
  import { routeStore } from '../stores/route';
  import { connectWallet, disconnectWallet, requestAirdrop } from '../utils/wallet';

  let connecting = false;
  let disconnecting = false;
  let requestingAirdrop = false;
  let error = '';
  let refreshInterval = 0;
  let connectionChecked = false;

  // Subscribe to wallet store
  $: connected = $walletStore?.connected || false;
  $: walletAddress = $walletStore?.wallet?.address || '';
  $: solBalance = $walletStore?.wallet?.sol_balance || 0;
  $: usdcBalance = $walletStore?.wallet?.usdc_balance || 0;

  // Format address for display
  $: displayAddress = walletAddress
    ? `${walletAddress.substring(0, 4)}...${walletAddress.substring(walletAddress.length - 4)}`
    : '';

  // Handle connect button click
  async function handleConnect() {
    try {
      console.log('WalletConnect: handleConnect called');
      connecting = true;
      error = '';
      
      // Check auth store state before connecting
      let authState = null;
      const unsubAuth = authStore.subscribe(state => {
        authState = state;
      });
      unsubAuth();
      console.log('WalletConnect: Auth state before connecting:', authState);
      
      await connectWallet();
      console.log('WalletConnect: Wallet connected successfully');
      
      // Set up auto-refresh of balances
      setupRefreshInterval();
      
      // Check auth store state after connecting
      const unsubAuth2 = authStore.subscribe(state => {
        authState = state;
      });
      unsubAuth2();
      console.log('WalletConnect: Auth state after connecting:', authState);
      
      // Call loginWithWallet on the auth store to ensure authentication state is updated
      console.log('WalletConnect: Attempting to login with wallet via auth store');
      try {
        await authStore.loginWithWallet();
        console.log('WalletConnect: Successfully logged in with wallet via auth store');
      } catch (authErr) {
        console.error('WalletConnect: Failed to login with wallet via auth store:', authErr);
      }
      
      // Check auth store state after login attempt
      const unsubAuth3 = authStore.subscribe(state => {
        authState = state;
      });
      unsubAuth3();
      console.log('WalletConnect: Auth state after login attempt:', authState);
      
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to connect wallet';
      console.error('Error connecting wallet:', err);
    } finally {
      connecting = false;
    }
  }

  // Handle disconnect button click
  async function handleDisconnect() {
    try {
      disconnecting = true;
      error = '';
      await disconnectWallet();
      
      // Clear refresh interval
      clearRefreshInterval();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to disconnect wallet';
      console.error('Error disconnecting wallet:', err);
    } finally {
      disconnecting = false;
    }
  }

  // Handle airdrop button click
  async function handleAirdrop() {
    try {
      requestingAirdrop = true;
      error = '';
      const signature = await requestAirdrop(1); // Request 1 SOL
      console.log('Airdrop transaction signature:', signature);
      
      // Refresh balances after airdrop
      await walletStore.refreshBalances();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to request airdrop';
      console.error('Error requesting airdrop:', err);
    } finally {
      requestingAirdrop = false;
    }
  }

  // Set up refresh interval for wallet balances
  function setupRefreshInterval() {
    if (!refreshInterval) {
      refreshInterval = window.setInterval(() => {
        if ($walletStore?.connected) {
          walletStore.refreshBalances();
        }
      }, 30000); // Refresh every 30 seconds
    }
  }

  // Clear refresh interval
  function clearRefreshInterval() {
    if (refreshInterval) {
      clearInterval(refreshInterval);
      refreshInterval = 0;
    }
  }

  // Check if Phantom wallet is installed
  let phantomInstalled = false;
  
  // Check for existing wallet connection
  async function checkExistingConnection() {
    try {
      console.log('Checking for existing wallet connection...');
      
      // First check if we have a persisted connection in the store
      const isConnected = await walletStore.checkConnection();
      
      if (isConnected) {
        console.log('Restored existing wallet connection from store');
        setupRefreshInterval();
      } else {
        // If no persisted connection, try auto-connecting via provider
        const provider = window?.phantom?.solana || window?.solana;
        if (provider?.isPhantom && provider?.isConnected) {
          console.log('Provider is connected, attempting to restore connection');
          await connectWallet();
          setupRefreshInterval();
        } else {
          // Check localStorage directly as a fallback
          const savedState = localStorage.getItem('walletState');
          if (savedState) {
            try {
              const parsedState = JSON.parse(savedState);
              console.log('Found wallet state in localStorage:', parsedState);
              
              if (parsedState.connected && parsedState.wallet) {
                console.log('Manually restoring wallet connection from localStorage');
                // Force update the wallet store with the saved state
                walletStore.updateWalletInfo(parsedState.wallet);
                setupRefreshInterval();
              }
            } catch (e) {
              console.error('Error parsing localStorage wallet state:', e);
            }
          }
        }
      }
    } catch (err) {
      console.error('Error checking existing connection:', err);
    } finally {
      connectionChecked = true;
    }
  }
  
  // Subscribe to route store to detect route changes
  const unsubscribeRoute = routeStore.subscribe(state => {
    // When route changes, check wallet connection
    console.log('WalletConnect detected route change to:', state.currentRoute);
    checkExistingConnection();
  });
  
  onMount(() => {
    // Check for Phantom wallet
    phantomInstalled = !!window?.phantom?.solana || !!window?.solana?.isPhantom;
    
    // Check for existing connection
    checkExistingConnection();
    
    return () => {
      // Clean up subscriptions
      unsubscribeRoute();
    };
  });
  
  onDestroy(() => {
    // Clear refresh interval when component is destroyed
    clearRefreshInterval();
  });
</script>

<div class="wallet-connect p-4 bg-white rounded-lg shadow-md">
  <h2 class="text-xl font-bold mb-4">Wallet</h2>
  
  {#if error}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
      <p>{error}</p>
    </div>
  {/if}
  
  {#if !phantomInstalled}
    <div class="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
      <p>Phantom wallet not detected. Please install the <a href="https://phantom.app/" target="_blank" rel="noopener noreferrer" class="underline">Phantom wallet extension</a> and refresh this page.</p>
    </div>
  {/if}
  
  {#if connected}
    <div class="mb-4">
      <div class="flex justify-between items-center mb-2">
        <span class="font-medium">Address:</span>
        <span class="font-mono">{displayAddress}</span>
      </div>
      <div class="flex justify-between items-center mb-2">
        <span class="font-medium">SOL Balance:</span>
        <span>{solBalance.toFixed(4)} SOL</span>
      </div>
      <div class="flex justify-between items-center">
        <span class="font-medium">USDC Balance:</span>
        <span>{usdcBalance.toFixed(2)} USDC</span>
      </div>
    </div>
    
    <div class="flex flex-col space-y-2">
      <button 
        on:click={handleDisconnect} 
        disabled={disconnecting}
        class="bg-red-500 hover:bg-red-600 text-white py-2 px-4 rounded disabled:opacity-50"
      >
        {disconnecting ? 'Disconnecting...' : 'Disconnect Wallet'}
      </button>
      
      <button
        on:click={handleAirdrop}
        disabled={requestingAirdrop || !connected}
        class="bg-purple-500 hover:bg-purple-600 text-white py-2 px-4 rounded disabled:opacity-50"
      >
        {requestingAirdrop ? 'Requesting...' : 'Request SOL Airdrop (Devnet)'}
      </button>
      
      <button
        on:click={() => walletStore.refreshBalances()}
        disabled={!connected}
        class="bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded disabled:opacity-50"
      >
        Refresh Balance
      </button>
    </div>
  {:else}
    <button 
      on:click={handleConnect} 
      disabled={connecting || !phantomInstalled}
      class="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded disabled:opacity-50"
    >
      {connecting ? 'Connecting...' : 'Connect Wallet'}
    </button>
  {/if}
</div>