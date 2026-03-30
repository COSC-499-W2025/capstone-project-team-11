import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import ResumePage from '../src/ResumePage.jsx';
import * as modal from '../src/modal.js';

const mockMountFetches = () =>
  vi.spyOn(global, 'fetch')
    .mockResolvedValueOnce({ ok: true, json: async () => [] })
    .mockResolvedValueOnce({ ok: true, json: async () => ({}) })
    .mockResolvedValueOnce({ ok: true, json: async () => [] })
    .mockResolvedValueOnce({ ok: true, json: async () => [] });

const mockBaseSelectableState = () =>
  vi.spyOn(global, 'fetch').mockImplementation((url) => {
    const requestUrl = String(url);

    if (requestUrl === 'http://127.0.0.1:8000/contributors') {
      return Promise.resolve({ ok: true, json: async () => ['alice'] });
    }
    if (requestUrl === 'http://127.0.0.1:8000/config') {
      return Promise.resolve({ ok: true, json: async () => ({ llm_resume_consent: true }) });
    }
    if (requestUrl === 'http://127.0.0.1:8000/projects') {
      return Promise.resolve({
        ok: true,
        json: async () => [{ id: 1, name: 'project-1', custom_name: 'Project 1' }],
      });
    }
    if (requestUrl === 'http://127.0.0.1:8000/resumes' || requestUrl === 'http://127.0.0.1:8000/resumes?username=alice') {
      return Promise.resolve({ ok: true, json: async () => [] });
    }
    if (requestUrl === 'http://127.0.0.1:8000/rank-projects?mode=contributor&contributor_name=alice') {
      return Promise.resolve({ ok: true, json: async () => [{ project: 'project-1' }] });
    }

    return Promise.resolve({ ok: false, json: async () => ({}) });
  });

afterEach(() => {
  vi.restoreAllMocks();
});

