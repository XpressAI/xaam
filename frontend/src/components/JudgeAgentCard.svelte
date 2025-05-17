<script>
  import { createEventDispatcher } from 'svelte';
  
  // Props
  export let agent;
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // Format date
  function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }
</script>

<div class="bg-card rounded-lg shadow-sm border overflow-hidden hover:shadow-md transition-shadow">
  <div class="p-6 border-b">
    <div class="flex justify-between items-start">
      <div>
        <h3 class="text-xl font-semibold">{agent.name}</h3>
        <p class="text-sm text-muted-foreground mt-1">Created: {formatDate(agent.created_at)}</p>
      </div>
      <div class="bg-primary/10 text-primary text-xs font-medium px-2.5 py-0.5 rounded">
        Judge Agent
      </div>
    </div>
  </div>
  
  <div class="p-6">
    <p class="text-sm text-muted-foreground mb-4">{agent.description}</p>
    
    <div class="grid grid-cols-2 gap-4 mb-4">
      <div>
        <p class="text-xs text-muted-foreground">Specialization</p>
        <p class="text-sm font-medium">{agent.specialization || 'General'}</p>
      </div>
      <div>
        <p class="text-xs text-muted-foreground">Reputation Score</p>
        <p class="text-sm font-medium">{agent.reputation_score.toFixed(2)}</p>
      </div>
    </div>
    
    <div class="grid grid-cols-2 gap-4">
      <div>
        <p class="text-xs text-muted-foreground">Completed Tasks</p>
        <p class="text-sm font-medium">{agent.completed_tasks}</p>
      </div>
      <div>
        <p class="text-xs text-muted-foreground">Successful Tasks</p>
        <p class="text-sm font-medium">{agent.successful_tasks}</p>
      </div>
    </div>
  </div>
  
  <div class="p-4 bg-muted/30 border-t">
    <button 
      class="w-full py-2 px-4 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
      on:click={() => dispatch('viewCredentials', agent)}
    >
      View Credentials
    </button>
  </div>
</div>