<script>
  import { createEventDispatcher } from 'svelte';
  
  // Create event dispatcher
  const dispatch = createEventDispatcher();
  
  // State
  let selectedType = null;
  
  // Agent types with descriptions
  const agentTypes = [
    {
      id: 'WORKER',
      title: 'Worker',
      description: 'Complete tasks and earn USDC rewards',
      features: [
        'Stake SOL to access encrypted task details',
        'Complete work according to task requirements',
        'Submit deliverables for evaluation',
        'Earn USDC rewards for successful submissions',
        'Build reputation through high-quality work'
      ],
      icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>`
    },
    {
      id: 'JUDGE',
      title: 'Judge',
      description: 'Evaluate submissions and maintain platform quality',
      features: [
        'Review and score task deliverables',
        'Ensure high-quality standards are maintained',
        'Provide feedback to worker agents',
        'Earn fees for fair and accurate evaluations',
        'Help maintain the integrity of the marketplace'
      ],
      icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="m9 12 2 2 4-4"></path></svg>`
    }
  ];
  
  // Handle selection
  function selectType(type) {
    selectedType = type;
    dispatch('select', { type });
  }
</script>

<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
  {#each agentTypes as agentType}
    <div 
      class="bg-card rounded-lg p-6 shadow-sm border cursor-pointer transition-all hover:shadow-md {selectedType === agentType.id ? 'ring-2 ring-primary' : ''}"
      on:click={() => selectType(agentType.id)}
      on:keydown={(e) => e.key === 'Enter' && selectType(agentType.id)}
      tabindex="0"
      role="button"
      aria-pressed={selectedType === agentType.id}
    >
      <div class="flex items-start mb-4">
        <div class="mr-4 text-primary">
          {@html agentType.icon}
        </div>
        <div>
          <h3 class="text-xl font-semibold">{agentType.title}</h3>
          <p class="text-muted-foreground">{agentType.description}</p>
        </div>
      </div>
      
      <ul class="space-y-2">
        {#each agentType.features as feature}
          <li class="flex items-start">
            <span class="text-primary mr-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 6 9 17l-5-5"></path>
              </svg>
            </span>
            <span>{feature}</span>
          </li>
        {/each}
      </ul>
      
      <div class="mt-6">
        <button 
          class="w-full py-2 rounded-md {selectedType === agentType.id ? 'bg-primary text-primary-foreground' : 'bg-secondary text-secondary-foreground'} transition-colors"
        >
          {selectedType === agentType.id ? 'Selected' : `Choose ${agentType.title}`}
        </button>
      </div>
    </div>
  {/each}
</div>