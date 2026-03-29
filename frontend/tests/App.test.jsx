import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, afterEach, beforeEach } from 'vitest';
import axios from 'axios';
import App from '../src/App.jsx';

beforeEach(() => {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockImplementation((url) => {
      const isConfig = typeof url === 'string' && url.endsWith('/config');
      return Promise.resolve({
        ok: true,
        json: async () => (isConfig ? { data_consent: true } : []),
      });
    })
  );
});

afterEach(() => {
  vi.restoreAllMocks();
  window.location.hash = '';
});

describe('App Component', () => {

  it('renders main menu after consent is granted', async () => {
    render(<App />);

    expect(await screen.findByRole('heading', { name: /GitHired/i })).toBeInTheDocument();
    expect(await screen.findByText(/Project analysis/i)).toBeInTheDocument();
  });

  it('shows loading state when testing backend connection', async () => {
    vi.spyOn(axios, 'get').mockReturnValue(new Promise(() => {}));

    window.location.hash = '#/main-menu';
    render(<App />);
    await screen.findByRole('heading', { name: /GitHired/i });

    fireEvent.click(screen.getByRole('button', { name: /Check Connection/i }));

    expect(screen.getByRole('button', { name: /Checking…/i })).toBeInTheDocument();
  });

  it('updates status when backend connection succeeds', async () => {
    vi.spyOn(axios, 'get').mockResolvedValue({ data: [] });

    window.location.hash = '#/main-menu';
    render(<App />);
    await screen.findByRole('heading', { name: /GitHired/i });

    fireEvent.click(screen.getByRole('button', { name: /Check Connection/i }));

    expect(await screen.findByText(/✓/)).toBeInTheDocument();
  });

  it('updates status when backend connection fails', async () => {
    vi.spyOn(axios, 'get').mockRejectedValue(new Error('Network Error'));

    window.location.hash = '#/main-menu';
    render(<App />);
    await screen.findByRole('heading', { name: /GitHired/i });

    fireEvent.click(screen.getByRole('button', { name: /Check Connection/i }));

    expect(await screen.findByText(/✗/)).toBeInTheDocument();
  });

  it('renders main menu directly when hash is set', async () => {
    window.location.hash = '#/main-menu';

    render(<App />);

    expect(await screen.findByRole('heading', { name: /GitHired/i })).toBeInTheDocument();
    expect(await screen.findByText(/Project analysis/i)).toBeInTheDocument();
  });

  it('navigates to Scan Project page', async () => {
    window.location.hash = '#/main-menu';
    render(<App />);
    await screen.findByRole('heading', { name: /GitHired/i });

    fireEvent.click(screen.getByRole('button', { name: /Scan Project/i }));
    fireEvent(window, new HashChangeEvent('hashchange'));

    await screen.findByText(/Scan Project/i);
  });

  it('navigates to Resume page', async () => {
    window.location.hash = '#/main-menu';
    render(<App />);
    await screen.findByRole('heading', { name: /GitHired/i });

    fireEvent.click(screen.getByRole('button', { name: /Generate Resume/i }));
    fireEvent(window, new HashChangeEvent('hashchange'));

    expect(window.location.hash).toBe('#/resume');
    expect(await screen.findByRole('heading', { name: /Generate Resume/i })).toBeInTheDocument();
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('http://127.0.0.1:8000/contributors');
    });
  });

  it('navigates to Rank Projects page', async () => {
    window.location.hash = '#/main-menu';
    render(<App />);
    await screen.findByRole('heading', { name: /GitHired/i });

    fireEvent.click(screen.getByRole('button', { name: /Rank Projects/i }));
    fireEvent(window, new HashChangeEvent('hashchange'));

    expect(window.location.hash).toBe('#/rank-projects');
    expect(await screen.findByRole('heading', { name: /Rank Projects/i })).toBeInTheDocument();
    expect(await screen.findByText(/No ranked projects found\./i)).toBeInTheDocument();
  });

  it('navigates to scanned projects page', async () => {
    window.location.hash = '#/main-menu';
    render(<App />);
    await screen.findByRole('heading', { name: /GitHired/i });

    fireEvent.click(
      screen.getByRole('button', { name: /View\/Manage Scanned Projects/i })
    );

    fireEvent(window, new HashChangeEvent('hashchange'));

    expect(window.location.hash).toBe('#/projects');
    expect(await screen.findByRole('heading', { name: /Scanned Projects/i })).toBeInTheDocument();
    expect(await screen.findByText(/No scanned projects yet/i)).toBeInTheDocument();
  });

  it('navigates to database maintenance page', async () => {
    window.location.hash = '#/main-menu';
    render(<App />);
    await screen.findByRole('heading', { name: /GitHired/i });

    fireEvent.click(screen.getByRole('button', { name: /Manage Database/i }));
    fireEvent(window, new HashChangeEvent('hashchange'));

    expect(window.location.hash).toBe('#/database');
    expect(await screen.findByRole('heading', { name: /Database Management/i })).toBeInTheDocument();
    const projectsToggle = await screen.findByRole('button', { name: /Projects/i }); 
    fireEvent.click(projectsToggle);
    expect(await screen.findByText(/No data/i)).toBeInTheDocument();
  });

});
