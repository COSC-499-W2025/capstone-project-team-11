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
});

// Portfolio Page Tests

// Helper function to generate mock projects with unique IDs and names
const mockProjects = (count) =>
  Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: `project-${i + 1}`,
    display_name: `Project ${i + 1}`,
    contributors: [{ name: 'alice' }, { name: 'bob' }],
  }));

  // Helper function to mock axios.get for both projects and contributors endpoints
const mockAxios = (projectCount) =>
  vi.spyOn(axios, 'get').mockImplementation((url) => {
    if (url.includes('/contributors')) return Promise.resolve({ data: ['alice', 'bob'] });
    return Promise.resolve({ data: mockProjects(projectCount) });
  });

  // Restore mocks after each test to prevent issues between tests (tearDown function)
afterEach(() => vi.restoreAllMocks());

// Test suite for PortfolioPage component
describe('PortfolioPage', () => {
  it('renders setup form heading', async () => {
    mockAxios(3);
    render(<PortfolioPage onBack={() => {}} />);
    expect(await screen.findByText(/Portfolio Setup/i)).toBeInTheDocument();
  });

  // Tests that the setup form shows an error message when fewer than 3 scanned projects are returned from the backend
  it('shows notice when fewer than 3 projects are scanned', async () => {
    mockAxios(2);
    render(<PortfolioPage onBack={() => {}} />);
    expect(await screen.findByText(/at least 3 scanned projects/i)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Generate Web Portfolio/i })).not.toBeInTheDocument();
  });

  // Tests that the setup form shows the "contributor select" dropdown and "generate portfolio" button when 3 or more scanned projects are returned from the backend
  it('shows contributor select when 3+ projects are loaded', async () => {
    mockAxios(3);
    render(<PortfolioPage onBack={() => {}} />);
    expect(await screen.findByRole('combobox')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Generate Web Portfolio/i })).toBeInTheDocument();
  });

  // Tests that the setup form shows an error message when the "generate portfolio" button is clicked without selecting a username from the dropdown
  it('shows error when generate clicked without selecting username', async () => {
    mockAxios(3);
    render(<PortfolioPage onBack={() => {}} />);
    await screen.findByRole('button', { name: /Generate Web Portfolio/i });
    fireEvent.click(screen.getByRole('button', { name: /Generate Web Portfolio/i }));
    expect(screen.getByText(/Please select a username/i)).toBeInTheDocument();
  });

  // Tests that the setup form shows an error message when the "generate portfolio" button is clicked with < 3 included projects
  it('shows error when too many projects are excluded', async () => {
    mockAxios(3);
    render(<PortfolioPage onBack={() => {}} />);
    await screen.findByRole('button', { name: /Generate Web Portfolio/i });

    // Select a username first
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'alice' } });

    // Uncheck all 3 projects (exclude them all)
    const checkboxes = screen.getAllByRole('checkbox');
    checkboxes.forEach((cb) => fireEvent.click(cb));

    fireEvent.click(screen.getByRole('button', { name: /Generate Web Portfolio/i }));
    expect(screen.getByText(/at least 3 projects/i)).toBeInTheDocument();
  });

  // Tests that the web portfolio is rendered successfully when the "generate portfolio" button is clicked with valid inputs (3+ projects, username selected)
  it('transitions to skeleton dashboard on valid submission', async () => {
    mockAxios(3);
    render(<PortfolioPage onBack={() => {}} />);
    await screen.findByRole('button', { name: /Generate Web Portfolio/i });

    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'alice' } });
    fireEvent.click(screen.getByRole('button', { name: /Generate Web Portfolio/i }));

    expect(await screen.findByText(/Web Portfolio/i)).toBeInTheDocument();
  });

  // Tests that all four portfolio section headings are rendered on the portfolio page
  it('renders all four dashboard section headings', async () => {
    mockAxios(3);
    render(<PortfolioPage onBack={() => {}} />);
    await screen.findByRole('button', { name: /Generate Web Portfolio/i });
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'alice' } });
    fireEvent.click(screen.getByRole('button', { name: /Generate Web Portfolio/i }));

    expect(await screen.findByText(/Activity Heatmap/i)).toBeInTheDocument();
    expect(screen.getByText(/Skills Timeline/i)).toBeInTheDocument();
    expect(screen.getByText(/Featured Projects/i)).toBeInTheDocument();
    expect(screen.getByText(/All Projects/i)).toBeInTheDocument();
  });

  // Tests that the "Back to Setup" button returns the user to the portfolio setup form
  it('back to setup button returns to setup form', async () => {
    mockAxios(3);
    render(<PortfolioPage onBack={() => {}} />);
    await screen.findByRole('button', { name: /Generate Web Portfolio/i });
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'alice' } });
    fireEvent.click(screen.getByRole('button', { name: /Generate Web Portfolio/i }));
    await screen.findByText(/Activity Heatmap/i);

    fireEvent.click(screen.getByRole('button', { name: /Back to Setup/i }));
    expect(await screen.findByText(/Portfolio Setup/i)).toBeInTheDocument();
  });
});
