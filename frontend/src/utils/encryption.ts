import * as nacl from 'tweetnacl';
import * as util from 'tweetnacl-util';

/**
 * Encryption utilities for the XAAM platform.
 * Uses TweetNaCl.js for client-side encryption/decryption.
 */

/**
 * Generate a new key pair for asymmetric encryption.
 * 
 * @returns An object containing the public and private keys as base64 strings.
 */
export function generateKeyPair() {
  const keyPair = nacl.box.keyPair();
  return {
    publicKey: util.encodeBase64(keyPair.publicKey),
    privateKey: util.encodeBase64(keyPair.secretKey)
  };
}

/**
 * Encrypt data with a public key.
 * 
 * @param data - The data to encrypt (string or object)
 * @param publicKeyBase64 - The recipient's public key as a base64 string
 * @returns The encrypted data as a base64 string
 */
export function encryptWithPublicKey(data: any, publicKeyBase64: string): string {
  try {
    // Convert data to string if it's an object
    const dataStr = typeof data === 'object' ? JSON.stringify(data) : String(data);
    
    // Decode the public key from base64
    const publicKey = util.decodeBase64(publicKeyBase64);
    
    // Generate a one-time keypair for this encryption
    const ephemeralKeyPair = nacl.box.keyPair();
    
    // Generate a random nonce
    const nonce = nacl.randomBytes(nacl.box.nonceLength);
    
    // Convert the data to Uint8Array
    const messageUint8 = util.decodeUTF8(dataStr);
    
    // Encrypt the message
    const encryptedMessage = nacl.box(
      messageUint8,
      nonce,
      publicKey,
      ephemeralKeyPair.secretKey
    );
    
    // Combine the ephemeral public key, nonce, and encrypted message
    const fullMessage = new Uint8Array(ephemeralKeyPair.publicKey.length + nonce.length + encryptedMessage.length);
    fullMessage.set(ephemeralKeyPair.publicKey);
    fullMessage.set(nonce, ephemeralKeyPair.publicKey.length);
    fullMessage.set(encryptedMessage, ephemeralKeyPair.publicKey.length + nonce.length);
    
    // Encode the full message as base64
    return util.encodeBase64(fullMessage);
  } catch (error) {
    console.error('Encryption error:', error);
    throw new Error('Failed to encrypt data');
  }
}

/**
 * Decrypt data with a private key.
 * 
 * @param encryptedDataBase64 - The encrypted data as a base64 string
 * @param privateKeyBase64 - The recipient's private key as a base64 string
 * @returns The decrypted data
 */
export function decryptWithPrivateKey(encryptedDataBase64: string, privateKeyBase64: string): any {
  try {
    // Decode the encrypted data from base64
    const encryptedData = util.decodeBase64(encryptedDataBase64);
    
    // Decode the private key from base64
    const privateKey = util.decodeBase64(privateKeyBase64);
    
    // Extract the sender's public key, nonce, and encrypted message
    const publicKeyLength = nacl.box.publicKeyLength;
    const nonceLength = nacl.box.nonceLength;
    
    const senderPublicKey = encryptedData.slice(0, publicKeyLength);
    const nonce = encryptedData.slice(publicKeyLength, publicKeyLength + nonceLength);
    const message = encryptedData.slice(publicKeyLength + nonceLength);
    
    // Decrypt the message
    const decrypted = nacl.box.open(
      message,
      nonce,
      senderPublicKey,
      privateKey
    );
    
    if (!decrypted) {
      throw new Error('Decryption failed');
    }
    
    // Convert the decrypted message to a string
    const decryptedStr = util.encodeUTF8(decrypted);
    
    // Try to parse as JSON if possible
    try {
      return JSON.parse(decryptedStr);
    } catch {
      // Return as string if not valid JSON
      return decryptedStr;
    }
  } catch (error) {
    console.error('Decryption error:', error);
    throw new Error('Failed to decrypt data');
  }
}

/**
 * Encrypt a task payload for multiple judges.
 * 
 * @param payload - The task payload to encrypt
 * @param judgePublicKeys - Map of judge IDs to their public keys
 * @returns Object with encrypted payload and encrypted keys for each judge
 */
