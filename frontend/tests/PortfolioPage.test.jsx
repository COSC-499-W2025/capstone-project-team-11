import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, afterEach } from 'vitest';
import axios from 'axios';
import PortfolioPage from '../src/PortfolioPage.jsx';

afterEach(() => {
  vi.restoreAllMocks();
});

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
      return Promise.resolve({
        data: {
          metadata: { project_count: projectCount },
          generated_at: new Date().toISOString(),
        },
      });
    return Promise.resolve({ data: projects });
  });
  vi.spyOn(axios, 'post').mockImplementation((url) => {
    if (url.includes('/portfolio/generate'))
      return Promise.resolve({ data: { portfolio_id: 42 } });
    return Promise.resolve({ data: {} });
  });
};

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
    expect(
      screen.getByRole('button', { name: /Generate Web Portfolio/i })
    ).toBeInTheDocument();
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
