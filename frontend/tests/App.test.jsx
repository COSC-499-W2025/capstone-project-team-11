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
    expect(
      await screen.findByRole('heading', { name: /Capstone MDA Dashboard/i })
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Project analysis and portfolio generation toolkit/i)
    ).toBeInTheDocument();
  });

  it('renders main menu directly when hash is set before render', () => {
    window.location.hash = '#/main-menu';

    render(<App />);

    expect(screen.getByRole('heading', { name: /Main Menu/i })).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /Back to Connection Test/i })
    ).toBeInTheDocument();
  });

  it('navigates back to connection view from main menu', async () => {
    window.location.hash = '#/main-menu';
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Back to Connection Test/i }));
    fireEvent(window, new HashChangeEvent('hashchange'));

    expect(window.location.hash).toBe('');
    expect(await screen.findByText(/Capstone MDA App/i)).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /Test Backend Connection/i })
    ).toBeInTheDocument();
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

  it('shows toast and highlights sidebar item when clicked', async () => {
    window.location.hash = '#/main-menu';
    render(<App />);

    const resumeButton = screen.getByRole('button', { name: /Generate Resume/i });
    fireEvent.click(resumeButton);

    expect(
      await screen.findByText(/Generate Resume clicked \(coming soon\)/i)
    ).toBeInTheDocument();

    expect(resumeButton.className).toMatch(/is-active/);
  });

  it('navigates to scanned projects page when clicking View/Manage Scanned Projects', async () => {
    vi.spyOn(axios, 'get')
      .mockResolvedValueOnce({
        data: [{ id: 1, name: 'Test Project' }],
      })
      .mockResolvedValueOnce({
        data: {
          project: {
            id: 1,
            name: 'Test Project',
            created_at: '2026-03-06 12:00:00',
            repo_url: null,
            thumbnail_path: null,
          },
          skills: [],
          languages: [],
          contributors: [],
          scans: [],
          files_summary: { total_files: 0, extensions: {} },
          evidence: [],
        },
      });

    // Button should have active class
    expect(resumeButton.className).toMatch(/is-active/);
  });

  it('navigates to Rank Projects from main menu', async () => {
    window.location.hash = '#/main-menu';
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Rank Projects/i }));
    fireEvent(window, new HashChangeEvent('hashchange'));

    expect(window.location.hash).toBe('#/rank-projects');
    expect(await screen.findByRole('heading', { name: /Rank Projects/i })).toBeInTheDocument();
  });

  it('returns to main menu from Rank Projects page', async () => {
    window.location.hash = '#/main-menu';
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Rank Projects/i }));
    fireEvent(window, new HashChangeEvent('hashchange'));
    fireEvent.click(await screen.findByRole('button', { name: /Back to Main Menu/i }));
    fireEvent(window, new HashChangeEvent('hashchange'));

    expect(window.location.hash).toBe('#/main-menu');
    expect(await screen.findByRole('heading', { name: /Capstone MDA Dashboard/i })).toBeInTheDocument();
  });

  it('shows coming soon toast for unimplemented menu actions', async () => {
    window.location.hash = '#/main-menu';
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Generate Portfolio/i }));

    expect(await screen.findByText(/Generate Portfolio clicked \(coming soon\)/i)).toBeInTheDocument();
    window.location.hash = '#/main-menu';
    render(<App />);

    const manageButton = screen.getByRole('button', {
      name: /View\/Manage Scanned Projects/i,
    });

    fireEvent.click(manageButton);
    fireEvent(window, new HashChangeEvent('hashchange'));

    expect(window.location.hash).toBe('#/projects');
    expect(
      await screen.findByRole('heading', { name: /Scanned Projects/i })
    ).toBeInTheDocument();
    expect(await screen.findByText(/Test Project/i)).toBeInTheDocument();
  });

  // ==========================
  // NEW: Tests for Database Maintenance
  // ==========================

  it('navigates to Database Maintenance page from main menu', async () => {
    window.location.hash = '#/main-menu';
    render(<App />);

    // Find the Manage Database button (using the title span to avoid duplicate buttons)
    const manageDbButton = screen.getAllByText('Manage Database').find(
      el => el.tagName === 'SPAN'
    ).parentElement; // get the button element itself

    fireEvent.click(manageDbButton);
    fireEvent(window, new HashChangeEvent('hashchange'));

    expect(window.location.hash).toBe('#/database');

    // Match the correct header text on the database page
    expect(await screen.findByRole('heading', { name: /Database Management/i })).toBeInTheDocument();
  });

  it('returns to main menu from Database Maintenance page', async () => {
    window.location.hash = '#/database';
    render(<App />);

    // Click the back button in database page
    const backButton = screen.getByRole('button', { name: /Back to Main Menu/i });
    fireEvent.click(backButton);
    fireEvent(window, new HashChangeEvent('hashchange'));

    expect(window.location.hash).toBe('#/main-menu');
    expect(await screen.findByRole('heading', { name: /Capstone MDA Dashboard/i })).toBeInTheDocument();
  });
});