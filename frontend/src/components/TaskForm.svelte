<script>
  import { createEventDispatcher } from 'svelte';
  // Import only what we need
  import { agentsStore } from '../stores/agents';
  import { encryptTaskPayload } from '../utils/encryption';
  
  // Define a simple judge structure to match what we need
  // This avoids TypeScript import issues
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // Form data
  let title = '';
  let summary = '';
  let taskPayload = '';
  let deadline = '';
  let rewardAmount = 0;
  let rewardCurrency = 'USDC';
  let selectedJudges = [];
  let isEncrypting = false;
  let encryptionError = '';
  
  // Form validation
  let errors = {
    title: '',
    summary: '',
    taskPayload: '',
    deadline: '',
    rewardAmount: '',
    judges: ''
  };
  
  // Judges list
  let judges = [];
  
  // In a real app, we would load judges from the API
  // This would be called in onMount
  
  // Initialize with mock judges if needed
  if (judges.length === 0) {
    judges = [
      {
        id: 'judge-1',
        name: 'Expert Judge 1',
        description: 'AI expert with focus on NLP',
        agent_type: 'JUDGE',
        wallet_address: '8xDxjYGQbx4VV9VEpzrZBxJwNWVE9JPNpHxX6rzrn5r3',
        public_key: '8xDxjYGQbx4VV9VEpzrZBxJwNWVE9JPNpHxX6rzrn5r3',
        reputation_score: 4.8,
        completed_tasks: 24,
        successful_tasks: 22,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 'judge-2',
        name: 'Expert Judge 2',
        description: 'Computer vision specialist',
        agent_type: 'JUDGE',
        wallet_address: '7xCxjYGQbx4VV9VEpzrZBxJwNWVE9JPNpHxX6rzrn5r2',
        public_key: '7xCxjYGQbx4VV9VEpzrZBxJwNWVE9JPNpHxX6rzrn5r2',
        reputation_score: 4.6,
        completed_tasks: 18,
        successful_tasks: 16,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    ];
  }
  
  // Set minimum deadline to tomorrow
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const minDeadline = tomorrow.toISOString().split('T')[0];
  
  // Handle form submission
  async function handleSubmit() {
    // Reset errors
    errors = {
      title: '',
      summary: '',
      taskPayload: '',
      deadline: '',
      rewardAmount: '',
      judges: ''
    };
    
    encryptionError = '';
    
    // Validate form
    let isValid = true;
    
    if (!title.trim()) {
      errors.title = 'Title is required';
      isValid = false;
    }
    
    if (!summary.trim()) {
      errors.summary = 'Summary is required';
      isValid = false;
    }
    
    if (!taskPayload.trim()) {
      errors.taskPayload = 'Task payload is required';
      isValid = false;
    } else {
      // Validate that the payload is valid JSON
      try {
        JSON.parse(taskPayload);
      } catch (e) {
        errors.taskPayload = 'Task payload must be valid JSON';
        isValid = false;
      }
    }
    
    if (!deadline) {
      errors.deadline = 'Deadline is required';
      isValid = false;
    }
    
    if (rewardAmount <= 0) {
      errors.rewardAmount = 'Reward amount must be greater than 0';
      isValid = false;
    }
    
    if (selectedJudges.length === 0) {
      errors.judges = 'At least one judge must be selected';
      isValid = false;
    }
    
    if (isValid) {
      try {
        isEncrypting = true;
        
        // Get the payload as a JSON object
        const payload = JSON.parse(taskPayload);
        
        // Get the public keys for the selected judges
        // Initialize as an object with string keys and string values
        const judgePublicKeys = Object.create(null);
        selectedJudges.forEach(judgeId => {
          const judge = judges.find(j => j.id === judgeId);
          if (judge) {
            judgePublicKeys[judgeId] = judge.public_key;
          }
        });
        
        // Encrypt the payload
        const encryptionResult = encryptTaskPayload(payload, judgePublicKeys);
        
        // In a real implementation, we would upload the encrypted payload to IPFS or S3
        // For now, we'll just use the encrypted payload directly
        
        // Get the first judge's key if available
        const firstJudgeKey = Object.values(encryptionResult.encryptedKeys)[0] || undefined;
        
        dispatch('submit', {
          title,
          summary,
          encrypted_payload_url: encryptionResult.encryptedPayload,
          ...(firstJudgeKey && { encryption_key: firstJudgeKey }), // Only include if defined
          deadline: new Date(deadline).toISOString(),
          reward_amount: rewardAmount,
          reward_currency: rewardCurrency,
          judges: selectedJudges,
          payload: payload // Include the original payload for reference
        });
      } catch (error) {
        console.error('Encryption error:', error);
        encryptionError = `Error encrypting payload: ${error.message || 'Unknown error'}`;
      } finally {
        isEncrypting = false;
      }
    }
  }
  
  // Handle cancel
  function handleCancel() {
    dispatch('cancel');
  }
  
  // Handle judge selection
  function toggleJudge(judgeId) {
    if (selectedJudges.includes(judgeId)) {
      selectedJudges = selectedJudges.filter(id => id !== judgeId);
    } else {
      selectedJudges = [...selectedJudges, judgeId];
    }
  }
</script>

<div class="bg-card rounded-lg shadow-sm border p-6">
  <h2 class="text-2xl font-semibold mb-6">Create New Task</h2>
  
  <form on:submit|preventDefault={handleSubmit} class="space-y-6">
    <!-- Title -->
    <div class="space-y-2">
      <label for="title" class="text-sm font-medium">Title</label>
      <input
        id="title"
        type="text"
        bind:value={title}
        class="w-full px-3 py-2 border rounded-md bg-background"
        placeholder="Enter task title"
      />
      {#if errors.title}
        <p class="text-destructive text-sm">{errors.title}</p>
      {/if}
    </div>
    
    <!-- Summary -->
    <div class="space-y-2">
      <label for="summary" class="text-sm font-medium">Summary</label>
      <textarea
        id="summary"
        bind:value={summary}
        class="w-full px-3 py-2 border rounded-md bg-background min-h-[100px]"
        placeholder="Enter task summary"
      ></textarea>
      {#if errors.summary}
        <p class="text-destructive text-sm">{errors.summary}</p>
      {/if}
    </div>
    
    <!-- Task Payload -->
    <div class="space-y-2">
      <label for="taskPayload" class="text-sm font-medium">Task Payload (JSON)</label>
      <textarea
        id="taskPayload"
        bind:value={taskPayload}
        class="w-full px-3 py-2 border rounded-md bg-background min-h-[150px] font-mono text-sm"
        placeholder={`{"description": "Detailed task description", "requirements": ["req1", "req2"], "data": {"key": "value"}}`}
      ></textarea>
      {#if errors.taskPayload}
        <p class="text-destructive text-sm">{errors.taskPayload}</p>
      {/if}
      <p class="text-muted-foreground text-xs">
        Enter your task details as JSON. This will be encrypted with the judges' public keys.
        Only judges will be able to decrypt this content.
      </p>
    </div>
    
    <!-- Deadline -->
    <div class="space-y-2">
      <label for="deadline" class="text-sm font-medium">Deadline</label>
      <input
        id="deadline"
        type="date"
        bind:value={deadline}
        min={minDeadline}
        class="w-full px-3 py-2 border rounded-md bg-background"
      />
      {#if errors.deadline}
        <p class="text-destructive text-sm">{errors.deadline}</p>
      {/if}
    </div>
    
    <!-- Reward -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="space-y-2">
        <label for="rewardAmount" class="text-sm font-medium">Reward Amount</label>
        <input
          id="rewardAmount"
          type="number"
          bind:value={rewardAmount}
          min="0"
          step="0.01"
          class="w-full px-3 py-2 border rounded-md bg-background"
        />
        {#if errors.rewardAmount}
          <p class="text-destructive text-sm">{errors.rewardAmount}</p>
        {/if}
      </div>
      
      <div class="space-y-2">
        <label for="rewardCurrency" class="text-sm font-medium">Currency</label>
        <select
          id="rewardCurrency"
          bind:value={rewardCurrency}
          class="w-full px-3 py-2 border rounded-md bg-background"
        >
          <option value="USDC">USDC</option>
          <option value="SOL">SOL</option>
        </select>
      </div>
    </div>
    
    <!-- Judges -->
    <div class="space-y-2">
      <label class="text-sm font-medium">Select Judges</label>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        {#each judges as judge}
          <div 
            class="border rounded-md p-3 cursor-pointer {selectedJudges.includes(judge.id) ? 'border-primary bg-primary/5' : ''}"
            on:click={() => toggleJudge(judge.id)}
          >
            <div class="flex items-center space-x-2">
              <input 
                type="checkbox" 
                checked={selectedJudges.includes(judge.id)} 
                class="h-4 w-4 text-primary"
              />
              <div>
                <p class="font-medium">{judge.name}</p>
                <p class="text-sm text-muted-foreground">{judge.description}</p>
                <div class="flex items-center mt-1">
                  <span class="text-xs bg-muted px-2 py-0.5 rounded-full">
                    Rating: {judge.reputation_score.toFixed(1)}
                  </span>
                  <span class="text-xs ml-2">
                    {judge.completed_tasks} tasks completed
                  </span>
                </div>
              </div>
            </div>
          </div>
        {/each}
      </div>
      {#if errors.judges}
        <p class="text-destructive text-sm">{errors.judges}</p>
      {/if}
    </div>
    
    {#if encryptionError}
      <div class="mt-4 p-4 bg-destructive/10 border border-destructive rounded-md">
        <p class="text-destructive">{encryptionError}</p>
      </div>
    {/if}
    
    <!-- Actions -->
    <div class="flex justify-end space-x-3 pt-4">
      <button
        type="button"
        on:click={handleCancel}
        class="px-4 py-2 border rounded-md hover:bg-muted transition-colors"
      >
        Cancel
      </button>
      <button
        type="submit"
        class="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
        disabled={isEncrypting}
      >
        {#if isEncrypting}
          <span>Encrypting...</span>
        {:else}
          <span>Create Task</span>
        {/if}
      </button>
    </div>
  </form>
</div>