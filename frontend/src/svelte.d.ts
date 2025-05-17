/// <reference types="svelte" />

declare module '*.svelte' {
  import type { ComponentType } from 'svelte';
  const component: ComponentType<any>;
  export default component;
}

declare module 'svelte-routing';