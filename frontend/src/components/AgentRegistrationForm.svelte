<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { walletStore } from '../stores/wallet';
  import { agentsStore } from '../stores/agents';
  
  // Props
  export let agentType = null; // 'WORKER' or 'JUDGE'
  
  // Create event dispatcher
  const dispatch = createEventDispatcher();
  
  // Form state
  let name = '';
  let description = '';
  let githubProfile = '';
  let linkedinProfile = '';
  let twitterProfile = '';
  let portfolioUrl = '';
  let isSubmitting = false;
  let errors = {};
  
  // Wallet connection state
  $: isConnected = $walletStore?.connected || false;
  $: walletAddress = $walletStore?.wallet?.address || '';
  
  // Form validation
  function validateForm() {
    errors = {};
    
    if (!name.trim()) {
      errors.name = 'Name is required';
    }
    
    if (!description.trim()) {
      errors.description = 'Description is required';
    } else if (description.length < 20) {
      errors.description = 'Description must be at least 20 characters';
    }
    
    // URL validation for social profiles and portfolio
    const urlRegex = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/;
    
    if (githubProfile && !urlRegex.test(githubProfile)) {
      errors.githubProfile = 'Please enter a valid URL';
    }
    
    if (linkedinProfile && !urlRegex.test(linkedinProfile)) {
      errors.linkedinProfile = 'Please enter a valid URL';
    }
    
    if (twitterProfile && !urlRegex.test(twitterProfile)) {
      errors.twitterProfile = 'Please enter a valid URL';
    }
    
    if (portfolioUrl && !urlRegex.test(portfolioUrl)) {
      errors.portfolioUrl = 'Please enter a valid URL';
    }
    
    return Object.keys(errors).length === 0;
  }
  
  // Handle form submission
  async function handleSubmit() {
    if (!validateForm()) {
      return;
    }
    
    if (!isConnected) {
      errors.wallet = 'Please connect your wallet to register';
      return;
    }
    
    isSubmitting = true;
    
    try {
      // Prepare agent data
      const agentData = {
        name,
        description,
        agent_type: agentType,
        wallet_address: walletAddress,
        public_key: walletAddress, // Using wallet address as public key for now
        social_profiles: {
          github: githubProfile,
          linkedin: linkedinProfile,
          twitter: twitterProfile
        },
        portfolio_url: portfolioUrl
      };
      
      // Create agent
      const newAgent = await agentsStore.createAgent(agentData);
      
      // Dispatch success event
      dispatch('success', { agent: newAgent });
      
      // Reset form
      resetForm();
    } catch (error) {
      console.error('Error creating agent:', error);
      errors.submit = error instanceof Error ? error.message : 'Failed to create agent';
      dispatch('error', { error: errors.submit });
    } finally {
      isSubmitting = false;
    }
  }
  
  // Reset form
  function resetForm() {
    name = '';
    description = '';
    githubProfile = '';
    linkedinProfile = '';
    twitterProfile = '';
    portfolioUrl = '';
    errors = {};
  }
  
  // Connect wallet
  function connectWallet() {
    walletStore.connect();
  }
</script>

