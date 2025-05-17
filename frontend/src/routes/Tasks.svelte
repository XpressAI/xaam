<script>
  import { onMount } from 'svelte';
  import { tasksStore, filteredTasks } from '../stores/tasks';
  import { authStore } from '../stores/auth';
  import TaskCard from '../components/TaskCard.svelte';
  
  // State
  let isLoading = true;
  let isAuthenticated = false;
  let searchTerm = '';
  let selectedStatus = null;
  let sortBy = 'deadline';
  let sortDirection = 'asc';
  
  // Status options
  const statusOptions = [
    { value: null, label: 'All Statuses' },
    { value: 'CREATED', label: 'Created' },
    { value: 'STAKED', label: 'Staked' },
    { value: 'IN_PROGRESS', label: 'In Progress' },
    { value: 'SUBMITTED', label: 'Submitted' },
    { value: 'JUDGED', label: 'Judged' },
    { value: 'COMPLETED', label: 'Completed' }
  ];
  
  // Sort options
  const sortOptions = [
    { value: 'deadline', label: 'Deadline' },
    { value: 'reward_amount', label: 'Reward Amount' },
    { value: 'created_at', label: 'Created Date' }
  ];
  
  // Subscribe to auth store
  authStore.subscribe(state => {
    isAuthenticated = state.isAuthenticated;
  });
  
  // Load tasks
  onMount(() => {
    loadTasks();
    return () => {};
  });
  
  async function loadTasks() {
    isLoading = true;
    try {
      await tasksStore.fetchTasks();
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      isLoading = false;
    }
  }
  
  // Handle search
  function handleSearch() {
    tasksStore.updateFilters({ search: searchTerm });
  }
  
  // Handle status change
  function handleStatusChange(event) {
    const target = event.target;
    selectedStatus = target.value === 'null' ? null : target.value;
    tasksStore.updateFilters({ status: selectedStatus });
  }
  
  // Handle sort change
  function handleSortChange(event) {
    const target = event.target;
    const value = target.value;
    
    // Only update if it's one of the valid values
    if (value === 'deadline' || value === 'reward_amount' || value === 'created_at') {
      sortBy = value;
      tasksStore.updateFilters({
        sortBy: value
      });
    }
  }
  
  // Toggle sort direction
  function toggleSortDirection() {
    const newDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    sortDirection = newDirection;
    tasksStore.updateFilters({
      sortDirection: newDirection
    });
  }
  
  // Reset filters
  function resetFilters() {
    searchTerm = '';
    selectedStatus = null;
    sortBy = 'deadline';
    sortDirection = 'asc';
    tasksStore.resetFilters();
  }
  
  // Navigate to task detail
  function handleViewTask(event) {
    window.location.href = `/tasks/${event.detail.taskId}`;
  }
  
  // Navigate to task creation
  function createTask() {
    window.location.href = '/tasks/create';
  }
  
  // Handle stake on task
  function handleStakeTask(event) {
    window.location.href = `/tasks/${event.detail.taskId}`;
  }
</script>

  <div class="max-w-6xl mx-auto">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
      <h1 class="text-3xl font-bold mb-4 md:mb-0">Task Marketplace</h1>
      
      {#if isAuthenticated}
        <button 
          on:click={createTask}
          class="bg-primary text-primary-foreground rounded-lg px-4 py-2 hover:bg-primary/90 transition-colors"
        >
          Create New Task
        </button>
      {/if}
    </div>
    
    <!-- Filters -->
    <div class="bg-card rounded-lg shadow-sm border p-4 mb-8">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Search -->
        <div class="col-span-1 md:col-span-2">
          <div class="relative">
            <input
              type="text"
              placeholder="Search tasks..."
              bind:value={searchTerm}
              on:input={handleSearch}
              class="w-full px-3 py-2 border rounded-md bg-background pr-10"
            />
            <button 
              class="absolute right-2 top-1/2 transform -translate-y-1/2 text-muted-foreground"
              aria-label="Search"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <path d="M21 21l-4.35-4.35"></path>
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Status Filter -->
        <div>
          <select
            value={selectedStatus === null ? 'null' : selectedStatus}
            on:change={handleStatusChange}
            class="w-full px-3 py-2 border rounded-md bg-background"
          >
            {#each statusOptions as option}
              <option value={option.value === null ? 'null' : option.value}>
                {option.label}
              </option>
            {/each}
          </select>
        </div>
        
        <!-- Sort -->
        <div class="flex space-x-2">
          <select
            bind:value={sortBy}
            on:change={handleSortChange}
            class="flex-1 px-3 py-2 border rounded-md bg-background"
          >
            {#each sortOptions as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
          
          <button 
            on:click={toggleSortDirection}
            class="px-3 py-2 border rounded-md bg-background text-muted-foreground"
            aria-label={sortDirection === 'asc' ? 'Sort ascending' : 'Sort descending'}
          >
            {#if sortDirection === 'asc'}
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 20V4M5 11l7-7 7 7M5 20h14"></path>
              </svg>
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 4v16M5 13l7 7 7-7M5 4h14"></path>
              </svg>
            {/if}
          </button>
        </div>
      </div>
      
      <!-- Reset Filters -->
      <div class="mt-4 flex justify-end">
        <button 
          on:click={resetFilters}
          class="text-sm text-muted-foreground hover:text-foreground"
        >
          Reset Filters
        </button>
      </div>
    </div>
    
    <!-- Tasks Grid -->
    {#if isLoading}
      <div class="flex justify-center items-center h-64">
        <div class="text-xl text-muted-foreground">Loading tasks...</div>
      </div>
    {:else}
      {#if $filteredTasks.length > 0}
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          {#each $filteredTasks as task}
            <TaskCard 
              task={task} 
              on:view={handleViewTask}
              on:stake={handleStakeTask}
            />
          {/each}
        </div>
      {:else}
        <div class="bg-card p-8 rounded-lg text-center">
          <p class="text-muted-foreground mb-4">No tasks found matching your filters.</p>
          <button 
            on:click={resetFilters}
            class="bg-secondary text-secondary-foreground rounded-lg px-4 py-2 hover:bg-secondary/80 transition-colors"
          >
            Reset Filters
          </button>
        </div>
      {/if}
    {/if}
  </div>