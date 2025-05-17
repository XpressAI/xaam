declare module 'svelte/store' {
  export interface Readable<T> {
    subscribe(run: (value: T) => void): () => void;
  }

  export interface Writable<T> extends Readable<T> {
    set(value: T): void;
    update(updater: (value: T) => T): void;
  }

  export function writable<T>(value: T): Writable<T>;
  export function readable<T>(value: T, start?: (set: (value: T) => void) => () => void): Readable<T>;
  export function derived<S, T>(stores: Readable<S>, fn: (value: S) => T): Readable<T>;
  export function get<T>(store: Readable<T>): T;
}