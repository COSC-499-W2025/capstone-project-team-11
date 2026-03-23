import { describe, it, expect, afterEach } from 'vitest';
import { showModal } from '../src/modal';

afterEach(() => {
  document.body.innerHTML = ''; // clean DOM after each test
});

describe('showModal', () => {
  it('renders modal with title and message', async () => {
    showModal({
      title: 'Test Title',
      message: 'Test Message',
    });

    expect(document.querySelector('.modal-overlay')).toBeInTheDocument();
    expect(document.querySelector('.modal-title').textContent).toBe('Test Title');
    expect(document.querySelector('.modal-body').textContent).toBe('Test Message');
  });

  it('resolves true when confirm is clicked', async () => {
    const promise = showModal({
      title: 'Confirm Test',
      message: 'Click confirm',
    });

    const confirmBtn = document.querySelector('.modal-confirm');
    confirmBtn.click();

    const result = await promise;
    expect(result).toBe(true);
  });

  it('resolves false when cancel is clicked', async () => {
    const promise = showModal({
      title: 'Cancel Test',
      message: 'Click cancel',
      cancelText: 'Cancel',
    });

    const cancelBtn = document.querySelector('.modal-cancel');
    cancelBtn.click();

    const result = await promise;
    expect(result).toBe(false);
  });

  it('resolves false when clicking outside modal', async () => {
    const promise = showModal({
      title: 'Outside Click Test',
      message: 'Click outside',
      cancelText: 'Cancel',
    });

    const overlay = document.querySelector('.modal-overlay');
    overlay.click(); // simulate outside click

    const result = await promise;
    expect(result).toBe(false);
  });

  it('removes modal from DOM after closing', async () => {
    const promise = showModal({
      title: 'Cleanup Test',
      message: 'Close me',
    });

    document.querySelector('.modal-confirm').click();
    await promise;

    expect(document.querySelector('.modal-overlay')).toBeNull();
  });

  it('renders cancel button only when cancelText is provided', () => {
    showModal({
      title: 'No Cancel',
      message: 'Only confirm',
    });

    expect(document.querySelector('.modal-cancel')).toBeNull();
  });

  it('applies correct type class (danger)', () => {
    showModal({
      type: 'danger',
      title: 'Danger',
      message: 'Be careful',
    });

    const card = document.querySelector('.modal-card');
    expect(card.classList.contains('modal-card--danger')).toBe(true);
  });
});