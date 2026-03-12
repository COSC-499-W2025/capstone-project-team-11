import '@testing-library/jest-dom/vitest';
import { vi, beforeEach } from 'vitest';
import axios from 'axios';

beforeEach(() => {
  vi.spyOn(axios, 'get').mockResolvedValue({ data: [] });
  vi.spyOn(axios, 'post').mockResolvedValue({ data: {} });
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [],
    })
  );
});
