import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  // Simple TypeScript preprocessing
  preprocess: {
    script: ({ content }) => {
      return { code: content };
    }
  },

  kit: {
    // Use a simple static adapter for now
    adapter: {
      name: 'static-adapter',
      adapt: () => {
        // This is a simple adapter that doesn't do anything
        // We'll replace it with a proper adapter when needed
        console.log('Using static adapter');
      }
    },
    alias: {
      $lib: './src/lib',
      $components: './src/components',
      $stores: './src/stores',
      $utils: './src/utils'
    }
  }
};

export default config;