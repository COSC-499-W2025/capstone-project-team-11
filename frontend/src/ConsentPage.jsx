import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { API_BASE_URL } from './api';

const APP_LOGO_SRC = '/logo.png';

const DATA_ACCESS_ITEMS = [
  {
    heading: 'File System Access',
    items: [
      'File names, directory names, and complete directory structure',
      'Full absolute file paths (stored in local database)',
      'File metadata: sizes, modification times, creation times',
      'Complete file contents for code analysis (language/framework/skill detection)',
      'Any content from files stored in zipped (.zip) folders within a scanned directory',
    ],
  },
  {
    heading: 'Git Repository Data (if applicable)',
    items: [
      'Repository remote URL',
      'All commit author names (no email addresses are stored)',
      'Commit counts, dates, and file-level contribution statistics',
      'Lines added/removed per author and per file',
      'Repository creation date and activity timelines',
      'File collaboration patterns (individual vs. collaborative ownership)',
    ],
  },
  {
    heading: 'Local Data Storage',
    items: [
      'All scan results are stored in an unencrypted SQLite database (file_data.db)',
      'User preferences are written to a hidden folder in your home directory (~/.mda/config.json)',
      'Generated reports in output/ and resumes/ directories (JSON, TXT, Markdown)',
    ],
  },
  {
    heading: 'What We Do NOT Access',
    positive: false,
    items: [
      'No network requests or external API calls',
      'No data transmission to external services',
      'No access to any files outside of user-provided scan directories',
    ],
  },
];

function Section({ heading, items, positive = true }) {
  return (
    <div className="consent-section">
      <p className={`consent-section-heading${positive ? '' : ' consent-section-heading--positive'}`}>
        {heading}
      </p>
      <ul className="consent-section-list">
        {items.map((item) => (
          <li key={item} className="consent-section-item">{item}</li>
        ))}
      </ul>
    </div>
  );
}

function Toggle({ checked, onChange, disabled, label, sublabel }) {
  const classes = [
    'consent-toggle',
    checked ? 'consent-toggle--checked' : '',
    disabled ? 'consent-toggle--disabled' : '',
  ].filter(Boolean).join(' ');

  return (
    <label className={classes}>
      <input
        type="checkbox"
        checked={checked}
        disabled={disabled}
        onChange={(e) => !disabled && onChange(e.target.checked)}
        style={{ cursor: disabled ? 'not-allowed' : 'pointer' }}
      />
      <span className="consent-toggle-copy">
        <span className="consent-toggle-label">{label}</span>
        {sublabel && <span className="consent-toggle-sublabel">{sublabel}</span>}
      </span>
    </label>
  );
}

export default function ConsentPage({ initialConsent = {}, onConsented }) {
  const [dataConsent, setDataConsent] = useState(Boolean(initialConsent.data_consent));
  const [llmSummaryConsent, setLlmSummaryConsent] = useState(Boolean(initialConsent.llm_summary_consent));
  const [llmResumeConsent, setLlmResumeConsent] = useState(Boolean(initialConsent.llm_resume_consent));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const handleDataConsentChange = (val) => {
    setDataConsent(val);
    if (!val) {
      setLlmSummaryConsent(false);
      setLlmResumeConsent(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');
    try {
      const res = await fetch(`${API_BASE_URL}/privacy-consent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          data_consent: dataConsent,
          llm_summary_consent: llmSummaryConsent,
          llm_resume_consent: llmResumeConsent,
        }),
      });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      onConsented({ dataConsent, llmSummaryConsent, llmResumeConsent });
    } catch (err) {
      setError(err.message || 'Failed to save preferences. Is the backend running?');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="consent-page">
      <motion.div
        className="consent-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.25, 0.46, 0.45, 0.94] }}
      >
        {/* Header */}
        <div className="consent-header-card">
          <div className="consent-header-row">
            <div className="consent-logo">
              <img src={APP_LOGO_SRC} alt="GitHired logo" className="consent-logo-image" />
            </div>
            <div>
              <h1 className="consent-header-title">Privacy &amp; Data Consent</h1>
              <p className="consent-header-subtitle">GitHired</p>
            </div>
          </div>
          <p className="consent-header-body">
            Before scanning any projects, please review what data this tool accesses on your machine.
            All processing is done <strong style={{ color: '#f1f5f9' }}>locally</strong>, nothing is
            sent to external servers.
          </p>
        </div>

        {/* Data access details */}
        <div className="consent-data-panel">
          <p className="consent-panel-eyebrow">Data Accessed During a Scan</p>
          {DATA_ACCESS_ITEMS.map((section) => (
            <Section key={section.heading} {...section} />
          ))}
        </div>

        {/* Consent toggles */}
        <div className="consent-prefs-panel">
          <p className="consent-panel-eyebrow">Your Preferences</p>

          <Toggle
            checked={dataConsent}
            onChange={handleDataConsentChange}
            label="Allow local data scanning"
            sublabel="Required to use the app. Grants permission to read file system and git metadata from directories you choose to scan."
          />

          <Toggle
            checked={llmSummaryConsent}
            onChange={setLlmSummaryConsent}
            disabled={!dataConsent}
            label="Allow local LLM project summaries (optional)"
            sublabel="Uses a local Ollama model (llama3.2:3b) to generate short project summaries. Reads project metadata and README content. No data leaves your machine."
          />

          <Toggle
            checked={llmResumeConsent}
            onChange={setLlmResumeConsent}
            disabled={!dataConsent}
            label="Allow local LLM resume summaries (optional)"
            sublabel="Uses a local Ollama model to generate a summary section in generated resumes. No data leaves your machine."
          />
        </div>

        {/* Error */}
        {error && <p className="consent-error">{error}</p>}

        {/* Action buttons */}
        <div className="consent-actions">
          <motion.button
            className={`consent-save-btn ${dataConsent ? 'consent-save-btn--active' : 'consent-save-btn--inactive'}`}
            whileHover={{ scale: dataConsent ? 1.02 : 1 }}
            whileTap={{ scale: dataConsent ? 0.98 : 1 }}
            onClick={handleSave}
            disabled={saving || !dataConsent}
          >
            {saving ? 'Saving…' : 'Save & Continue'}
          </motion.button>
        </div>

        <p className="consent-footer-note">
          You can update these preferences at any time from the main menu.
        </p>
      </motion.div>
    </div>
  );
}
