<script>
  import { createEventDispatcher } from 'svelte';
  
  // Props
  export let task;
  export let showActions = true;
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // Format deadline
  function formatDeadline(dateString) {
    const deadline = new Date(dateString);
    const now = new Date();
    
    // Calculate days remaining
    const diffTime = deadline.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) {
      return 'Expired';
    } else if (diffDays === 0) {
      return 'Today';
    } else if (diffDays === 1) {
      return 'Tomorrow';
    } else {
      return `${diffDays} days`;
    }
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
  
  // Handle view task
  function handleViewTask() {
    dispatch('view', { taskId: task.id });
  }
  
  // Handle stake on task
  function handleStakeTask() {
    dispatch('stake', { taskId: task.id });
  }
</script>

<div class="bg-card rounded-lg shadow-sm border overflow-hidden hover:shadow-md transition-shadow">
  <div class="p-5">
    <!-- Header -->
    <div class="flex justify-between items-start mb-3">
      <h3 class="text-lg font-semibold line-clamp-1">{task.title}</h3>
      <span class="text-xs rounded-full px-2 py-1 {getStatusColor(task.status)}">
        {task.status}
      </span>
    </div>
    
    <!-- Summary -->
    <p class="text-muted-foreground text-sm mb-4 line-clamp-2">{task.summary}</p>
    
    <!-- Details -->
    <div class="grid grid-cols-2 gap-2 text-sm mb-4">
      <div>
        <span class="text-muted-foreground">Reward:</span>
        <span class="font-medium">{task.reward_amount} {task.reward_currency}</span>
      </div>
      <div>
        <span class="text-muted-foreground">Deadline:</span>
        <span class="font-medium">{formatDeadline(task.deadline)}</span>
      </div>
    </div>
    
    <!-- Actions -->
    {#if showActions}
      <div class="flex space-x-2 mt-4">
        <button 
          on:click={handleViewTask}
          class="flex-1 bg-secondary text-secondary-foreground rounded-md px-3 py-2 text-sm hover:bg-secondary/80 transition-colors"
        >
          View Details
        </button>
        
        {#if task.status === 'CREATED'}
          <button 
            on:click={handleStakeTask}
            class="flex-1 bg-primary text-primary-foreground rounded-md px-3 py-2 text-sm hover:bg-primary/90 transition-colors"
          >
            Stake & Access
          </button>
        {/if}
      </div>
    {/if}
  </div>
</div>