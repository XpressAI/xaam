declare interface Buffer extends Uint8Array {
  write(string: string, offset?: number, length?: number, encoding?: string): number;
  toString(encoding?: string, start?: number, end?: number): string;
  toJSON(): { type: 'Buffer'; data: number[] };
  equals(otherBuffer: Uint8Array): boolean;
  compare(otherBuffer: Uint8Array, targetStart?: number, targetEnd?: number, sourceStart?: number, sourceEnd?: number): number;
  copy(targetBuffer: Uint8Array, targetStart?: number, sourceStart?: number, sourceEnd?: number): number;
  slice(start?: number, end?: number): Buffer;
  writeUIntLE(value: number, offset: number, byteLength: number): number;
  writeUIntBE(value: number, offset: number, byteLength: number): number;
  writeIntLE(value: number, offset: number, byteLength: number): number;
  writeIntBE(value: number, offset: number, byteLength: number): number;
  readUIntLE(offset: number, byteLength: number): number;
  readUIntBE(offset: number, byteLength: number): number;
  readIntLE(offset: number, byteLength: number): number;
  readIntBE(offset: number, byteLength: number): number;
  readUInt8(offset: number): number;
  readUInt16LE(offset: number): number;
  readUInt16BE(offset: number): number;
  readUInt32LE(offset: number): number;
  readUInt32BE(offset: number): number;
  readInt8(offset: number): number;
  readInt16LE(offset: number): number;
  readInt16BE(offset: number): number;
  readInt32LE(offset: number): number;
  readInt32BE(offset: number): number;
  readFloatLE(offset: number): number;
  readFloatBE(offset: number): number;
  readDoubleLE(offset: number): number;
  readDoubleBE(offset: number): number;
  swap16(): Buffer;
  swap32(): Buffer;
  swap64(): Buffer;
  writeUInt8(value: number, offset: number): number;
  writeUInt16LE(value: number, offset: number): number;
  writeUInt16BE(value: number, offset: number): number;
  writeUInt32LE(value: number, offset: number): number;
  writeUInt32BE(value: number, offset: number): number;
  writeInt8(value: number, offset: number): number;
  writeInt16LE(value: number, offset: number): number;
  writeInt16BE(value: number, offset: number): number;
  writeInt32LE(value: number, offset: number): number;
  writeInt32BE(value: number, offset: number): number;
  writeFloatLE(value: number, offset: number): number;
  writeFloatBE(value: number, offset: number): number;
  writeDoubleLE(value: number, offset: number): number;
  writeDoubleBE(value: number, offset: number): number;
  fill(value: any, offset?: number, end?: number): this;
  indexOf(value: string | number | Uint8Array, byteOffset?: number, encoding?: string): number;
  lastIndexOf(value: string | number | Uint8Array, byteOffset?: number, encoding?: string): number;
  includes(value: string | number | Uint8Array, byteOffset?: number, encoding?: string): boolean;
}

declare module NodeJS {
  interface Global {
    Buffer: {
      new (str: string, encoding?: string): Buffer;
      new (size: number): Buffer;
      new (array: Uint8Array): Buffer;
      new (arrayBuffer: ArrayBuffer): Buffer;
      new (array: any[]): Buffer;
      isBuffer(obj: any): boolean;
      byteLength(string: string, encoding?: string): number;
      concat(list: Buffer[], totalLength?: number): Buffer;
      from(arrayBuffer: ArrayBuffer, byteOffset?: number, length?: number): Buffer;
      from(data: any[]): Buffer;
      from(data: Uint8Array): Buffer;
      from(str: string, encoding?: string): Buffer;
      alloc(size: number, fill?: string | Buffer | number, encoding?: string): Buffer;
      allocUnsafe(size: number): Buffer;
      allocUnsafeSlow(size: number): Buffer;
    };
  }
}

declare var Buffer: {
  new (str: string, encoding?: string): Buffer;
  new (size: number): Buffer;
  new (array: Uint8Array): Buffer;
  new (arrayBuffer: ArrayBuffer): Buffer;
  new (array: any[]): Buffer;
  isBuffer(obj: any): boolean;
  byteLength(string: string, encoding?: string): number;
  concat(list: Buffer[], totalLength?: number): Buffer;
  from(arrayBuffer: ArrayBuffer, byteOffset?: number, length?: number): Buffer;
  from(data: any[]): Buffer;
  from(data: Uint8Array): Buffer;
  from(str: string, encoding?: string): Buffer;
  alloc(size: number, fill?: string | Buffer | number, encoding?: string): Buffer;
  allocUnsafe(size: number): Buffer;
  allocUnsafeSlow(size: number): Buffer;
};