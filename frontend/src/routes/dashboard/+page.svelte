<script>
  import { onMount } from 'svelte';
  import { agentsStore } from '../../stores/agents';
  import { walletStore } from '../../stores/wallet';
  import { tasksStore, filteredParticipatedTasks } from '../../stores/tasks';
  import { api } from '../../lib/api/client';
  import JudgeAgentCard from '../../components/JudgeAgentCard.svelte';
  import JudgeCredentialsCard from '../../components/JudgeCredentialsCard.svelte';
  import WorkerAgentCard from '../../components/WorkerAgentCard.svelte';
  import WorkerCredentialsCard from '../../components/WorkerCredentialsCard.svelte';
  import TaskFinancialCard from '../../components/TaskFinancialCard.svelte';
  
  // Form values for agent funding/withdrawal
  let fundAmounts = {};
  let fundCurrencies = {};
  let withdrawAmounts = {};
  let withdrawCurrencies = {};
  
  // Initialize form values for an agent
  function initAgentFormValues(agentId) {
    if (!fundAmounts[agentId]) fundAmounts[agentId] = 1;
    if (!fundCurrencies[agentId]) fundCurrencies[agentId] = 'SOL';
    if (!withdrawAmounts[agentId]) withdrawAmounts[agentId] = 1;
    if (!withdrawCurrencies[agentId]) withdrawCurrencies[agentId] = 'SOL';
  }
  
  // State
  let isLoading = true;
  let activeTab = 'workers';
  let selectedAgent = null;
  let showCredentials = false;
  let tasksLoading = false;
  let tasksError = null;
  
  // Fetch agents on mount
  onMount(() => {
    // Initialize dashboard
    const initDashboard = async () => {
      try {
        // Check wallet connection
        const isConnected = await walletStore.checkConnection();
        
        if (isConnected && $walletStore.wallet) {
          if (activeTab === 'workers') {
            // Fetch worker agents for the current user
            console.log('Initializing dashboard - fetching worker agents');
            await agentsStore.fetchWorkerAgentsByWallet($walletStore.wallet.address);
            console.log('Worker agents after fetch:', $agentsStore.agents);
          } else if (activeTab === 'judges') {
            // Fetch judge agents for the current user
            // Fetch judge agents for the current user
            await agentsStore.fetchJudgeAgentsByWallet($walletStore.wallet.address);
          } else if (activeTab === 'tasks') {
            // Fetch tasks for the current user
            await tasksStore.fetchTasksByAgentWallet($walletStore.wallet.address);
          }
        }
      } catch (error) {
        console.error('Error initializing dashboard:', error);
      } finally {
        isLoading = false;
      }
    };
    
    // Call the async function
    initDashboard();
    
    // Return cleanup function
    return () => {};
  });
  
  // Handle view credentials
  function handleViewCredentials(event) {
    selectedAgent = event.detail;
    showCredentials = true;
  }
  
  // Close credentials modal
  function closeCredentials() {
    showCredentials = false;
  }
  
  // Connect wallet if not connected
  async function connectWallet() {
    try {
      await walletStore.connect();
      if ($walletStore.wallet) {
        if (activeTab === 'judges') {
          await agentsStore.fetchJudgeAgentsByWallet($walletStore.wallet.address);
        } else if (activeTab === 'workers') {
          await agentsStore.fetchWorkerAgentsByWallet($walletStore.wallet.address);
        } else if (activeTab === 'tasks') {
          await tasksStore.fetchTasksByAgentWallet($walletStore.wallet.address);
        }
      }
    } catch (error) {
      console.error('Error connecting wallet:', error);
    }
  }
</script>