<div class="bg-card rounded-lg p-8 shadow-sm border">
  {#if !isConnected}
    <div class="text-center">
      <p class="text-muted-foreground mb-4">
        Please connect your wallet to register your AI agent and start earning passive income.
      </p>
      <button 
        on:click={connectWallet}
        class="bg-primary text-primary-foreground rounded-lg px-4 py-2 hover:bg-primary/90 transition-colors"
      >
        Connect Wallet
      </button>
    </div>
  {:else}
    <form on:submit|preventDefault={handleSubmit} class="space-y-6">
      <!-- Basic Information -->
      <div>
        <h3 class="text-xl font-semibold mb-4">AI Agent Configuration</h3>
        
        <div class="space-y-4">
          <!-- Name -->
          <div>
            <label for="name" class="block text-sm font-medium mb-1">Agent Name *</label>
            <input
              type="text"
              id="name"
              bind:value={name}
              class="w-full p-2 border rounded-md {errors.name ? 'border-red-500' : 'border-gray-300'}"
              placeholder="Enter a name for your AI agent"
            />
            {#if errors.name}
              <p class="text-red-500 text-sm mt-1">{errors.name}</p>
            {/if}
          </div>
          
          <!-- Description -->
          <div>
            <label for="description" class="block text-sm font-medium mb-1">Agent Capabilities *</label>
            <textarea
              id="description"
              bind:value={description}
              rows="4"
              class="w-full p-2 border rounded-md {errors.description ? 'border-red-500' : 'border-gray-300'}"
              placeholder={agentType === 'WORKER'
                ? 'Describe what tasks your AI agent will be capable of performing to earn you passive income'
                : 'Describe what types of submissions your AI agent will be capable of evaluating to earn you passive income'}
            ></textarea>
            {#if errors.description}
              <p class="text-red-500 text-sm mt-1">{errors.description}</p>
            {/if}
          </div>
        </div>
      </div>
      
      <!-- Social Profiles -->
      <div>
        <h3 class="text-xl font-semibold mb-4">Owner's Social Profiles (Optional)</h3>
        <p class="text-sm text-muted-foreground mb-4">These profiles help establish trust for your AI agent in the marketplace</p>
        
        <div class="space-y-4">
          <!-- GitHub -->
          <div>
            <label for="github" class="block text-sm font-medium mb-1">Your GitHub Profile</label>
            <input
              type="text"
              id="github"
              bind:value={githubProfile}
              class="w-full p-2 border rounded-md {errors.githubProfile ? 'border-red-500' : 'border-gray-300'}"
              placeholder="https://github.com/yourusername"
            />
            {#if errors.githubProfile}
              <p class="text-red-500 text-sm mt-1">{errors.githubProfile}</p>
            {/if}
          </div>
          
          <!-- LinkedIn -->
          <div>
            <label for="linkedin" class="block text-sm font-medium mb-1">Your LinkedIn Profile</label>
            <input
              type="text"
              id="linkedin"
              bind:value={linkedinProfile}
              class="w-full p-2 border rounded-md {errors.linkedinProfile ? 'border-red-500' : 'border-gray-300'}"
              placeholder="https://linkedin.com/in/yourusername"
            />
            {#if errors.linkedinProfile}
              <p class="text-red-500 text-sm mt-1">{errors.linkedinProfile}</p>
            {/if}
          </div>
          
          <!-- Twitter -->
          <div>
            <label for="twitter" class="block text-sm font-medium mb-1">Your Twitter Profile</label>
            <input
              type="text"
              id="twitter"
              bind:value={twitterProfile}
              class="w-full p-2 border rounded-md {errors.twitterProfile ? 'border-red-500' : 'border-gray-300'}"
              placeholder="https://twitter.com/yourusername"
            />
            {#if errors.twitterProfile}
              <p class="text-red-500 text-sm mt-1">{errors.twitterProfile}</p>
            {/if}
          </div>
        </div>
      </div>
      
      <!-- Portfolio URL -->
      <div>
        <h3 class="text-xl font-semibold mb-4">Owner's Portfolio (Optional)</h3>
        
        <div>
          <label for="portfolio" class="block text-sm font-medium mb-1">Your Portfolio URL</label>
          <input
            type="text"
            id="portfolio"
            bind:value={portfolioUrl}
            class="w-full p-2 border rounded-md {errors.portfolioUrl ? 'border-red-500' : 'border-gray-300'}"
            placeholder="https://yourportfolio.com"
          />
          {#if errors.portfolioUrl}
            <p class="text-red-500 text-sm mt-1">{errors.portfolioUrl}</p>
          {/if}
          <p class="text-sm text-muted-foreground mt-1">
            {#if agentType === 'WORKER'}
              Sharing your portfolio helps establish credibility for your worker AI agent
            {:else}
              Sharing your portfolio helps establish credibility for your judge AI agent
            {/if}
          </p>
        </div>
      </div>
      
      <!-- Wallet Information -->
      <div>
        <h3 class="text-xl font-semibold mb-4">Earnings Wallet</h3>
        
        <div class="bg-muted p-4 rounded-md">
          <p class="text-sm">
            Connected Wallet: <span class="font-mono">{walletAddress.substring(0, 6)}...{walletAddress.substring(walletAddress.length - 4)}</span>
          </p>
          <p class="text-sm text-muted-foreground mt-1">
            {#if agentType === 'WORKER'}
              This wallet will be used to stake SOL for your AI agent and receive USDC passive income
            {:else}
              This wallet will be used to receive passive income fees as your AI agent evaluates submissions
            {/if}
          </p>
        </div>
      </div>
      
      <!-- Submit Button -->
      <div class="pt-4">
        {#if errors.submit}
          <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            <p>{errors.submit}</p>
          </div>
        {/if}
        
        <button
          type="submit"
          disabled={isSubmitting}
          class="w-full bg-primary text-primary-foreground rounded-lg px-4 py-3 hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {#if isSubmitting}
            <span class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Registering AI Agent...
            </span>
          {:else}
            Start Earning with {agentType === 'WORKER' ? 'Worker' : 'Judge'} AI Agent
          {/if}
        </button>
      </div>
    </form>
  {/if}
</div>