import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, afterEach } from 'vitest';
import axios from 'axios';
import App from '../src/App.jsx';

afterEach(() => {
  vi.restoreAllMocks();
  window.location.hash = '';
});

describe('App Component', () => {

  it('renders connection test screen', () => {
    render(<App />);

    expect(screen.getByText(/Capstone MDA App/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Test Backend Connection/i })).toBeInTheDocument();
  });

  it('shows loading state when testing backend connection', () => {
    vi.spyOn(axios, 'get').mockReturnValue(new Promise(() => {}));

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /Test Backend Connection/i }));

    expect(screen.getByRole('button', { name: /Checking…/i })).toBeInTheDocument();
  });

  it('updates status when backend connection succeeds', async () => {
    vi.spyOn(axios, 'get').mockResolvedValue({ data: [] });

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /Test Backend Connection/i }));

    expect(await screen.findByText(/Connected to backend!/i)).toBeInTheDocument();
  });

  it('updates status when backend connection fails', async () => {
    vi.spyOn(axios, 'get').mockRejectedValue(new Error('Network Error'));

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /Test Backend Connection/i }));

    expect(await screen.findByText(/Failed: Network Error/i)).toBeInTheDocument();
  });

  it('navigates to main menu', async () => {
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Go to Main Menu/i }));
    fireEvent(window, new HashChangeEvent('hashchange'));

    expect(window.location.hash).toBe('#/main-menu');
    expect(await screen.findByRole('heading', { name: /Capstone MDA/i })).toBeInTheDocument();
  });

  it('renders main menu directly when hash is set', () => {
    window.location.hash = '#/main-menu';

    render(<App />);

    expect(screen.getByRole('heading', { name: /Capstone MDA/i })).toBeInTheDocument();
    expect(screen.getByText(/Project analysis/i)).toBeInTheDocument();
  });

  it('shows toast for unimplemented feature', async () => {
    window.location.hash = '#/main-menu';
    render(<App />);

    fireEvent.click(
      screen.getByRole('button', { name: /Summarize Contributor Projects/i })
    );

    expect(
      await screen.findByText(/Summarize Contributor Projects — coming soon/i)
    ).toBeInTheDocument();
  });

  it('navigates to Scan Project page', async () => {
    window.location.hash = '#/main-menu';
    render(<App />);
  
    fireEvent.click(screen.getByRole('button', { name: /Scan Project/i }));
    fireEvent(window, new HashChangeEvent('hashchange'));
  
    await screen.findByText(/Scan Project/i);
  });

  it('navigates to Resume page', async () => {
    window.location.hash = '#/main-menu';
    render(<App />);

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

    fireEvent.click(screen.getByRole('button', { name: /Rank Projects/i }));
    fireEvent(window, new HashChangeEvent('hashchange'));

    expect(window.location.hash).toBe('#/rank-projects');
    expect(await screen.findByRole('heading', { name: /Rank Projects/i })).toBeInTheDocument();
    expect(await screen.findByText(/No ranked projects found\./i)).toBeInTheDocument();
  });

  it('navigates to scanned projects page', async () => {
    window.location.hash = '#/main-menu';
    render(<App />);

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

    fireEvent.click(screen.getByRole('button', { name: /Manage Database/i }));
    fireEvent(window, new HashChangeEvent('hashchange'));

    expect(window.location.hash).toBe('#/database');
    expect(await screen.findByRole('heading', { name: /Database Management/i })).toBeInTheDocument();
    expect(await screen.findByText(/No tables found in database\./i)).toBeInTheDocument();
  });

});
