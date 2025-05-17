import './app.css';
import App from './App.svelte';

// Protocol compliance check
function checkProtocolCompliance() {
  const whitepaper_read = import.meta.env.VITE_XAAM_WHITEPAPER_READ === 'true';
  
  if (!whitepaper_read) {
    const warningMessage = `
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║                               WARNING                                      ║
    ║                                                                            ║
    ║  You MUST read the XAAM Protocol Whitepaper before proceeding with         ║
    ║  implementation. The whitepaper contains the definitive protocol           ║
    ║  specification that all implementations must adhere to.                    ║
    ║                                                                            ║
    ║  To acknowledge that you have read and understood the whitepaper,          ║
    ║  set the VITE_XAAM_WHITEPAPER_READ environment variable to "true"          ║
    ║  in your .env file.                                                        ║
    ║                                                                            ║
    ║  Example:                                                                  ║
    ║    VITE_XAAM_WHITEPAPER_READ=true                                          ║
    ║                                                                            ║
    ║  The whitepaper can be found at: XAAM_Whitepaper.md                        ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    `;
    
    console.warn(warningMessage);
    
    // In production, you might want to show a modal or prevent the app from loading
    if (import.meta.env.PROD) {
      // Display a more prominent warning in production
      document.body.innerHTML = `
        <div style="font-family: monospace; padding: 20px; background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; border-radius: 5px; margin: 20px; white-space: pre-wrap;">
          ${warningMessage}
        </div>
      `;
      throw new Error('XAAM Protocol Whitepaper must be read before running in production');
    }
  } else {
    console.info('XAAM Protocol Whitepaper compliance check passed');
  }
}

// Run protocol compliance check
checkProtocolCompliance();

// Create and mount the app
const app = new App({
  target: document.getElementById('app') as HTMLElement,
});

export default app;