import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, afterEach } from 'vitest';
import axios from 'axios';
import App from '../src/App.jsx';

afterEach(() => {
  vi.restoreAllMocks();
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
});
