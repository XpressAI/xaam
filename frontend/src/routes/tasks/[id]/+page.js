import { error } from '@sveltejs/kit';
import { api } from '$lib/api/client';

/** @type {import('./$types').PageLoad} */
export async function load({ params }) {
  try {
    // Get the task ID from the route params
    const taskId = params.id;
    
    // Fetch the task data
    const task = await api.tasks.getById(taskId);
    
    // Return the task data to the page
    return {
      task
    };
  } catch (err) {
    console.error('Error loading task:', err);
    throw error(404, {
      message: `Task not found: ${params.id}`
    });
  }
}