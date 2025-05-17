declare module 'svelte' {
  export function onMount(callback: () => void | (() => void)): void;
  export function onDestroy(callback: () => void): void;
  export function beforeUpdate(callback: () => void): void;
  export function afterUpdate(callback: () => void): void;
  export function tick(): Promise<void>;
  export function setContext<T>(key: any, context: T): T;
  export function getContext<T>(key: any): T;
  export function hasContext(key: any): boolean;
  export function createEventDispatcher<T extends Record<string, any>>(): (type: keyof T, detail?: T[keyof T]) => void;
}