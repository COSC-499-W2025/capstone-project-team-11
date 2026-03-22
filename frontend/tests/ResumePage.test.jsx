import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import ResumePage from '../src/ResumePage.jsx';
import { API_BASE_URL } from '../src/api.js';

const mockMountFetches = () =>
  vi.spyOn(global, 'fetch')
    .mockResolvedValueOnce({ ok: true, json: async () => [] })
    .mockResolvedValueOnce({ ok: true, json: async () => ({}) })
    .mockResolvedValueOnce({ ok: true, json: async () => [] });

afterEach(() => {
  vi.restoreAllMocks();
});

describe('ResumePage', () => {
  it('renders contributor select and generate button', async () => {
    mockMountFetches();
    render(<ResumePage />);
    expect(screen.getByText(/Select Contributor/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Generate Resume/i })).toBeInTheDocument();
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('http://127.0.0.1:8000/contributors');
    });
  });

  it('shows generating state when generate is clicked', async () => {
    mockMountFetches();
    vi.spyOn(global, 'fetch').mockReturnValue(new Promise(() => {}));
    render(<ResumePage />);
    fireEvent.click(screen.getByRole('button', { name: /Generate Resume/i }));
    expect(await screen.findByRole('button', { name: /Generating/i })).toBeDisabled();
  });

  it('shows resume content when API calls succeed', async () => {
    vi.spyOn(global, 'fetch')
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => ({}) })
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ resume_id: 42, resume_path: '/tmp/resume.md', generated_at: '2026-03-07' }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          id: 42,
          username: 'alice',
          resume_path: '/tmp/resume.md',
          content: '# Alice Resume\n- Built key features',
          generated_at: '2026-03-07',
          metadata: {},
        }),
      })
      .mockResolvedValueOnce({ ok: true, json: async () => [] });

    render(<ResumePage />);
    fireEvent.click(screen.getByRole('button', { name: /Generate Resume/i }));

    expect(await screen.findByText(/Generated Resume/i)).toBeInTheDocument();
    expect(screen.getByText(/Alice Resume/i)).toBeInTheDocument();
    expect(global.fetch).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/resume/generate',
      expect.objectContaining({ method: 'POST' }),
    );
    expect(global.fetch).toHaveBeenCalledWith('http://127.0.0.1:8000/resume/42');
  });

  it('shows error message when API call fails', async () => {
    vi.spyOn(global, 'fetch')
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => ({}) })
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockRejectedValueOnce(new Error('Network failure'));

    render(<ResumePage />);
    fireEvent.click(screen.getByRole('button', { name: /Generate Resume/i }));

    await waitFor(() => {
      expect(screen.getByText(/Network failure/i)).toBeInTheDocument();
    });
  });
});

describe('ResumePage project selection', () => {
  const projects = [
    { id: 1, name: 'project-1', custom_name: 'Project 1' },
    { id: 2, name: 'project-2', custom_name: 'Project 2' },
    { id: 3, name: 'project-3', custom_name: 'Project 3' },
  ];
  const contributors = ['alice', 'bob'];
  const rankedProjects = projects.map((project) => ({ project: project.name }));

  const mockProjectSelectionFetch = () =>
    vi.spyOn(global, 'fetch').mockImplementation((url) => {
      const requestUrl = String(url);

      if (requestUrl === `${API_BASE_URL}/contributors`) {
        return Promise.resolve({ ok: true, json: async () => contributors });
      }
      if (requestUrl === `${API_BASE_URL}/projects`) {
        return Promise.resolve({ ok: true, json: async () => projects });
      }
      if (requestUrl === `${API_BASE_URL}/rank-projects?mode=contributor&contributor_name=alice`) {
        return Promise.resolve({ ok: true, json: async () => rankedProjects });
      }
      if (requestUrl === `${API_BASE_URL}/resume/generate`) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ resume_id: 42, resume_path: '/tmp/resume.md', generated_at: '2026-03-07' }),
        });
      }
      if (requestUrl === `${API_BASE_URL}/resume/42`) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            id: 42,
            username: 'alice',
            resume_path: '/tmp/resume.md',
            content: '# Alice Resume\n- Built key features',
            generated_at: '2026-03-07',
            metadata: {},
          }),
        });
      }

      return Promise.resolve({ ok: false, json: async () => ({}) });
    });

  it('loads the project checklist after selecting a contributor', async () => {
    mockProjectSelectionFetch();
    render(<ResumePage />);

    fireEvent.change(await screen.findByRole('combobox'), { target: { value: 'alice' } });

    expect(await screen.findByText(/Included Projects/i)).toBeInTheDocument();
    expect(await screen.findByLabelText(/Project 1/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Project 2/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Project 3/i)).toBeInTheDocument();
  });

  it('Select All and Deselect All update all resume project checkboxes', async () => {
    mockProjectSelectionFetch();
    render(<ResumePage />);

    fireEvent.change(await screen.findByRole('combobox'), { target: { value: 'alice' } });

    const projectOne = await screen.findByLabelText(/Project 1/i);
    const projectTwo = screen.getByLabelText(/Project 2/i);
    const projectThree = screen.getByLabelText(/Project 3/i);

    fireEvent.click(screen.getByRole('button', { name: /^Deselect All$/i }));
    expect(projectOne).not.toBeChecked();
    expect(projectTwo).not.toBeChecked();
    expect(projectThree).not.toBeChecked();

    fireEvent.click(screen.getByRole('button', { name: /^Select All$/i }));
    expect(projectOne).toBeChecked();
    expect(projectTwo).toBeChecked();
    expect(projectThree).toBeChecked();
  });

  it('sends excluded_project_names in the resume generate request body', async () => {
    const fetchSpy = mockProjectSelectionFetch();
    render(<ResumePage />);

    fireEvent.change(await screen.findByRole('combobox'), { target: { value: 'alice' } });

    const projectTwo = await screen.findByLabelText(/Project 2/i);
    fireEvent.click(projectTwo);
    expect(projectTwo).not.toBeChecked();

    fireEvent.click(screen.getByRole('button', { name: /Generate Resume/i }));

    await screen.findByText(/Generated Resume/i);

    const generateCall = fetchSpy.mock.calls.find(([url]) => String(url) === `${API_BASE_URL}/resume/generate`);
    expect(generateCall).toBeTruthy();

    const requestBody = JSON.parse(generateCall[1].body);
    expect(requestBody).toMatchObject({
      username: 'alice',
      save_to_db: true,
      llm_summary: false,
      excluded_project_names: ['project-2'],
    });
  });
});