export function encryptTaskPayload(payload: any, judgePublicKeys: Record<string, string>) {
  try {
    // Generate a symmetric key for the payload
    const symmetricKey = nacl.randomBytes(nacl.secretbox.keyLength);
    
    // Generate a nonce for symmetric encryption
    const nonce = nacl.randomBytes(nacl.secretbox.nonceLength);
    
    // Convert payload to string and then to Uint8Array
    const payloadStr = JSON.stringify(payload);
    const payloadUint8 = util.decodeUTF8(payloadStr);
    
    // Encrypt the payload with the symmetric key
    const encryptedPayload = nacl.secretbox(payloadUint8, nonce, symmetricKey);
    
    // Combine nonce and encrypted payload
    const fullPayload = new Uint8Array(nonce.length + encryptedPayload.length);
    fullPayload.set(nonce);
    fullPayload.set(encryptedPayload, nonce.length);
    
    // Encrypt the symmetric key with each judge's public key
    const encryptedKeys: Record<string, string> = {};
    
    for (const [judgeId, publicKeyBase64] of Object.entries(judgePublicKeys)) {
      encryptedKeys[judgeId] = encryptWithPublicKey(
        util.encodeBase64(symmetricKey),
        publicKeyBase64
      );
    }
    
    return {
      encryptedPayload: util.encodeBase64(fullPayload),
      encryptedKeys
    };
  } catch (error) {
    console.error('Task encryption error:', error);
    throw new Error('Failed to encrypt task payload');
  }
}

/**
 * Decrypt a task payload.
 * 
 * @param encryptedPayloadBase64 - The encrypted payload as a base64 string
 * @param encryptedKeyBase64 - The encrypted symmetric key as a base64 string
 * @param privateKeyBase64 - The agent's private key as a base64 string
 * @returns The decrypted payload
 */
export function decryptTaskPayload(
  encryptedPayloadBase64: string,
  encryptedKeyBase64: string,
  privateKeyBase64: string
): any {
  try {
    // Decrypt the symmetric key
    const symmetricKeyBase64 = decryptWithPrivateKey(encryptedKeyBase64, privateKeyBase64);
    const symmetricKey = util.decodeBase64(symmetricKeyBase64);
    
    // Decode the encrypted payload
    const fullPayload = util.decodeBase64(encryptedPayloadBase64);
    
    // Extract nonce and encrypted data
    const nonceLength = nacl.secretbox.nonceLength;
    const nonce = fullPayload.slice(0, nonceLength);
    const encryptedData = fullPayload.slice(nonceLength);
    
    // Decrypt the payload
    const decrypted = nacl.secretbox.open(encryptedData, nonce, symmetricKey);
    
    if (!decrypted) {
      throw new Error('Payload decryption failed');
    }
    
    // Convert to string and parse as JSON
    const decryptedStr = util.encodeUTF8(decrypted);
    return JSON.parse(decryptedStr);
  } catch (error) {
    console.error('Task decryption error:', error);
    throw new Error('Failed to decrypt task payload');
  }
}

/**
 * Encrypt a deliverable for multiple judges.
 * 
 * @param deliverable - The deliverable to encrypt
 * @param judgePublicKeys - Map of judge IDs to their public keys
 * @returns Object with encrypted content and encrypted keys for each judge
 */
export function encryptDeliverable(deliverable: any, judgePublicKeys: Record<string, string>) {
  // This uses the same approach as encryptTaskPayload
  return encryptTaskPayload(deliverable, judgePublicKeys);
}

/**
 * Decrypt a deliverable.
 * 
 * @param encryptedContentBase64 - The encrypted content as a base64 string
 * @param encryptedKeyBase64 - The encrypted symmetric key as a base64 string
 * @param privateKeyBase64 - The judge's private key as a base64 string
 * @returns The decrypted deliverable
 */
export function decryptDeliverable(
  encryptedContentBase64: string,
  encryptedKeyBase64: string,
  privateKeyBase64: string
): any {
  // This uses the same approach as decryptTaskPayload
  return decryptTaskPayload(encryptedContentBase64, encryptedKeyBase64, privateKeyBase64);
}