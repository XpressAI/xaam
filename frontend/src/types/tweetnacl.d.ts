declare module 'tweetnacl' {
  export const box: any;
  export const secretbox: any;
  export const sign: any;
  export function randomBytes(length: number): Uint8Array;
  export function hash(message: Uint8Array): Uint8Array;
  export function verify(a: Uint8Array, b: Uint8Array): boolean;
}

declare module 'tweetnacl-util' {
  export function encodeUTF8(array: Uint8Array): string;
  export function decodeUTF8(string: string): Uint8Array;
  export function encodeBase64(array: Uint8Array): string;
  export function decodeBase64(string: string): Uint8Array;
}