describe('ResumePage', () => {
  it('renders contributor select and generate button', async () => {
    mockMountFetches();
    render(<ResumePage />);
    expect(screen.getByRole('combobox')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Generate Resume/i })).toBeInTheDocument();
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('http://127.0.0.1:8000/contributors');
    });
  });

  it('shows generating state when generate is clicked', async () => {
    const pendingGenerate = new Promise(() => {});
    mockBaseSelectableState().mockImplementation((url) => {
      const requestUrl = String(url);
      if (requestUrl === 'http://127.0.0.1:8000/resume/generate') return pendingGenerate;
      if (requestUrl === 'http://127.0.0.1:8000/contributors') {
        return Promise.resolve({ ok: true, json: async () => ['alice'] });
      }
      if (requestUrl === 'http://127.0.0.1:8000/config') {
        return Promise.resolve({ ok: true, json: async () => ({ llm_resume_consent: true }) });
      }
      if (requestUrl === 'http://127.0.0.1:8000/projects') {
        return Promise.resolve({
          ok: true,
          json: async () => [{ id: 1, name: 'project-1', custom_name: 'Project 1' }],
        });
      }
      if (requestUrl === 'http://127.0.0.1:8000/resumes' || requestUrl === 'http://127.0.0.1:8000/resumes?username=alice') {
        return Promise.resolve({ ok: true, json: async () => [] });
      }
      if (requestUrl === 'http://127.0.0.1:8000/rank-projects?mode=contributor&contributor_name=alice') {
        return Promise.resolve({ ok: true, json: async () => [{ project: 'project-1' }] });
      }
      return Promise.resolve({ ok: false, json: async () => ({}) });
    });
    render(<ResumePage />);
    fireEvent.change(await screen.findByRole('combobox'), { target: { value: 'alice' } });
    await screen.findByLabelText(/Project 1/i);
    fireEvent.click(screen.getByRole('button', { name: /Generate Resume/i }));
    expect(await screen.findByRole('button', { name: /Generating/i })).toBeDisabled();
  });

  it('shows resume content when API calls succeed', async () => {
    vi.spyOn(global, 'fetch').mockImplementation((url) => {
      const requestUrl = String(url);
      if (requestUrl === 'http://127.0.0.1:8000/contributors') {
        return Promise.resolve({ ok: true, json: async () => ['alice'] });
      }
      if (requestUrl === 'http://127.0.0.1:8000/config') {
        return Promise.resolve({ ok: true, json: async () => ({ llm_resume_consent: true }) });
      }
      if (requestUrl === 'http://127.0.0.1:8000/projects') {
        return Promise.resolve({
          ok: true,
          json: async () => [{ id: 1, name: 'project-1', custom_name: 'Project 1' }],
        });
      }
      if (requestUrl === 'http://127.0.0.1:8000/resumes' || requestUrl === 'http://127.0.0.1:8000/resumes?username=alice') {
        return Promise.resolve({ ok: true, json: async () => [] });
      }
      if (requestUrl === 'http://127.0.0.1:8000/rank-projects?mode=contributor&contributor_name=alice') {
        return Promise.resolve({ ok: true, json: async () => [{ project: 'project-1' }] });
      }
      if (requestUrl === 'http://127.0.0.1:8000/resume/generate') {
        return Promise.resolve({
          ok: true,
          json: async () => ({ resume_id: 42, resume_path: '/tmp/resume.md', generated_at: '2026-03-07' }),
        });
      }
      if (requestUrl === 'http://127.0.0.1:8000/resume/42') {
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

    render(<ResumePage />);
    fireEvent.change(await screen.findByRole('combobox'), { target: { value: 'alice' } });
    await screen.findByLabelText(/Project 1/i);
    fireEvent.click(screen.getByRole('button', { name: /Generate Resume/i }));

    expect(await screen.findByText(/Generated Resume/i)).toBeInTheDocument();
    expect(screen.getByText(/Alice Resume/i)).toBeInTheDocument();
    expect(global.fetch).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/resume/generate',
      expect.objectContaining({
        method: 'POST',
        body: expect.stringContaining('"excluded_project_names":[]'),
      }),
    );
    expect(global.fetch).toHaveBeenCalledWith('http://127.0.0.1:8000/resume/42');
  });

  it('shows error message when API call fails', async () => {
    vi.spyOn(global, 'fetch').mockImplementation((url) => {
      const requestUrl = String(url);
      if (requestUrl === 'http://127.0.0.1:8000/contributors') {
        return Promise.resolve({ ok: true, json: async () => ['alice'] });
      }
      if (requestUrl === 'http://127.0.0.1:8000/config') {
        return Promise.resolve({ ok: true, json: async () => ({ llm_resume_consent: true }) });
      }
      if (requestUrl === 'http://127.0.0.1:8000/projects') {
        return Promise.resolve({
          ok: true,
          json: async () => [{ id: 1, name: 'project-1', custom_name: 'Project 1' }],
        });
      }
      if (requestUrl === 'http://127.0.0.1:8000/resumes' || requestUrl === 'http://127.0.0.1:8000/resumes?username=alice') {
        return Promise.resolve({ ok: true, json: async () => [] });
      }
      if (requestUrl === 'http://127.0.0.1:8000/rank-projects?mode=contributor&contributor_name=alice') {
        return Promise.resolve({ ok: true, json: async () => [{ project: 'project-1' }] });
      }
      if (requestUrl === 'http://127.0.0.1:8000/resume/generate') {
        return Promise.reject(new Error('Network failure'));
      }
      return Promise.resolve({ ok: false, json: async () => ({}) });
    });

    render(<ResumePage />);
    fireEvent.change(await screen.findByRole('combobox'), { target: { value: 'alice' } });
    await screen.findByLabelText(/Project 1/i);
    fireEvent.click(screen.getByRole('button', { name: /Generate Resume/i }));

    await waitFor(() => {
      expect(screen.getByText(/Network failure/i)).toBeInTheDocument();
    });
  });

  it('downloads pdf from backend endpoint', async () => {
    const originalCreateObjectURL = URL.createObjectURL;
    const originalRevokeObjectURL = URL.revokeObjectURL;
    URL.createObjectURL = vi.fn(() => 'blob:resume-pdf');
    URL.revokeObjectURL = vi.fn();

    vi.spyOn(global, 'fetch').mockImplementation((url) => {
      const requestUrl = String(url);
      if (requestUrl === 'http://127.0.0.1:8000/contributors') {
        return Promise.resolve({ ok: true, json: async () => ['alice'] });
      }
      if (requestUrl === 'http://127.0.0.1:8000/config') {
        return Promise.resolve({ ok: true, json: async () => ({ llm_resume_consent: true }) });
      }
      if (requestUrl === 'http://127.0.0.1:8000/projects') {
        return Promise.resolve({
          ok: true,
          json: async () => [{ id: 1, name: 'project-1', custom_name: 'Project 1' }],
        });
      }
      if (requestUrl === 'http://127.0.0.1:8000/resumes' || requestUrl === 'http://127.0.0.1:8000/resumes?username=alice') {
        return Promise.resolve({ ok: true, json: async () => [] });
      }
      if (requestUrl === 'http://127.0.0.1:8000/rank-projects?mode=contributor&contributor_name=alice') {
        return Promise.resolve({ ok: true, json: async () => [{ project: 'project-1' }] });
      }
      if (requestUrl === 'http://127.0.0.1:8000/resume/generate') {
        return Promise.resolve({
          ok: true,
          json: async () => ({ resume_id: 42, resume_path: '/tmp/resume.md', generated_at: '2026-03-07' }),
        });
      }
      if (requestUrl === 'http://127.0.0.1:8000/resume/42') {
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
      if (requestUrl === 'http://127.0.0.1:8000/resume/42/pdf/info') {
        return Promise.resolve({
          ok: true,
          json: async () => ({ filename: 'resume_alice_42.pdf', page_count: 1, is_multi_page: false }),
        });
      }
      if (requestUrl === 'http://127.0.0.1:8000/resume/42/pdf') {
        return Promise.resolve({
          ok: true,
          blob: async () => new Blob(['pdf-bytes'], { type: 'application/pdf' }),
          headers: new Headers({
            'Content-Disposition': 'attachment; filename="resume_alice_42.pdf"',
          }),
        });
      }
      return Promise.resolve({ ok: false, json: async () => ({}) });
    });

    render(<ResumePage />);
    fireEvent.change(await screen.findByRole('combobox'), { target: { value: 'alice' } });
    await screen.findByLabelText(/Project 1/i);
    fireEvent.click(screen.getByRole('button', { name: /Generate Resume/i }));
    expect(await screen.findByText(/Generated Resume/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /\.pdf/i }));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('http://127.0.0.1:8000/resume/42/pdf/info');
      expect(global.fetch).toHaveBeenCalledWith('http://127.0.0.1:8000/resume/42/pdf');
      expect(URL.createObjectURL).toHaveBeenCalled();
      expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:resume-pdf');
    });

    URL.createObjectURL = originalCreateObjectURL;
    URL.revokeObjectURL = originalRevokeObjectURL;
  });

  it('shows a warning before exporting a multi-page pdf and stops when cancelled', async () => {
    const showModalSpy = vi.spyOn(modal, 'showModal').mockResolvedValue(false);

    vi.spyOn(global, 'fetch').mockImplementation((url) => {
      const requestUrl = String(url);
      if (requestUrl === 'http://127.0.0.1:8000/contributors') {
        return Promise.resolve({ ok: true, json: async () => ['alice'] });
      }
      if (requestUrl === 'http://127.0.0.1:8000/config') {
        return Promise.resolve({ ok: true, json: async () => ({ llm_resume_consent: true }) });
      }
      if (requestUrl === 'http://127.0.0.1:8000/projects') {
        return Promise.resolve({
          ok: true,
          json: async () => [{ id: 1, name: 'project-1', custom_name: 'Project 1' }],
        });
      }
      if (requestUrl === 'http://127.0.0.1:8000/resumes' || requestUrl === 'http://127.0.0.1:8000/resumes?username=alice') {
        return Promise.resolve({ ok: true, json: async () => [] });
      }
      if (requestUrl === 'http://127.0.0.1:8000/rank-projects?mode=contributor&contributor_name=alice') {
        return Promise.resolve({ ok: true, json: async () => [{ project: 'project-1' }] });
      }
      if (requestUrl === 'http://127.0.0.1:8000/resume/generate') {
        return Promise.resolve({
          ok: true,
          json: async () => ({ resume_id: 42, resume_path: '/tmp/resume.md', generated_at: '2026-03-07' }),
        });
      }
      if (requestUrl === 'http://127.0.0.1:8000/resume/42') {
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
      if (requestUrl === 'http://127.0.0.1:8000/resume/42/pdf/info') {
        return Promise.resolve({
          ok: true,
          json: async () => ({ filename: 'resume_alice_42.pdf', page_count: 3, is_multi_page: true }),
        });
      }
      return Promise.resolve({ ok: false, json: async () => ({}) });
    });

    render(<ResumePage />);
    fireEvent.change(await screen.findByRole('combobox'), { target: { value: 'alice' } });
    await screen.findByLabelText(/Project 1/i);
    fireEvent.click(screen.getByRole('button', { name: /Generate Resume/i }));
    expect(await screen.findByText(/Generated Resume/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /\.pdf/i }));

    await waitFor(() => {
      expect(showModalSpy).toHaveBeenCalledWith(expect.objectContaining({
        type: 'warning',
        title: 'Resume Exceeds One Page',
        message: expect.stringContaining('3 pages long'),
      }));
    });

    expect(global.fetch).toHaveBeenCalledWith('http://127.0.0.1:8000/resume/42/pdf/info');
    expect(global.fetch).not.toHaveBeenCalledWith('http://127.0.0.1:8000/resume/42/pdf');
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
