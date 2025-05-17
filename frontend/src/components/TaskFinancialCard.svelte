<script>
  import { createEventDispatcher } from 'svelte';
  
  // Props
  export let task;
  export let role = 'WORKER'; // 'WORKER' or 'JUDGE'
  export let financialOutcome = 0; // Positive for profit, negative for loss
  export let agentStatus = 'DISCONNECTED'; // 'CONNECTED' or 'DISCONNECTED' to MCP server
  export let agentActivity = 'IDLE'; // 'WORKING', 'BROWSING', or 'IDLE'
  
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
  
  // Format date
  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
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
  
  // Get agent status badge color
  function getAgentStatusColor(status) {
    switch (status) {
      case 'CONNECTED':
        return 'bg-green-100 text-green-800';
      case 'DISCONNECTED':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }
  
  // Get agent activity badge color
  function getAgentActivityColor(activity) {
    switch (activity) {
      case 'WORKING':
        return 'bg-yellow-100 text-yellow-800';
      case 'BROWSING':
        return 'bg-blue-100 text-blue-800';
      case 'IDLE':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }
  
  // Get financial outcome color
  function getFinancialColor(outcome) {
    if (outcome > 0) {
      return 'text-green-600';
    } else if (outcome < 0) {
      return 'text-red-600';
    } else {
      return 'text-gray-600';
    }
  }
  
  // Handle view task
  function handleViewTask() {
    dispatch('view', { taskId: task.id });
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
        <span class="text-muted-foreground">Role:</span>
        <span class="font-medium">{role}</span>
      </div>
      <div>
        <span class="text-muted-foreground">Completed:</span>
        <span class="font-medium">{formatDate(task.updated_at)}</span>
      </div>
      <div>
        <span class="text-muted-foreground">Reward:</span>
        <span class="font-medium">{task.reward_amount} {task.reward_currency}</span>
      </div>
      <div>
        <span class="text-muted-foreground">Deadline:</span>
        <span class="font-medium">{formatDeadline(task.deadline)}</span>
      </div>
    </div>
    
    <!-- Agent Status -->
    <div class="flex space-x-2 mb-4">
      <span class="text-xs rounded-full px-2 py-1 {getAgentStatusColor(agentStatus)}">
        MCP: {agentStatus}
      </span>
      <span class="text-xs rounded-full px-2 py-1 {getAgentActivityColor(agentActivity)}">
        {agentActivity}
      </span>
    </div>
    
    <!-- Financial Outcome -->
    <div class="mt-4 pt-4 border-t">
      <div class="flex justify-between items-center">
        <span class="text-sm text-muted-foreground">Financial Outcome:</span>
        <span class="text-lg font-bold {getFinancialColor(financialOutcome)}">
          {financialOutcome > 0 ? '+' : ''}{financialOutcome} {task.reward_currency}
        </span>
      </div>
    </div>
    
    <!-- Actions -->
    <div class="flex space-x-2 mt-4">
      <button 
        on:click={handleViewTask}
        class="flex-1 bg-secondary text-secondary-foreground rounded-md px-3 py-2 text-sm hover:bg-secondary/80 transition-colors"
      >
        View Details
      </button>
    </div>
  </div>
</div>