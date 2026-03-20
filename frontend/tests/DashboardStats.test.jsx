import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, afterEach, beforeEach } from 'vitest';
import App from '../src/App.jsx';

describe('Dashboard Stats', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation((url) => {
      if (url.includes('/config')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ data_consent: true }),
        });
      }
      if (url.includes('/stats/dashboard')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            projects: { count: 3, latest_project: 'my-app', latest_scan: '2026-03-20T13:00:00Z' },
            contributors: { count: 5, top_contributor: 'alice_dev', top_contributor_files: 42 },
            outputs: { resumes: 2, portfolios: 1, total: 3, latest_generated: '2026-03-19T10:00:00Z' },
          }),
        });
      }
      return Promise.resolve({ ok: true, json: async () => ({}) });
    }));
  });

  afterEach(() => {
    vi.restoreAllMocks();
    window.location.hash = '';
  });

  it('fetches and displays dashboard stats on mount', async () => {
    window.location.hash = '#/main-menu';
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText('Scanned Projects')).toBeInTheDocument();
      expect(screen.getByText('Contributors')).toBeInTheDocument();
      expect(screen.getByText('Generated Outputs')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('displays latest project and contributor info', async () => {
    window.location.hash = '#/main-menu';
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/my-app/)).toBeInTheDocument();
      expect(screen.getByText(/alice_dev/)).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('displays outputs breakdown', async () => {
    window.location.hash = '#/main-menu';
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/2 resumes/)).toBeInTheDocument();
      expect(screen.getByText(/1 portfolio/)).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('handles fetch errors without crashing', async () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation((url) => {
      if (url.includes('/config')) {
        return Promise.resolve({ ok: true, json: async () => ({ data_consent: true }) });
      }
      return Promise.reject(new Error('Network error'));
    }));

    window.location.hash = '#/main-menu';
    render(<App />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /Capstone MDA/i })).toBeInTheDocument();
    }, { timeout: 3000 });
  });
});


