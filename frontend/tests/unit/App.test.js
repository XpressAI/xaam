import { render, screen } from '@testing-library/svelte';
import { describe, it, expect, beforeEach } from 'vitest';
import App from '../../src/App.svelte';

describe('App Component', () => {
  beforeEach(() => {
    // Reset any mocks or state before each test
  });

  it('renders the XAAM title', () => {
    render(App);
    expect(screen.getByText('XAAM')).toBeTruthy();
  });

  it('renders the subtitle', () => {
    render(App);
    expect(screen.getByText('Xpress AI Agent Marketplace')).toBeTruthy();
  });

  it('renders the welcome section', () => {
    render(App);
    expect(screen.getByText('Welcome to XAAM')).toBeTruthy();
  });

  it('renders the three main feature cards', () => {
    render(App);
    expect(screen.getByText('Create Tasks')).toBeTruthy();
    expect(screen.getByText('Work on Tasks')).toBeTruthy();
    expect(screen.getByText('Judge Submissions')).toBeTruthy();
  });

  it('initially shows loading state and then content', async () => {
    // Mock the loading state
    vi.mock('svelte', async () => {
      const actual = await vi.importActual('svelte');
      return {
        ...actual,
        onMount: (callback) => {
          // Delay the callback to simulate loading
          setTimeout(callback, 100);
        },
      };
    });

    const { container } = render(App);
    
    // Initially should show loading
    expect(screen.getByText('Loading XAAM...')).toBeTruthy();
    
    // After a delay, should show content
    await new Promise(resolve => setTimeout(resolve, 200));
    expect(screen.queryByText('Loading XAAM...')).toBeFalsy();
    expect(screen.getByText('XAAM')).toBeTruthy();
  });

  it('has the correct structure with header and sections', () => {
    const { container } = render(App);
    
    // Check for main container
    expect(container.querySelector('main')).toBeTruthy();
    
    // Check for header
    expect(container.querySelector('header')).toBeTruthy();
    
    // Check for sections
    const sections = container.querySelectorAll('section');
    expect(sections.length).toBeGreaterThanOrEqual(2);
  });

  it('has the correct number of feature cards', () => {
    const { container } = render(App);
    
    // Find the grid section
    const gridSection = Array.from(container.querySelectorAll('section')).find(
      section => section.classList.contains('grid')
    );
    
    // Check for three cards
    expect(gridSection.querySelectorAll('.bg-card').length).toBe(3);
  });
});