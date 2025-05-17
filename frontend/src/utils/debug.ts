/**
 * Debug utilities for testing wallet persistence
 */

import { walletStore } from '../stores/wallet';

/**
 * Set a mock wallet state for testing
 */
export function setMockWalletState() {
  // Create a mock wallet state
  const mockWalletState = {
    wallet: {
      address: '5YNmS1R9nNSCDzb5a7mMJ1dwK9uHeAAF4CmPEwKgVWr8',
      sol_balance: 14.90,
      usdc_balance: 0.00
    },
    connected: true,
    loading: false,
    error: null
  };
  
  // Save to localStorage
  localStorage.setItem('walletState', JSON.stringify(mockWalletState));
  
  // Update the wallet store
  walletStore.updateWalletInfo(mockWalletState.wallet);
  
  console.log('Mock wallet state set:', mockWalletState);
  
  return mockWalletState;
}

/**
 * Clear the wallet state
 */
export function clearWalletState() {
  localStorage.removeItem('walletState');
  console.log('Wallet state cleared');
}

/**
 * Get the current wallet state from localStorage
 */
export function getWalletStateFromStorage() {
  const savedState = localStorage.getItem('walletState');
  if (savedState) {
    try {
      return JSON.parse(savedState);
    } catch (e) {
      console.error('Failed to parse wallet state from localStorage:', e);
    }
  }
  return null;
}