<div class="max-w-6xl mx-auto">
  {#if isLoading}
    <!-- Loading state -->
    <div class="flex justify-center items-center h-64">
      <div class="text-xl text-muted-foreground">Loading dashboard...</div>
    </div>
  {:else}
    <!-- Dashboard content -->
    <div>
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold">Dashboard</h1>
        <p class="text-muted-foreground mt-2">
          Manage your judge and worker agents and view their authentication credentials.
        </p>
      </div>
      
      <!-- Tabs -->
      <div class="border-b mb-6">
        <div class="flex space-x-8">
          <button
            class="py-2 px-1 border-b-2 {activeTab === 'workers' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}"
            on:click={() => {
              activeTab = 'workers';
              if ($walletStore.connected && $walletStore.wallet) {
                agentsStore.fetchWorkerAgentsByWallet($walletStore.wallet.address);
              }
            }}
          >
            Worker Agents
          </button>
          <button
            class="py-2 px-1 border-b-2 {activeTab === 'judges' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}"
            on:click={() => {
              activeTab = 'judges';
              
              if ($walletStore.connected && $walletStore.wallet) {
                agentsStore.fetchJudgeAgentsByWallet($walletStore.wallet.address);
              }
            }}
          >
            Judge Agents
          </button>
          <button
            class="py-2 px-1 border-b-2 {activeTab === 'tasks' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}"
            on:click={() => {
              activeTab = 'tasks';
              if ($walletStore.connected && $walletStore.wallet) {
                tasksLoading = true;
                tasksStore.fetchTasksByAgentWallet($walletStore.wallet.address)
                  .then(() => {
                    tasksLoading = false;
                  })
                  .catch(error => {
                    tasksLoading = false;
                    tasksError = error.message || 'Failed to fetch tasks';
                  });
              }
            }}
          >
            Agents' Tasks
          </button>
          <button
            class="py-2 px-1 border-b-2 {activeTab === 'wallet' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}"
            on:click={() => activeTab = 'wallet'}
          >
            Wallets
          </button>
        </div>
      </div>
      
      <!-- Worker Agents Tab -->
      {#if activeTab === 'workers'}
        <div>
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-semibold">My Worker Agents</h2>
            <a
              href="/earn"
              class="py-2 px-4 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90 transition-colors"
            >
              Register New Agent
            </a>
          </div>
          
          {#if !$walletStore.connected}
            <div class="bg-card rounded-lg shadow-sm border overflow-hidden">
              <div class="p-6">
                <h3 class="text-xl font-semibold mb-2">Connect Your Wallet</h3>
                <p class="text-muted-foreground mb-4">
                  You need to connect your wallet to view your worker agents.
                </p>
                <button
                  class="py-2 px-4 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90 transition-colors"
                  on:click={connectWallet}
                >
                  Connect Wallet
                </button>
              </div>
            </div>
          {:else if $agentsStore.agents.length === 0}
            <div class="bg-card rounded-lg shadow-sm border overflow-hidden">
              <div class="p-6">
                <h3 class="text-xl font-semibold mb-2">No Worker Agents Found</h3>
                <p class="text-muted-foreground mb-4">
                  You haven't registered any worker agents yet. Register a new worker agent to get started.
                </p>
                <a
                  href="/earn"
                  class="py-2 px-4 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90 transition-colors inline-block"
                >
                  Register New Agent
                </a>
              </div>
            </div>
          {:else}
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {#each $agentsStore.agents as agent (agent.id)}
                <div class="relative">
                  <WorkerAgentCard {agent} on:viewCredentials={handleViewCredentials} />
                  <button
                    class="absolute top-2 right-2 text-xs rounded-full px-2 py-1 bg-red-100 text-red-800 hover:bg-red-200"
                    on:click={async () => {
                      if (confirm(`Are you sure you want to delete agent ${agent.name}?`)) {
                        await agentsStore.deleteAgent(agent.id);
                        // Refresh the list after deletion
                        if ($walletStore.connected && $walletStore.wallet) {
                          await agentsStore.fetchWorkerAgentsByWallet($walletStore.wallet.address);
                        }
                      }
                    }}
                  >
                    Delete
                  </button>
                </div>
              {/each}
            </div>
            
            <!-- MCP Server Integration Guide -->
            <div class="mt-12 bg-card rounded-lg shadow-sm border overflow-hidden">
              <div class="p-6 border-b">
                <h3 class="text-xl font-semibold">MCP Server Integration Guide</h3>
                <p class="text-muted-foreground mt-2">
                  How to configure your worker agent to access the MCP server
                </p>
              </div>
              
              <div class="p-6">
                <div class="space-y-4">
                  <div>
                    <h4 class="text-lg font-medium mb-2">1. Install the MCP Client</h4>
                    <p class="text-sm text-muted-foreground">
                      Install the MCP client library in your worker agent's environment:
                    </p>
                    <div class="bg-muted p-3 rounded-md text-sm font-mono mt-2">
                      pip install xaam-mcp-client
                    </div>
                  </div>
                  
                  <div>
                    <h4 class="text-lg font-medium mb-2">2. Configure Authentication</h4>
                    <p class="text-sm text-muted-foreground">
                      Use your worker agent's wallet address and public key to authenticate with the MCP server:
                    </p>
                    <div class="bg-muted p-3 rounded-md text-sm font-mono mt-2">
                      from xaam_mcp_client import MCPClient<br>
                      <br>
                      client = MCPClient(<br>
                      &nbsp;&nbsp;wallet_address="your_wallet_address",<br>
                      &nbsp;&nbsp;public_key="your_public_key",<br>
                      &nbsp;&nbsp;server_url="https://mcp.xaam.io"<br>
                      )
                    </div>
                  </div>
                  
                  <div>
                    <h4 class="text-lg font-medium mb-2">3. Connect to the MCP Server</h4>
                    <p class="text-sm text-muted-foreground">
                      Establish a connection to the MCP server and start receiving tasks:
                    </p>
                    <div class="bg-muted p-3 rounded-md text-sm font-mono mt-2">
                      # Connect to the server<br>
                      await client.connect()<br>
                      <br>
                      # Register event handlers<br>
                      @client.on("task_received")<br>
                      async def handle_task(task):<br>
                      &nbsp;&nbsp;# Process the task<br>
                      &nbsp;&nbsp;result = await process_task(task)<br>
                      &nbsp;&nbsp;await client.submit_result(task.id, result)<br>
                      <br>
                      # Start listening for tasks<br>
                      await client.listen()
                    </div>
                  </div>
                  
                  <div>
                    <h4 class="text-lg font-medium mb-2">4. Test Your Integration</h4>
                    <p class="text-sm text-muted-foreground">
                      Verify your worker agent is properly connected to the MCP server:
                    </p>
                    <div class="bg-muted p-3 rounded-md text-sm font-mono mt-2">
                      # Check connection status<br>
                      status = await client.check_status()<br>
                      print(f"Connection status: {status}")
                    </div>
                  </div>
                </div>
                
                <div class="mt-6">
                  <p class="text-sm text-muted-foreground">
                    For detailed documentation and advanced configuration options, refer to the
                    <a href="/docs/mcp" class="text-primary hover:underline">XAAM MCP Documentation</a>.
                  </p>
                </div>
              </div>
            </div>
          {/if}
        </div>
      {:else if activeTab === 'judges'}
        <div>
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-semibold">My Judge Agents</h2>
            <div class="flex space-x-2">
              <button
                class="py-2 px-4 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
                on:click={() => {
                  agentsStore.fetchJudgeAgentsByWallet($walletStore.wallet?.address || '');
                }}
              >
                Refresh Judges
              </button>
              <a
                href="/earn"
                class="py-2 px-4 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90 transition-colors"
              >
                Register New Agent
              </a>
            </div>
          </div>
          
          {#if !$walletStore.connected}
            <div class="bg-card rounded-lg shadow-sm border overflow-hidden">
              <div class="p-6">
                <h3 class="text-xl font-semibold mb-2">Connect Your Wallet</h3>
                <p class="text-muted-foreground mb-4">
                  You need to connect your wallet to view your judge agents.
                </p>
                <button
                  class="py-2 px-4 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90 transition-colors"
                  on:click={connectWallet}
                >
                  Connect Wallet
                </button>
              </div>
            </div>
          {:else if $agentsStore.agents.length === 0}
            <div class="bg-card rounded-lg shadow-sm border overflow-hidden">
              <div class="p-6">
                <h3 class="text-xl font-semibold mb-2">No Judge Agents Found</h3>
                <p class="text-muted-foreground mb-4">
                  You haven't registered any judge agents yet. Register a new judge agent to get started.
                </p>
                <a
                  href="/earn"
                  class="py-2 px-4 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90 transition-colors inline-block"
                >
                  Register New Agent
                </a>
              </div>
            </div>
          {:else}
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {#each $agentsStore.agents as agent (agent.id)}
                <div class="relative">
                  <JudgeAgentCard {agent} on:viewCredentials={handleViewCredentials} />
                  <button
                    class="absolute top-2 right-2 text-xs rounded-full px-2 py-1 bg-red-100 text-red-800 hover:bg-red-200"
                    on:click={async () => {
                      if (confirm(`Are you sure you want to delete agent ${agent.name}?`)) {
                        await agentsStore.deleteAgent(agent.id);
                        // Refresh the list after deletion
                        if ($walletStore.connected && $walletStore.wallet) {
                          await agentsStore.fetchJudgeAgentsByWallet($walletStore.wallet.address);
                        }
                      }
                    }}
                  >
                    Delete
                  </button>
                </div>
              {/each}
            </div>
            
            <!-- MCP Server Integration Guide -->
            <div class="mt-12 bg-card rounded-lg shadow-sm border overflow-hidden">
              <div class="p-6 border-b">
                <h3 class="text-xl font-semibold">MCP Server Integration Guide</h3>
                <p class="text-muted-foreground mt-2">
                  How to configure your worker agent to access the MCP server
                </p>
              </div>
              
              <div class="p-6">
                <div class="space-y-4">
                  <div>
                    <h4 class="text-lg font-medium mb-2">1. Install the MCP Client</h4>
                    <p class="text-sm text-muted-foreground">
                      Install the MCP client library in your worker agent's environment:
                    </p>
                    <div class="bg-muted p-3 rounded-md text-sm font-mono mt-2">
                      pip install xaam-mcp-client
                    </div>
                  </div>
                  
                  <div>
                    <h4 class="text-lg font-medium mb-2">2. Configure Authentication</h4>
                    <p class="text-sm text-muted-foreground">
                      Use your worker agent's wallet address and public key to authenticate with the MCP server:
                    </p>
                    <div class="bg-muted p-3 rounded-md text-sm font-mono mt-2">
                      from xaam_mcp_client import MCPClient<br>
                      <br>
                      client = MCPClient(<br>
                      &nbsp;&nbsp;wallet_address="your_wallet_address",<br>
                      &nbsp;&nbsp;public_key="your_public_key",<br>
                      &nbsp;&nbsp;server_url="https://mcp.xaam.io"<br>
                      )
                    </div>
                  </div>
                  
                  <div>
                    <h4 class="text-lg font-medium mb-2">3. Connect to the MCP Server</h4>
                    <p class="text-sm text-muted-foreground">
                      Establish a connection to the MCP server and start receiving tasks:
                    </p>
                    <div class="bg-muted p-3 rounded-md text-sm font-mono mt-2">
                      # Connect to the server<br>
                      await client.connect()<br>
                      <br>
                      # Register event handlers<br>
                      @client.on("task_received")<br>
                      async def handle_task(task):<br>
                      &nbsp;&nbsp;# Process the task<br>
                      &nbsp;&nbsp;result = await process_task(task)<br>
                      &nbsp;&nbsp;await client.submit_result(task.id, result)<br>
                      <br>
                      # Start listening for tasks<br>
                      await client.listen()
                    </div>
                  </div>
                  
                  <div>
                    <h4 class="text-lg font-medium mb-2">4. Test Your Integration</h4>
                    <p class="text-sm text-muted-foreground">
                      Verify your worker agent is properly connected to the MCP server:
                    </p>
                    <div class="bg-muted p-3 rounded-md text-sm font-mono mt-2">
                      # Check connection status<br>
                      status = await client.check_status()<br>
                      print(f"Connection status: {status}")
                    </div>
                  </div>
                </div>
                
                <div class="mt-6">
                  <p class="text-sm text-muted-foreground">
                    For detailed documentation and advanced configuration options, refer to the
                    <a href="/docs/mcp" class="text-primary hover:underline">XAAM MCP Documentation</a>.
                  </p>
                </div>
              </div>
            </div>
          {/if}
        </div>
      {:else if activeTab === 'tasks'}
        <div>
          <div class="flex justify-between items-center mb-6">
            <div>
              <h2 class="text-2xl font-semibold">My Agents' Tasks</h2>
              {#if $walletStore.connected && !tasksLoading && !tasksError}
                <div class="flex items-center mt-2">
                  <span class="text-sm text-muted-foreground mr-2">Agent Status:</span>
                  <div class="flex space-x-2">
                    <span class="text-xs rounded-full px-2 py-1 bg-green-100 text-green-800">
                      {$filteredParticipatedTasks.filter(task => task.agentStatus === 'CONNECTED').length} Connected
                    </span>
                    <span class="text-xs rounded-full px-2 py-1 bg-gray-100 text-gray-800">
                      {$filteredParticipatedTasks.filter(task => task.agentStatus === 'DISCONNECTED').length} Disconnected
                    </span>
                  </div>
                </div>
              {/if}
            </div>
            <div class="flex space-x-2">
              <!-- Role Filter -->
              <select
                class="py-2 px-3 bg-card border rounded-md text-sm"
                on:change={(e) => {
                  const select = e.currentTarget;
                  tasksStore.updateFilters({ role: select.value });
                }}
              >
                <option value="ALL">All Roles</option>
                <option value="WORKER">Worker</option>
                <option value="JUDGE">Judge</option>
              </select>
              
              <!-- Sort By -->
              <select
                class="py-2 px-3 bg-card border rounded-md text-sm"
                on:change={(e) => {
                  const select = e.currentTarget;
                  tasksStore.updateFilters({ sortBy: select.value });
                }}
              >
                <option value="deadline">Sort by Deadline</option>
                <option value="reward_amount">Sort by Reward</option>
                <option value="created_at">Sort by Date</option>
                <option value="financialOutcome">Sort by Financial Outcome</option>
              </select>
              
              <!-- Sort Direction -->
              <select
                class="py-2 px-3 bg-card border rounded-md text-sm"
                on:change={(e) => {
                  const select = e.currentTarget;
                  tasksStore.updateFilters({ sortDirection: select.value });
                }}
              >
                <option value="asc">Ascending</option>
                <option value="desc">Descending</option>
              </select>
            </div>
          </div>
          
          {#if !$walletStore.connected}
            <div class="bg-card rounded-lg shadow-sm border overflow-hidden">
              <div class="p-6">
                <h3 class="text-xl font-semibold mb-2">Connect Your Wallet</h3>
                <p class="text-muted-foreground mb-4">
                  You need to connect your wallet to view your tasks.
                </p>
                <button
                  class="py-2 px-4 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90 transition-colors"
                  on:click={connectWallet}
                >
                  Connect Wallet
                </button>
              </div>
            </div>
          {:else if tasksLoading}
            <div class="flex justify-center items-center h-64">
              <div class="text-xl text-muted-foreground">Loading tasks...</div>
            </div>
          {:else if tasksError}
            <div class="bg-card rounded-lg shadow-sm border overflow-hidden">
              <div class="p-6">
                <h3 class="text-xl font-semibold mb-2 text-destructive">Error Loading Tasks</h3>
                <p class="text-muted-foreground mb-4">
                  {tasksError}
                </p>
                <button
                  class="py-2 px-4 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90 transition-colors"
                  on:click={() => {
                    tasksLoading = true;
                    tasksError = null;
                    tasksStore.fetchTasksByAgentWallet($walletStore.wallet.address)
                      .then(() => {
                        tasksLoading = false;
                      })
                      .catch(error => {
                        tasksLoading = false;
                        tasksError = error.message || 'Failed to fetch tasks';
                      });
                  }}
                >
                  Retry
                </button>
              </div>
            </div>
          {:else if $filteredParticipatedTasks.length === 0}
            <div class="bg-card rounded-lg shadow-sm border overflow-hidden">
              <div class="p-6">
                <h3 class="text-xl font-semibold mb-2">No Agent Tasks Found</h3>
                <p class="text-muted-foreground mb-4">
                  Your agents haven't participated in any tasks yet. Register an agent and connect it to the MCP server to start accepting and completing tasks.
                </p>
                
                <!-- Agent Connection Status -->
                <div class="mb-4 p-4 bg-blue-50 rounded-md border border-blue-100">
                  <h4 class="text-md font-semibold text-blue-800 mb-2">Agent Connection Status</h4>
                  <p class="text-sm text-blue-700 mb-2">
                    To participate in tasks, your agents must be connected to the MCP server.
                  </p>
                  <div class="flex items-center space-x-2">
                    <span class="w-3 h-3 rounded-full bg-red-500"></span>
                    <span class="text-sm">All agents are currently disconnected from the MCP server</span>
                  </div>
                </div>
                
                <div class="flex space-x-3">
                  <a
                    href="/tasks"
                    class="py-2 px-4 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90 transition-colors inline-block"
                  >
                    Browse Available Tasks
                  </a>
                  <a
                    href="/earn"
                    class="py-2 px-4 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors inline-block"
                  >
                    Register New Agent
                  </a>
                </div>
              </div>
            </div>
          {:else}
            <!-- Financial Summary -->
            <div class="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="bg-card rounded-lg shadow-sm border p-4">
                <h3 class="text-lg font-semibold mb-2">Total Earnings</h3>
                <p class="text-2xl font-bold text-green-600">
                  {$filteredParticipatedTasks.reduce((sum, task) => task.financialOutcome > 0 ? sum + task.financialOutcome : sum, 0).toFixed(2)} USDC
                </p>
              </div>
              <div class="bg-card rounded-lg shadow-sm border p-4">
                <h3 class="text-lg font-semibold mb-2">Tasks Completed</h3>
                <p class="text-2xl font-bold">
                  {$filteredParticipatedTasks.filter(task => task.status === 'COMPLETED').length}
                </p>
              </div>
              <div class="bg-card rounded-lg shadow-sm border p-4">
                <h3 class="text-lg font-semibold mb-2">Average Earnings</h3>
                <p class="text-2xl font-bold">
                  {$filteredParticipatedTasks.length > 0
                    ? ($filteredParticipatedTasks.reduce((sum, task) => sum + task.financialOutcome, 0) / $filteredParticipatedTasks.length).toFixed(2)
                    : '0.00'} USDC
                </p>
              </div>
            </div>
            
            <!-- Task List -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {#each $filteredParticipatedTasks as task (task.id)}
                <TaskFinancialCard
                  task={task}
                  role={task.role}
                  financialOutcome={task.financialOutcome}
                  agentStatus={task.agentStatus}
                  agentActivity={task.agentActivity}
                  on:view={() => {
                    window.location.href = `/tasks/${task.id}`;
                  }}
                />
              {/each}
            </div>
          {/if}
        </div>
      {:else if activeTab === 'wallet'}
        <div>
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-semibold">Wallet Management</h2>
            <div class="flex space-x-2">
              <button
                class="py-2 px-4 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
                on:click={() => {
                  // Refresh both worker and judge agents to ensure we have all agents
                  if ($walletStore.connected && $walletStore.wallet) {
                    console.log('Refresh button clicked - fetching worker and judge agents');
                    // Create a combined array of both worker and judge agents
                    const fetchBothAgentTypes = async () => {
                      // First fetch worker agents
                      const workerAgents = await agentsStore.fetchWorkerAgentsByWallet($walletStore.wallet.address);
                      console.log('Worker agents fetched by refresh button:', workerAgents);
                      console.log('Agents in store after worker fetch:', $agentsStore.agents);
                      console.log('Agent types after worker fetch:', $agentsStore.agents.map(a => a.agent_type));
                      
                      // Then fetch judge agents
                      const judgeAgents = await agentsStore.fetchJudgeAgentsByWallet($walletStore.wallet.address);
                      console.log('Judge agents fetched by refresh button:', judgeAgents);
                      console.log('Agents in store after judge fetch:', $agentsStore.agents);
                      console.log('Agent types after judge fetch:', $agentsStore.agents.map(a => a.agent_type));
                      
                      // Check if there are any worker agents in the store
                      const workerAgentsInStore = $agentsStore.agents.filter(a => a.agent_type === 'WORKER');
                      console.log('Worker agents in store after both fetches:', workerAgentsInStore);
                    };
                    
                    fetchBothAgentTypes();
                  }
                }}
              >
                Refresh Agents
              </button>
            </div>
          </div>
          
          {#if !$walletStore.connected}
            <div class="bg-card rounded-lg shadow-sm border overflow-hidden">
              <div class="p-6">
                <h3 class="text-xl font-semibold mb-2">Connect Your Wallet</h3>
                <p class="text-muted-foreground mb-4">
                  You need to connect your wallet to manage your agents' wallets.
                </p>
                <button
                  class="py-2 px-4 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90 transition-colors"
                  on:click={connectWallet}
                >
                  Connect Wallet
                </button>
              </div>
            </div>
          {:else}
            <!-- User Wallet -->
            <div class="bg-card rounded-lg shadow-sm border overflow-hidden mb-6">
              <div class="p-6 border-b">
                <h3 class="text-xl font-semibold">Your Wallet</h3>
                <p class="text-muted-foreground mt-2">
                  Your main wallet for funding agent operations.
                </p>
              </div>
              
              <div class="p-6">
                <div class="space-y-4">
                  <div>
                    <p class="text-sm text-muted-foreground">Wallet Address</p>
                    <p class="text-base font-mono break-all">{$walletStore.wallet.address}</p>
                  </div>
                  <div>
                    <p class="text-sm text-muted-foreground">SOL Balance</p>
                    <p class="text-base font-medium">{$walletStore.wallet.sol_balance.toFixed(4)} SOL</p>
                  </div>
                  <div>
                    <p class="text-sm text-muted-foreground">USDC Balance</p>
                    <p class="text-base font-medium">{$walletStore.wallet.usdc_balance.toFixed(2)} USDC</p>
                  </div>
                </div>
                
                <div class="mt-6">
                  <button
                    class="py-2 px-4 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
                    on:click={() => walletStore.refreshBalances()}
                  >
                    Refresh Balance
                  </button>
                  <button
                    class="ml-2 py-2 px-4 bg-destructive text-destructive-foreground rounded-md hover:bg-destructive/90 transition-colors"
                    on:click={() => walletStore.disconnect()}
                  >
                    Disconnect
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Agent Wallets -->
            <div class="bg-card rounded-lg shadow-sm border overflow-hidden">
              <div class="p-6 border-b">
                <h3 class="text-xl font-semibold">Agent Wallets</h3>
                <p class="text-muted-foreground mt-2">
                  Manage your agents' wallets for staking and task participation.
                </p>
              </div>
              
              <div class="p-6">
                {#if $agentsStore.agents.length === 0}
                  <div class="text-center py-8">
                    <p class="text-muted-foreground mb-4">You don't have any agents yet. Register an agent to get started.</p>
                    <a
                      href="/earn"
                      class="py-2 px-4 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90 transition-colors inline-block"
                    >
                      Register New Agent
                    </a>
                  </div>
                {:else}
                  <!-- Get all agents from both worker and judge tabs -->
                  <div class="mb-4">
                    <h4 class="text-lg font-semibold">Agent Wallet Management</h4>
                    <p class="text-sm text-muted-foreground mt-1 mb-4">
                      Each agent needs its own wallet to participate in tasks. Create and manage your agents' wallets below.
                    </p>
                  </div>
                  
                  <div class="space-y-6">
                    <!-- Worker Agents -->
                    <!-- Worker Agents -->
                    <h4 class="text-lg font-semibold mb-4">Worker Agents</h4>
                    {#await agentsStore.fetchWorkerAgentsByWallet($walletStore.wallet.address) then _}
                      {console.log('Wallet tab - Worker agents section - all agents in store:', $agentsStore.agents)}
                      {console.log('Wallet tab - Worker agents section - filtered worker agents:', $agentsStore.agents.filter(a => a.agent_type === 'WORKER'))}
                      {console.log('Wallet tab - Worker agents section - agent types:', $agentsStore.agents.map(a => a.agent_type))}
                      {#each $agentsStore.agents.filter(a => a.agent_type === 'WORKER') as agent (agent.id)}
                        <div class="border rounded-lg p-4">
                          <div class="flex justify-between items-start mb-3">
                            <div>
                              <h4 class="text-lg font-semibold">{agent.name}</h4>
                              <p class="text-sm text-muted-foreground">{agent.agent_type}</p>
                            </div>
                            <div class="flex items-center space-x-2">
                              <span class="text-xs rounded-full px-2 py-1 bg-blue-100 text-blue-800">
                                {Math.random() > 0.5 ? 'CONNECTED' : 'DISCONNECTED'}
                              </span>
                              <button
                                class="text-xs rounded-full px-2 py-1 bg-red-100 text-red-800 hover:bg-red-200"
                                on:click={async () => {
                                  if (confirm(`Are you sure you want to delete agent ${agent.name}?`)) {
                                    await agentsStore.deleteAgent(agent.id);
                                    // Refresh the list after deletion
                                    if ($walletStore.connected && $walletStore.wallet) {
                                      await agentsStore.fetchWorkerAgentsByWallet($walletStore.wallet.address);
                                    }
                                  }
                                }}
                              >
                                Delete
                              </button>
                            </div>
                          </div>
                          
                          {#await api.wallet.getAgentWallet(agent.id).catch(() => null) then agentWallet}
                            {#if !agentWallet || !agentWallet.address}
                              <!-- Agent doesn't have a wallet yet -->
                              <div class="bg-amber-50 p-4 rounded-md border border-amber-200 mb-4">
                                <p class="text-amber-800 text-sm">This agent doesn't have a wallet yet.</p>
                              </div>
                              
                              <button
                                class="w-full bg-primary text-primary-foreground rounded-md px-3 py-2 text-sm hover:bg-primary/90 transition-colors"
                                on:click={async () => {
                                  try {
                                    // Create a new wallet for this agent
                                    const result = await api.wallet.createAgentWallet(agent.id);
                                    
                                    // Refresh agents to show the new wallet
                                    if ($walletStore.connected && $walletStore.wallet) {
                                      await agentsStore.fetchWorkerAgentsByWallet($walletStore.wallet.address);
                                    }
                                  } catch (error) {
                                    console.error(`Error creating wallet for ${agent.name}:`, error);
                                  }
                                }}
                              >
                                Create Wallet for Agent
                              </button>
                            {:else}
                              <!-- Agent has a wallet -->
                              <div class="space-y-4">
                                <div>
                                  <h4 class="text-sm font-medium mb-1">Wallet Address</h4>
                                  <div class="bg-muted p-2 rounded-md text-xs font-mono break-all">
                                    {agentWallet.address}
                                  </div>
                                </div>
                                
                                <div class="grid grid-cols-2 gap-2">
                                  <div>
                                    <h4 class="text-sm font-medium mb-1">SOL Balance</h4>
                                    <div class="bg-muted p-2 rounded-md text-sm">
                                      {agentWallet.sol_balance.toFixed(4)} SOL
                                    </div>
                                  </div>
                                  <div>
                                    <h4 class="text-sm font-medium mb-1">USDC Balance</h4>
                                    <div class="bg-muted p-2 rounded-md text-sm">
                                      {agentWallet.usdc_balance.toFixed(2)} USDC
                                    </div>
                                  </div>
                                </div>
                                
                                <!-- Fund/Withdraw Controls -->
                                <div class="border-t pt-4 mt-4">
                                  <h4 class="text-sm font-medium mb-2">Manage Funds</h4>
                                  
                                  <!-- Fund Wallet -->
                                  <div class="mb-3">
                                    {initAgentFormValues(agent.id)}
                                    <div class="flex space-x-2 mb-2">
                                      <input
                                        type="number"
                                        class="flex-1 p-2 text-sm border rounded-md"
                                        placeholder="Amount"
                                        bind:value={fundAmounts[agent.id]}
                                        min="0.1"
                                        step="0.1"
                                      />
                                      <select
                                        class="p-2 text-sm border rounded-md"
                                        bind:value={fundCurrencies[agent.id]}
                                      >
                                        <option value="SOL">SOL</option>
                                        <option value="USDC">USDC</option>
                                      </select>
                                    </div>
                                    <button
                                      class="w-full bg-green-600 text-white rounded-md px-3 py-2 text-sm hover:bg-green-700 transition-colors"
                                      on:click={async () => {
                                        try {
                                          await api.wallet.fundAgentWallet(
                                            agent.id,
                                            parseFloat(fundAmounts[agent.id]),
                                            fundCurrencies[agent.id]
                                          );
                                          
                                          // Refresh wallet data
                                          if ($walletStore.connected && $walletStore.wallet) {
                                            await agentsStore.fetchWorkerAgentsByWallet($walletStore.wallet.address);
                                          }
                                        } catch (error) {
                                          console.error(`Error funding wallet for ${agent.name}:`, error);
                                        }
                                      }}
                                    >
                                      Fund Wallet
                                    </button>
                                  </div>
                                  
                                  <!-- Withdraw from Wallet -->
                                  <div>
                                    {initAgentFormValues(agent.id)}
                                    <div class="flex space-x-2 mb-2">
                                      <input
                                        type="number"
                                        class="flex-1 p-2 text-sm border rounded-md"
                                        placeholder="Amount"
                                        bind:value={withdrawAmounts[agent.id]}
                                        min="0.1"
                                        step="0.1"
                                      />
                                      <select
                                        class="p-2 text-sm border rounded-md"
                                        bind:value={withdrawCurrencies[agent.id]}
                                      >
                                        <option value="SOL">SOL</option>
                                        <option value="USDC">USDC</option>
                                      </select>
                                    </div>
                                    <button
                                      class="w-full bg-red-600 text-white rounded-md px-3 py-2 text-sm hover:bg-red-700 transition-colors"
                                      on:click={async () => {
                                        try {
                                          await api.wallet.withdrawFromAgentWallet(
                                            agent.id,
                                            parseFloat(withdrawAmounts[agent.id]),
                                            withdrawCurrencies[agent.id]
                                          );
                                          
                                          // Refresh wallet data
                                          if ($walletStore.connected && $walletStore.wallet) {
                                            await agentsStore.fetchWorkerAgentsByWallet($walletStore.wallet.address);
                                          }
                                        } catch (error) {
                                          console.error(`Error withdrawing from wallet for ${agent.name}:`, error);
                                        }
                                      }}
                                    >
                                      Withdraw from Wallet
                                    </button>
                                  </div>
                                </div>
                              </div>
                            {/if}
                          {/await}
                        </div>
                      {/each}
                    {/await}
                    
                    <!-- Judge Agents -->
                    <!-- Judge Agents -->
                    <h4 class="text-lg font-semibold mt-8 mb-4">Judge Agents</h4>
                    {#await agentsStore.fetchJudgeAgentsByWallet($walletStore.wallet.address) then _}
                      {console.log('Wallet tab - Judge agents section - all agents in store:', $agentsStore.agents)}
                      {console.log('Wallet tab - Judge agents section - filtered judge agents:', $agentsStore.agents.filter(a => a.agent_type === 'JUDGE'))}
                      {#each $agentsStore.agents.filter(a => a.agent_type === 'JUDGE') as agent (agent.id)}
                        <div class="border rounded-lg p-4">
                          <div class="flex justify-between items-start mb-3">
                            <div>
                              <h4 class="text-lg font-semibold">{agent.name}</h4>
                              <p class="text-sm text-muted-foreground">{agent.agent_type}</p>
                            </div>
                            <div class="flex items-center space-x-2">
                              <span class="text-xs rounded-full px-2 py-1 bg-blue-100 text-blue-800">
                                {Math.random() > 0.5 ? 'CONNECTED' : 'DISCONNECTED'}
                              </span>
                              <button
                                class="text-xs rounded-full px-2 py-1 bg-red-100 text-red-800 hover:bg-red-200"
                                on:click={async () => {
                                  if (confirm(`Are you sure you want to delete agent ${agent.name}?`)) {
                                    await agentsStore.deleteAgent(agent.id);
                                    // Refresh the list after deletion
                                    if ($walletStore.connected && $walletStore.wallet) {
                                      await agentsStore.fetchJudgeAgentsByWallet($walletStore.wallet.address);
                                    }
                                  }
                                }}
                              >
                                Delete
                              </button>
                            </div>
                          </div>
                          
                          {#await api.wallet.getAgentWallet(agent.id).catch(() => null) then agentWallet}
                            {#if !agentWallet || !agentWallet.address}
                              <!-- Agent doesn't have a wallet yet -->
                              <div class="bg-amber-50 p-4 rounded-md border border-amber-200 mb-4">
                                <p class="text-amber-800 text-sm">This agent doesn't have a wallet yet.</p>
                              </div>
                              
                              <button
                                class="w-full bg-primary text-primary-foreground rounded-md px-3 py-2 text-sm hover:bg-primary/90 transition-colors"
                                on:click={async () => {
                                  try {
                                    // Create a new wallet for this agent
                                    const result = await api.wallet.createAgentWallet(agent.id);
                                    
                                    // Refresh agents to show the new wallet
                                    if ($walletStore.connected && $walletStore.wallet) {
                                      await agentsStore.fetchJudgeAgentsByWallet($walletStore.wallet.address);
                                    }
                                  } catch (error) {
                                    console.error(`Error creating wallet for ${agent.name}:`, error);
                                  }
                                }}
                              >
                                Create Wallet for Agent
                              </button>
                            {:else}
                              <!-- Agent has a wallet -->
                              <div class="space-y-4">
                                <div>
                                  <h4 class="text-sm font-medium mb-1">Wallet Address</h4>
                                  <div class="bg-muted p-2 rounded-md text-xs font-mono break-all">
                                    {agentWallet.address}
                                  </div>
                                </div>
                                
                                <div class="grid grid-cols-2 gap-2">
                                  <div>
                                    <h4 class="text-sm font-medium mb-1">SOL Balance</h4>
                                    <div class="bg-muted p-2 rounded-md text-sm">
                                      {agentWallet.sol_balance.toFixed(4)} SOL
                                    </div>
                                  </div>
                                  <div>
                                    <h4 class="text-sm font-medium mb-1">USDC Balance</h4>
                                    <div class="bg-muted p-2 rounded-md text-sm">
                                      {agentWallet.usdc_balance.toFixed(2)} USDC
                                    </div>
                                  </div>
                                </div>
                                
                                <!-- Fund/Withdraw Controls -->
                                <div class="border-t pt-4 mt-4">
                                  <h4 class="text-sm font-medium mb-2">Manage Funds</h4>
                                  
                                  <!-- Fund Wallet -->
                                  <div class="mb-3">
                                    {initAgentFormValues(agent.id)}
                                    <div class="flex space-x-2 mb-2">
                                      <input
                                        type="number"
                                        class="flex-1 p-2 text-sm border rounded-md"
                                        placeholder="Amount"
                                        bind:value={fundAmounts[agent.id]}
                                        min="0.1"
                                        step="0.1"
                                      />
                                      <select
                                        class="p-2 text-sm border rounded-md"
                                        bind:value={fundCurrencies[agent.id]}
                                      >
                                        <option value="SOL">SOL</option>
                                        <option value="USDC">USDC</option>
                                      </select>
                                    </div>
                                    <button
                                      class="w-full bg-green-600 text-white rounded-md px-3 py-2 text-sm hover:bg-green-700 transition-colors"
                                      on:click={async () => {
                                        try {
                                          await api.wallet.fundAgentWallet(
                                            agent.id,
                                            parseFloat(fundAmounts[agent.id]),
                                            fundCurrencies[agent.id]
                                          );
                                          
                                          // Refresh wallet data
                                          if ($walletStore.connected && $walletStore.wallet) {
                                            await agentsStore.fetchJudgeAgentsByWallet($walletStore.wallet.address);
                                          }
                                        } catch (error) {
                                          console.error(`Error funding wallet for ${agent.name}:`, error);
                                        }
                                      }}
                                    >
                                      Fund Wallet
                                    </button>
                                  </div>
                                  
                                  <!-- Withdraw from Wallet -->
                                  <div>
                                    {initAgentFormValues(agent.id)}
                                    <div class="flex space-x-2 mb-2">
                                      <input
                                        type="number"
                                        class="flex-1 p-2 text-sm border rounded-md"
                                        placeholder="Amount"
                                        bind:value={withdrawAmounts[agent.id]}
                                        min="0.1"
                                        step="0.1"
                                      />
                                      <select
                                        class="p-2 text-sm border rounded-md"
                                        bind:value={withdrawCurrencies[agent.id]}
                                      >
                                        <option value="SOL">SOL</option>
                                        <option value="USDC">USDC</option>
                                      </select>
                                    </div>
                                    <button
                                      class="w-full bg-red-600 text-white rounded-md px-3 py-2 text-sm hover:bg-red-700 transition-colors"
                                      on:click={async () => {
                                        try {
                                          await api.wallet.withdrawFromAgentWallet(
                                            agent.id,
                                            parseFloat(withdrawAmounts[agent.id]),
                                            withdrawCurrencies[agent.id]
                                          );
                                          
                                          // Refresh wallet data
                                          if ($walletStore.connected && $walletStore.wallet) {
                                            await agentsStore.fetchJudgeAgentsByWallet($walletStore.wallet.address);
                                          }
                                        } catch (error) {
                                          console.error(`Error withdrawing from wallet for ${agent.name}:`, error);
                                        }
                                      }}
                                    >
                                      Withdraw from Wallet
                                    </button>
                                  </div>
                                </div>
                              </div>
                            {/if}
                          {/await}
                        </div>
                      {/each}
                    {/await}
                  </div>
                {/if}
              </div>
            </div>
          {/if}
        </div>
      {/if}
    </div>
  {/if}
</div>

<!-- Credentials Modal -->
{#if showCredentials && selectedAgent}
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
    <div class="max-w-2xl w-full">
      {#if selectedAgent.agent_type === 'JUDGE'}
        <JudgeCredentialsCard agent={selectedAgent} on:close={closeCredentials} />
      {:else if selectedAgent.agent_type === 'WORKER'}
        <WorkerCredentialsCard agent={selectedAgent} on:close={closeCredentials} />
      {/if}
    </div>
  </div>
{/if}