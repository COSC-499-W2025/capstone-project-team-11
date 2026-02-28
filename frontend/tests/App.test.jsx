import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, afterEach } from 'vitest';
import axios from 'axios';
import App from '../src/App.jsx';

afterEach(() => {
  vi.restoreAllMocks();
  window.location.hash = '';
});

describe('App Component', () => {
  it('renders initial UI', () => {
    render(<App />);
    expect(screen.getByText(/Capstone MDA App/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Test Backend Connection/i })).toBeInTheDocument();
    expect(screen.getByText(/Status: Not tested/i)).toBeInTheDocument();
  });

  it('shows loading state when button clicked', () => {
    vi.spyOn(axios, 'get').mockReturnValue(new Promise(() => {}));
    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /Test Backend Connection/i }));
    expect(screen.getByRole('button', { name: /Checking.../i })).toBeInTheDocument();
  });

  it('navigates to main menu when clicking Go to Main Menu', async () => {
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Go to Main Menu/i }));
    fireEvent(window, new HashChangeEvent('hashchange'));

    expect(window.location.hash).toBe('#/main-menu');
    expect(await screen.findByRole('heading', { name: /Capstone MDA Dashboard/i })).toBeInTheDocument();
    expect(screen.getByText(/Project analysis and portfolio generation toolkit/i)).toBeInTheDocument();
  });

  it('renders main menu directly when hash is set before render', () => {
    window.location.hash = '#/main-menu';

    render(<App />);

    expect(screen.getByRole('heading', { name: /Main Menu/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Back to Connection Test/i })).toBeInTheDocument();
  });

  it('navigates back to connection view from main menu', async () => {
    window.location.hash = '#/main-menu';
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Back to Connection Test/i }));
    fireEvent(window, new HashChangeEvent('hashchange'));

    expect(window.location.hash).toBe('');
    expect(await screen.findByText(/Capstone MDA App/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Test Backend Connection/i })).toBeInTheDocument();
  });

  it('updates status on successful backend connection', async () => {
    vi.spyOn(axios, 'get').mockResolvedValue({ data: [] });
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Test Backend Connection/i }));

    expect(await screen.findByText(/Status: Connected to backend!/i)).toBeInTheDocument();
  });

  it('updates status on failed backend connection', async () => {
    vi.spyOn(axios, 'get').mockRejectedValue(new Error('Network Error'));
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Test Backend Connection/i }));

    expect(await screen.findByText(/Status: Failed: Network Error/i)).toBeInTheDocument();
  });
});
