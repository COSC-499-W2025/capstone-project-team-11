import React from 'react';

const THEMES = [
  {
    id: 'evergreen',
    name: 'Evergreen',
    description: 'Original look with rich green-cyan accents.',
    swatches: ['#4ade80', '#22d3ee', '#0a5948'],
  },
  {
    id: 'harbor',
    name: 'Harbor',
    description: 'Balanced teal and blue with less green dominance.',
    swatches: ['#2dd4bf', '#38bdf8', '#0b4d66'],
  },
  {
    id: 'violet-night',
    name: 'Violet Night',
    description: 'Cool indigo tones for a calm, modern interface.',
    swatches: ['#818cf8', '#38bdf8', '#292148'],
  },
  {
    id: 'sunset',
    name: 'Sunset',
    description: 'Warm coral and amber highlights with dark contrast.',
    swatches: ['#fb7185', '#f59e0b', '#5b1e2f'],
  },
];

function ThemeSettingsPage({ currentTheme, onThemeChange, onBack }) {
  return (
    <div className="page-shell">
      <header className="app-header">
        <h1>Theme Settings</h1>
        <p>Select a color scheme for the app. Changes apply instantly.</p>
      </header>

      <section className="scan-panel" style={{ textAlign: 'left' }}>
        <div className="theme-grid">
          {THEMES.map((theme) => {
            const selected = theme.id === currentTheme;

            return (
              <button
                key={theme.id}
                type="button"
                className="theme-card"
                onClick={() => onThemeChange(theme.id)}
                style={{
                  borderColor: selected ? 'var(--accent-cyan)' : 'var(--border)',
                  boxShadow: selected
                    ? '0 0 0 1px color-mix(in srgb, var(--accent-cyan) 40%, transparent), var(--shadow-sm)'
                    : 'var(--shadow-sm)',
                }}
              >
                <div className="theme-card-top">
                  <span className="theme-title">{theme.name}</span>
                  {selected && <span className="theme-active-pill">Active</span>}
                </div>
                <p className="theme-description">{theme.description}</p>
                <div className="theme-swatches" aria-hidden="true">
                  {theme.swatches.map((color) => (
                    <span key={color} className="theme-swatch" style={{ background: color }} />
                  ))}
                </div>
              </button>
            );
          })}
        </div>

        <div className="scan-actions" style={{ marginTop: '1rem' }}>
          <button onClick={onBack} className="secondary px-4 py-2">
            ← Back
          </button>
        </div>
      </section>
    </div>
  );
}

export default ThemeSettingsPage;
