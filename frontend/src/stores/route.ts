import { writable, get } from 'svelte/store';
import { walletStore } from './wallet';

// Route store state
interface RouteState {
  currentRoute: string;
  previousRoute: string;
  params: Record<string, string>;
}

// Initial state
const initialState: RouteState = {
  currentRoute: typeof window !== 'undefined' ? window.location.pathname : '/',
  previousRoute: '',
  params: {}
};

// Create the writable store
const store = writable<RouteState>(initialState);

// Route store actions
export const routeStore = {
  subscribe: store.subscribe,
  
  // Initialize route store
  init: () => {
    // Parse initial route parameters
    const currentRoute = typeof window !== 'undefined' ? window.location.pathname : '/';
    let params: Record<string, string> = {};
    
    if (currentRoute.startsWith('/tasks/') && currentRoute !== '/tasks/create') {
      const id = currentRoute.split('/tasks/')[1];
      params = { id: id || '' };
    } else {
      params = { id: '' };
    }
    
    store.update(state => ({
      ...state,
      currentRoute,
      params
    }));
    
    // Set up event listeners for route changes
    if (typeof window !== 'undefined') {
      // Listen for popstate events (browser back/forward)
      window.addEventListener('popstate', () => {
        routeStore.handleRouteChange();
      });
      
      // Listen for click events on links
      document.addEventListener('click', (e) => {
        const target = e.target as HTMLElement;
        const anchor = target.closest('a');
        if (anchor && anchor.href && anchor.href.startsWith(window.location.origin)) {
          // Wait a bit for the route to change before checking
          setTimeout(() => {
            routeStore.handleRouteChange();
          }, 100);
        }
      });
    }
  },
  
  // Handle route changes
  handleRouteChange: () => {
    const currentState = get(store);
    const newRoute = typeof window !== 'undefined' ? window.location.pathname : '/';
    
    // Only update if the route has actually changed
    if (newRoute !== currentState.currentRoute) {
      console.log(`Route changed from ${currentState.currentRoute} to ${newRoute}`);
      
      // Parse route parameters
      let params: Record<string, string> = {};
      if (newRoute.startsWith('/tasks/') && newRoute !== '/tasks/create') {
        const id = newRoute.split('/tasks/')[1];
        params = { id: id || '' };
      } else {
        params = { id: '' };
      }
      
      // Update route store
      store.update(state => ({
        ...state,
        previousRoute: state.currentRoute,
        currentRoute: newRoute,
        params
      }));
      
      // Ensure wallet connection is maintained across routes
      console.log('Checking wallet connection after route change');
      walletStore.checkConnection();
    }
  },
  
  // Navigate to a new route
  navigate: (path: string) => {
    if (typeof window !== 'undefined') {
      window.history.pushState({}, '', path);
      routeStore.handleRouteChange();
    }
  }
};