<script>
  import '../app.css';
  import { walletStore } from '../lib/stores/wallet';
  import Layout from '../lib/components/Layout.svelte';
  
  // Initialize wallet connection when the app loads
  if (typeof window !== 'undefined') {
    // Check for existing wallet connection
    setTimeout(() => {
      walletStore.checkConnection();
    }, 0);
  }
</script>

<Layout>
  <slot />
</Layout>