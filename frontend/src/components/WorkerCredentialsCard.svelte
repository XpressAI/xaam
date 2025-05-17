<script>
  import { createEventDispatcher } from 'svelte';
  
  // Props
  export let agent;
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // State
  let walletAddressCopied = false;
  let publicKeyCopied = false;
  
  // Copy to clipboard function
  async function copyToClipboard(text, field) {
    try {
      await navigator.clipboard.writeText(text);
      
      if (field === 'wallet') {
        walletAddressCopied = true;
        setTimeout(() => walletAddressCopied = false, 2000);
      } else if (field === 'publicKey') {
        publicKeyCopied = true;
        setTimeout(() => publicKeyCopied = false, 2000);
      }
    } catch (err) {
      console.error('Failed to copy: ', err);
    }
  }
</script>

<div class="bg-card rounded-lg shadow-sm border overflow-hidden">
  <div class="p-6 border-b">
    <div class="flex justify-between items-center">
      <h3 class="text-xl font-semibold">Authentication Credentials</h3>
      <button 
        class="text-sm text-muted-foreground hover:text-foreground"
        on:click={() => dispatch('close')}
      >
        Close
      </button>
    </div>
    <p class="text-sm text-muted-foreground mt-2">
      These credentials are required to authenticate your worker agent with the MCP server.
    </p>
  </div>
  
  <div class="p-6">
    <div class="mb-6">
      <h4 class="text-base font-medium mb-2">Wallet Address</h4>
      <div class="flex items-center">
        <div class="bg-muted p-3 rounded-md text-sm font-mono flex-1 overflow-x-auto whitespace-nowrap">
          {agent.wallet_address}
        </div>
        <button 
          class="ml-2 p-2 text-muted-foreground hover:text-foreground"
          on:click={() => copyToClipboard(agent.wallet_address, 'wallet')}
        >
          {#if walletAddressCopied}
            <span class="text-green-500">✓ Copied</span>
          {:else}
            <span>Copy</span>
          {/if}
        </button>
      </div>
    </div>
    
    <div class="mb-6">
      <h4 class="text-base font-medium mb-2">Public Key</h4>
      <div class="flex items-center">
        <div class="bg-muted p-3 rounded-md text-sm font-mono flex-1 overflow-x-auto whitespace-nowrap">
          {agent.public_key}
        </div>
        <button 
          class="ml-2 p-2 text-muted-foreground hover:text-foreground"
          on:click={() => copyToClipboard(agent.public_key, 'publicKey')}
        >
          {#if publicKeyCopied}
            <span class="text-green-500">✓ Copied</span>
          {:else}
            <span>Copy</span>
          {/if}
        </button>
      </div>
    </div>
    
    <div class="bg-muted/30 p-4 rounded-md">
      <h4 class="text-base font-medium mb-2">How to Use These Credentials</h4>
      <ol class="list-decimal pl-5 space-y-2 text-sm">
        <li>Configure your worker agent with these credentials to authenticate with the MCP server.</li>
        <li>Use the wallet address to identify your agent in the XAAM ecosystem.</li>
        <li>The public key is used for verifying your agent's identity and encrypting communications.</li>
        <li>Keep your private key secure and never share it with anyone.</li>
        <li>For detailed setup instructions, refer to the <a href="/docs/worker-agent" class="text-primary hover:underline">Worker Agent Documentation</a>.</li>
      </ol>
    </div>
  </div>
</div>