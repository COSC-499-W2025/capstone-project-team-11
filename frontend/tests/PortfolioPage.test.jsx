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
  const getSpy = vi.spyOn(axios, 'get').mockImplementation((url, config = {}) => {
    if (url.includes('/web/portfolio/') && url.includes('/heatmap/project')) {
      const scope = config?.params?.view_scope || 'project';
      if (scope === 'user') {
        return Promise.resolve({
          data: {
            cells: [
              { period: '2026-01-05', value: 1 },
              { period: '2026-01-12', value: 2 },
            ],
            max_value: 2,
            range_start: '2026-01-05',
            range_end: '2026-01-12',
            value_unit: 'commits',
          },
        });
      }
      return Promise.resolve({
        data: {
          cells: [
            { period: '2026-01-05', value: 3 },
            { period: '2026-01-12', value: 5 },
          ],
          max_value: 5,
          range_start: '2026-01-05',
          range_end: '2026-01-12',
          value_unit: 'commits',
        },
      });
    }
    if (url.includes('/contributors')) return Promise.resolve({ data: ['alice', 'bob'] });
    if (url.includes('/rank-projects')) return Promise.resolve({ data: ranked });
    if (url.includes('/web/portfolio/') && url.includes('/showcase'))
      return Promise.resolve({ data: { projects: [] } });
    if (url.includes('/web/portfolio/') && url.includes('/heatmap'))
      return Promise.resolve({ data: { cells: [], max_value: 0 } });
    if (url.includes('/web/portfolio/') && url.includes('/timeline'))
      return Promise.resolve({ data: { timeline: [] } });
    if (url.includes('/portfolios/'))
      return Promise.resolve({
        data: {
          id: 42,
          included_project_ids: Array.from({ length: projectCount }, (_, i) => i + 1),
          created_at: new Date().toISOString(),
        },
      });
    if (/\/projects\/\d+/.test(url)) {
      return Promise.resolve({
        data: {
          project: { name: 'project-detail' },
          contributors: ['alice', 'bob'],
          contributor_roles: { contributors: [] },
          files_summary: { total_files: 0, extensions: {} },
          git_metrics: {},
          llm_summary: { text: 'summary' },
        },
      });
    }
    return Promise.resolve({ data: projects });
  });
  vi.spyOn(axios, 'post').mockImplementation((url) => {
    if (url.includes('/portfolios'))
      return Promise.resolve({ data: { id: 42, included_project_ids: [], created_at: new Date().toISOString() } });
    return Promise.resolve({ data: {} });
  });

  return { getSpy };
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

  it('loads project heatmap with project scope by default', async () => {
    const { getSpy } = mockAxios(3);
    render(<PortfolioPage onBack={() => {}} />);
    await screen.findByRole('button', { name: /Generate Web Portfolio/i });

    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'alice' } });
    await screen.findAllByRole('checkbox');
    fireEvent.click(screen.getByRole('button', { name: /Generate Web Portfolio/i }));
    await screen.findByText(/Activity Heatmap/i);

    const projectHeatmapCall = getSpy.mock.calls.find(([url]) =>
      String(url).includes('/web/portfolio/42/heatmap/project')
    );
    expect(projectHeatmapCall).toBeTruthy();
    expect(projectHeatmapCall?.[1]?.params?.view_scope).toBe('project');
  });

  it('switches to per user heatmap and requests user scope', async () => {
    const { getSpy } = mockAxios(3);
    render(<PortfolioPage onBack={() => {}} />);
    await screen.findByRole('button', { name: /Generate Web Portfolio/i });

    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'alice' } });
    await screen.findAllByRole('checkbox');
    fireEvent.click(screen.getByRole('button', { name: /Generate Web Portfolio/i }));
    await screen.findByText(/Activity Heatmap/i);

    fireEvent.click(screen.getByRole('button', { name: /Per User View/i }));
    expect(await screen.findAllByText(/commit\(s\)/i)).not.toHaveLength(0);

    const userHeatmapCall = getSpy.mock.calls.find(([url, config]) =>
      String(url).includes('/web/portfolio/42/heatmap/project')
      && config?.params?.view_scope === 'user'
    );
    expect(userHeatmapCall).toBeTruthy();
  });

  it('renders one shared horizontal scroll container for heatmap and date labels', async () => {
    mockAxios(3);
    const { container } = render(<PortfolioPage onBack={() => {}} />);
    await screen.findByRole('button', { name: /Generate Web Portfolio/i });

    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'alice' } });
    await screen.findAllByRole('checkbox');
    fireEvent.click(screen.getByRole('button', { name: /Generate Web Portfolio/i }));
    await screen.findByText(/Activity Heatmap/i);

    const sharedScroll = container.querySelector('.heatmap-scroll-wrap');
    expect(sharedScroll).toBeTruthy();
    expect(sharedScroll?.querySelector('.project-heatmap-grid')).toBeTruthy();
    expect(sharedScroll?.querySelector('.project-heatmap-weeks')).toBeTruthy();
  });

  it('Select All checks all included-project checkboxes', async () => {
    mockAxios(3);
    render(<PortfolioPage onBack={() => {}} />);

    fireEvent.change(await screen.findByRole('combobox'), { target: { value: 'alice' } });

    const projectOne = await screen.findByLabelText(/project-1/i);
    const projectTwo = screen.getByLabelText(/project-2/i);
    const projectThree = screen.getByLabelText(/project-3/i);

    fireEvent.click(projectOne);
    expect(projectOne).not.toBeChecked();

    fireEvent.click(screen.getByRole('button', { name: /^Select All$/i }));

    expect(projectOne).toBeChecked();
    expect(projectTwo).toBeChecked();
    expect(projectThree).toBeChecked();
  });

  it('Deselect All unchecks all included-project checkboxes', async () => {
    mockAxios(3);
    render(<PortfolioPage onBack={() => {}} />);

    fireEvent.change(await screen.findByRole('combobox'), { target: { value: 'alice' } });

    const projectOne = await screen.findByLabelText(/project-1/i);
    const projectTwo = screen.getByLabelText(/project-2/i);
    const projectThree = screen.getByLabelText(/project-3/i);

    fireEvent.click(screen.getByRole('button', { name: /^Deselect All$/i }));

    expect(projectOne).not.toBeChecked();
    expect(projectTwo).not.toBeChecked();
    expect(projectThree).not.toBeChecked();
  });

  it('individual included-project toggle still works after bulk selection controls exist', async () => {
    mockAxios(3);
    render(<PortfolioPage onBack={() => {}} />);

    fireEvent.change(await screen.findByRole('combobox'), { target: { value: 'alice' } });

    const projectOne = await screen.findByLabelText(/project-1/i);
    const projectTwo = screen.getByLabelText(/project-2/i);
    const projectThree = screen.getByLabelText(/project-3/i);

    fireEvent.click(projectTwo);

    expect(projectOne).toBeChecked();
    expect(projectTwo).not.toBeChecked();
    expect(projectThree).toBeChecked();
  });
});
