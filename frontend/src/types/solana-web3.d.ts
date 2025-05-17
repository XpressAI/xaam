declare module '@solana/web3.js' {
  export class PublicKey {
    constructor(value: string | number[] | Uint8Array);
    toString(): string;
    toBase58(): string;
    toBytes(): Uint8Array;
    equals(publicKey: PublicKey): boolean;
  }

  export class Transaction {
    constructor(options?: any);
    add(...instructions: TransactionInstruction[]): Transaction;
    sign(...signers: Account[]): void;
    serialize(config?: any): Uint8Array;
    signatures: Array<SignaturePubkeyPair>;
  }

  export class TransactionInstruction {
    constructor(options: {
      keys: Array<AccountMeta>;
      programId: PublicKey;
      data?: Uint8Array;
    });
    keys: Array<AccountMeta>;
    programId: PublicKey;
    data: Uint8Array;
  }

  export class Account {
    constructor(secretKey?: Uint8Array);
    publicKey: PublicKey;
    secretKey: Uint8Array;
    sign(message: Uint8Array): Uint8Array;
  }

  export interface AccountMeta {
    pubkey: PublicKey;
    isSigner: boolean;
    isWritable: boolean;
  }

  export interface SignaturePubkeyPair {
    signature: Uint8Array | null;
    publicKey: PublicKey;
  }

  export class Connection {
    constructor(endpoint: string, commitment?: string);
    getBalance(publicKey: PublicKey): Promise<number>;
    getAccountInfo(publicKey: PublicKey): Promise<AccountInfo<Uint8Array> | null>;
    getMinimumBalanceForRentExemption(dataLength: number): Promise<number>;
    getRecentBlockhash(): Promise<{ blockhash: string; feeCalculator: FeeCalculator }>;
    sendTransaction(transaction: Transaction, signers: Array<Account>, options?: any): Promise<string>;
    confirmTransaction(signature: string): Promise<{ err: any }>;
    getSignatureStatus(signature: string): Promise<{ err: any }>;
    requestAirdrop(publicKey: PublicKey, lamports: number): Promise<string>;
  }

  export interface AccountInfo<T> {
    executable: boolean;
    owner: PublicKey;
    lamports: number;
    data: T;
    rentEpoch?: number;
  }

  export interface FeeCalculator {
    lamportsPerSignature: number;
  }

  export const clusterApiUrl: (cluster: 'mainnet-beta' | 'testnet' | 'devnet') => string;
  export const LAMPORTS_PER_SOL: number;
}