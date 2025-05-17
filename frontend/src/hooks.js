// This file handles client-side setup for SvelteKit
// It's used to set up any client-side libraries or configuration

/** @type {import('@sveltejs/kit').Handle} */
export async function handle({ event, resolve }) {
  // You can modify the request here
  
  // Pass the request to the default handler
  const response = await resolve(event);
  
  // You can modify the response here
  
  return response;
}

// Handle client-side errors
/** @type {import('@sveltejs/kit').HandleClientError} */
export function handleError({ error, event }) {
  console.error('Client error:', error);
  
  // Return the error to be displayed in the UI
  return {
    message: error.message || 'An unexpected error occurred',
    code: error.code || 'UNKNOWN'
  };
}