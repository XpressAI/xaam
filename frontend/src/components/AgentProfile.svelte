<script>
  import { agentsStore } from '../stores/agents';
  
  // Props
  export let agent;
  export let isCurrentUser = false;
  
  // Format date
  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
  
  // Calculate success rate
  function calculateSuccessRate() {
    if (agent.completed_tasks === 0) {
      return '0%';
    }
    
    const rate = (agent.successful_tasks / agent.completed_tasks) * 100;
    return `${rate.toFixed(0)}%`;
  }
  
  // Get agent type badge color
  function getAgentTypeColor(type) {
    switch (type) {
      case 'WORKER':
        return 'bg-blue-100 text-blue-800';
      case 'JUDGE':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }
</script>

<div class="bg-card rounded-lg shadow-sm border overflow-hidden">
  <!-- Header -->
  <div class="p-6 border-b">
    <div class="flex justify-between items-start">
      <h2 class="text-2xl font-semibold">{agent.name}</h2>
      <span class="text-sm rounded-full px-3 py-1 {getAgentTypeColor(agent.agent_type)}">
        {agent.agent_type}
      </span>
    </div>
    {#if isCurrentUser}
      <div class="mt-2 text-sm text-muted-foreground">This is your profile</div>
    {/if}
  </div>
  
  <!-- Content -->
  <div class="p-6">
    <!-- Description -->
    <div class="mb-6">
      <h3 class="text-lg font-medium mb-2">About</h3>
      <p class="text-muted-foreground">{agent.description}</p>
    </div>
    
    <!-- Stats -->
    <div class="mb-6">
      <h3 class="text-lg font-medium mb-3">Performance</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-muted/30 p-4 rounded-md">
          <div class="text-3xl font-bold">{agent.reputation_score.toFixed(1)}</div>
          <div class="text-sm text-muted-foreground">Reputation Score</div>
        </div>
        <div class="bg-muted/30 p-4 rounded-md">
          <div class="text-3xl font-bold">{agent.completed_tasks}</div>
          <div class="text-sm text-muted-foreground">Completed Tasks</div>
        </div>
        <div class="bg-muted/30 p-4 rounded-md">
          <div class="text-3xl font-bold">{calculateSuccessRate()}</div>
          <div class="text-sm text-muted-foreground">Success Rate</div>
        </div>
      </div>
    </div>
    
    <!-- Details -->
    <div class="mb-6">
      <h3 class="text-lg font-medium mb-3">Details</h3>
      <div class="space-y-3">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
          <div class="text-sm text-muted-foreground">Wallet Address:</div>
          <div class="text-sm font-mono break-all">{agent.wallet_address}</div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
          <div class="text-sm text-muted-foreground">Public Key:</div>
          <div class="text-sm font-mono break-all">{agent.public_key}</div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
          <div class="text-sm text-muted-foreground">Joined:</div>
          <div class="text-sm">{formatDate(agent.created_at)}</div>
        </div>
      </div>
    </div>
    
    <!-- Actions (only for current user) -->
    {#if isCurrentUser}
      <div class="flex justify-end">
        <button class="bg-secondary text-secondary-foreground rounded-md px-4 py-2 hover:bg-secondary/80 transition-colors">
          Edit Profile
        </button>
      </div>
    {/if}
  </div>
</div>