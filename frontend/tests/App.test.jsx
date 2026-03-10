import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, afterEach } from 'vitest';
import axios from 'axios';
import App from '../src/App.jsx';
import PortfolioPage from '../src/PortfolioPage.jsx';

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

  it('shows resume page and highlights sidebar item when clicked', async () => {
    window.location.hash = '#/main-menu';
    render(<App />);

    const resumeButton = screen.getByRole('button', { name: /Generate Resume/i });
    fireEvent.click(resumeButton);

    expect(
      await screen.findByText(/Create a contributor-focused resume from project data\./i)
    ).toBeInTheDocument();

    expect(resumeButton.className).toMatch(/is-active/);
  });

  it('navigates to Rank Projects from main menu', async () => {
    window.location.hash = '#/main-menu';
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Rank Projects/i }));
    fireEvent(window, new HashChangeEvent('hashchange'));

    expect(window.location.hash).toBe('#/rank-projects');
    expect(
      await screen.findByRole('heading', { name: /Rank Projects/i })
    ).toBeInTheDocument();
  });

  it('returns to main menu from Rank Projects page', async () => {
    window.location.hash = '#/main-menu';
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Rank Projects/i }));
    fireEvent(window, new HashChangeEvent('hashchange'));
    fireEvent.click(await screen.findByRole('button', { name: /Back to Main Menu/i }));
    fireEvent(window, new HashChangeEvent('hashchange'));

    expect(window.location.hash).toBe('#/main-menu');
    expect(
      await screen.findByRole('heading', { name: /Capstone MDA Dashboard/i })
    ).toBeInTheDocument();
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

    window.location.hash = '#/main-menu';
    render(<App />);

    const resumeButton = screen.getByRole('button', { name: /Generate Resume/i });
    fireEvent.click(resumeButton);

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
    vi.spyOn(axios, 'get').mockResolvedValue({ data: [{ id: 1, name: 'Test Project' }] });

    window.location.hash = '#/main-menu';
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Summarize Contributor Projects/i }));

    expect(await screen.findByText(/Summarize Contributor Projects clicked \(coming soon\)/i)).toBeInTheDocument();

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

// Portfolio Page Tests

const mockProjects = (count) =>
  Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: `project-${i + 1}`,
    display_name: `Project ${i + 1}`,
    contributors: [{ name: 'alice' }, { name: 'bob' }],
  }));

const mockAxios = (projectCount) => {
  const projects = mockProjects(projectCount);
  const ranked = projects.map((p) => ({ project: p.name }));
  vi.spyOn(axios, 'get').mockImplementation((url) => {
    if (url.includes('/contributors')) return Promise.resolve({ data: ['alice', 'bob'] });
    if (url.includes('/rank-projects')) return Promise.resolve({ data: ranked });
    if (url.includes('/web/portfolio/') && url.includes('/showcase'))
      return Promise.resolve({ data: { projects: [] } });
    if (url.includes('/web/portfolio/') && url.includes('/heatmap'))
      return Promise.resolve({ data: { cells: [], max_value: 0 } });
    if (url.includes('/web/portfolio/') && url.includes('/timeline'))
      return Promise.resolve({ data: { timeline: [] } });
    if (url.includes('/portfolio/'))
      return Promise.resolve({ data: { metadata: { project_count: projectCount }, generated_at: new Date().toISOString() } });
    return Promise.resolve({ data: projects });
  });
  vi.spyOn(axios, 'post').mockImplementation((url) => {
    if (url.includes('/portfolio/generate'))
      return Promise.resolve({ data: { portfolio_id: 42 } });
    return Promise.resolve({ data: {} });
  });
};

afterEach(() => vi.restoreAllMocks());

describe('PortfolioPage', () => {
  it('renders setup form heading', async () => {
    mockAxios(3);
    render(<PortfolioPage onBack={() => {}} />);
    expect(await screen.findByText(/Portfolio Setup/i)).toBeInTheDocument();
  });

  it('shows notice when fewer than 3 projects are scanned', async () => {
    mockAxios(2);
    render(<PortfolioPage onBack={() => {}} />);
    expect(await screen.findByText(/at least 3 scanned projects/i)).toBeInTheDocument();
    expect(
      screen.queryByRole('button', { name: /Generate Web Portfolio/i })
    ).not.toBeInTheDocument();
  });

  it('shows contributor select when 3+ projects are loaded', async () => {
    mockAxios(3);
    render(<PortfolioPage onBack={() => {}} />);
    expect(await screen.findByRole('combobox')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Generate Web Portfolio/i })).toBeInTheDocument();
  });

  it('shows error when generate clicked without selecting username', async () => {
    mockAxios(3);
    render(<PortfolioPage onBack={() => {}} />);
    await screen.findByRole('button', { name: /Generate Web Portfolio/i });
    fireEvent.click(screen.getByRole('button', { name: /Generate Web Portfolio/i }));
    expect(screen.getByText(/Please select a username/i)).toBeInTheDocument();
  });

  it('shows error when too many projects are excluded', async () => {
    mockAxios(3);
    render(<PortfolioPage onBack={() => {}} />);
    await screen.findByRole('button', { name: /Generate Web Portfolio/i });

    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'alice' } });

    const checkboxes = await screen.findAllByRole('checkbox');
    checkboxes.forEach((cb) => fireEvent.click(cb));

    fireEvent.click(screen.getByRole('button', { name: /Generate Web Portfolio/i }));
    expect(screen.getByText(/at least 3 projects/i)).toBeInTheDocument();
  });

  it('transitions to skeleton dashboard on valid submission', async () => {
    mockAxios(3);
    render(<PortfolioPage onBack={() => {}} />);
    await screen.findByRole('button', { name: /Generate Web Portfolio/i });

    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'alice' } });
    await screen.findAllByRole('checkbox');
    fireEvent.click(screen.getByRole('button', { name: /Generate Web Portfolio/i }));

    expect(await screen.findByRole('heading', { name: /Web Portfolio/i })).toBeInTheDocument();
  });

  it('renders all four dashboard section headings', async () => {
    mockAxios(3);
    render(<PortfolioPage onBack={() => {}} />);
    await screen.findByRole('button', { name: /Generate Web Portfolio/i });
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'alice' } });
    await screen.findAllByRole('checkbox');
    fireEvent.click(screen.getByRole('button', { name: /Generate Web Portfolio/i }));

    expect(await screen.findByText(/Activity Heatmap/i)).toBeInTheDocument();
    expect(screen.getByText(/Skills Timeline/i)).toBeInTheDocument();
    expect(screen.getByText(/Featured Projects/i)).toBeInTheDocument();
    expect(screen.getByText(/All Projects/i)).toBeInTheDocument();
  });

  it('back to setup button returns to setup form', async () => {
    mockAxios(3);
    render(<PortfolioPage onBack={() => {}} />);
    await screen.findByRole('button', { name: /Generate Web Portfolio/i });
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'alice' } });
    await screen.findAllByRole('checkbox');
    fireEvent.click(screen.getByRole('button', { name: /Generate Web Portfolio/i }));
    await screen.findByText(/Activity Heatmap/i);

    fireEvent.click(screen.getByRole('button', { name: /Back to Setup/i }));
    expect(await screen.findByText(/Portfolio Setup/i)).toBeInTheDocument();
  });
});