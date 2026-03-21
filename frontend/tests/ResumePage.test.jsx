import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import ResumePage from '../src/ResumePage.jsx';

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

  it('downloads pdf from backend endpoint', async () => {
    const originalCreateObjectURL = URL.createObjectURL;
    const originalRevokeObjectURL = URL.revokeObjectURL;
    URL.createObjectURL = vi.fn(() => 'blob:resume-pdf');
    URL.revokeObjectURL = vi.fn();

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
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({
        ok: true,
        blob: async () => new Blob(['pdf-bytes'], { type: 'application/pdf' }),
        headers: new Headers({
          'Content-Disposition': 'attachment; filename="resume_alice_42.pdf"',
        }),
      });

    render(<ResumePage />);
    fireEvent.click(screen.getByRole('button', { name: /Generate Resume/i }));
    expect(await screen.findByText(/Generated Resume/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /\.pdf/i }));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('http://127.0.0.1:8000/resume/42/pdf');
      expect(URL.createObjectURL).toHaveBeenCalled();
      expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:resume-pdf');
    });

    URL.createObjectURL = originalCreateObjectURL;
    URL.revokeObjectURL = originalRevokeObjectURL;
  });
});
