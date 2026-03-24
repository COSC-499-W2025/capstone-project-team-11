import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import ResumePage from '../src/ResumePage.jsx';

const mockMountFetches = () =>
  vi.spyOn(global, 'fetch')
    .mockResolvedValueOnce({ ok: true, json: async () => [] })
    .mockResolvedValueOnce({ ok: true, json: async () => ({}) })
    .mockResolvedValueOnce({ ok: true, json: async () => [] })
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

  it('shows error message when API call fails', async () => {
    vi.spyOn(global, 'fetch')
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => ({}) })
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockRejectedValueOnce(new Error('Network failure'));

    render(<ResumePage />);
    fireEvent.click(screen.getByRole('button', { name: /Generate Resume/i }));

    await waitFor(() => {
      expect(screen.getByText(/Network failure/i)).toBeInTheDocument();
    });
  });

  it('select all and deselect all update the resume project checkboxes', async () => {
    vi.spyOn(global, 'fetch').mockImplementation((url) => {
      const requestUrl = String(url);

      if (requestUrl === 'http://127.0.0.1:8000/contributors') {
        return Promise.resolve({ ok: true, json: async () => ['alice'] });
      }
      if (requestUrl === 'http://127.0.0.1:8000/config') {
        return Promise.resolve({ ok: true, json: async () => ({}) });
      }
      if (requestUrl === 'http://127.0.0.1:8000/projects') {
        return Promise.resolve({
          ok: true,
          json: async () => [
            { id: 1, name: 'project-1', custom_name: 'Project 1' },
            { id: 2, name: 'project-2', custom_name: 'Project 2' },
            { id: 3, name: 'project-3', custom_name: 'Project 3' },
          ],
        });
      }
      if (requestUrl === 'http://127.0.0.1:8000/resumes' || requestUrl === 'http://127.0.0.1:8000/resumes?username=alice') {
        return Promise.resolve({ ok: true, json: async () => [] });
      }
      if (requestUrl === 'http://127.0.0.1:8000/rank-projects?mode=contributor&contributor_name=alice') {
        return Promise.resolve({
          ok: true,
          json: async () => [{ project: 'project-1' }, { project: 'project-2' }, { project: 'project-3' }],
        });
      }

      return Promise.resolve({ ok: false, json: async () => ({}) });
    });

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
});