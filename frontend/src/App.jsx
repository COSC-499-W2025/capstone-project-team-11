import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [status, setStatus] = useState('Not tested');
  const [isLoading, setIsLoading] = useState(false);

  const testConnection = async () => {
    setIsLoading(true);
    setStatus('Not tested');

    try {
      await axios.get('http://localhost:8000/projects');
      setStatus('Connected to backend!');
    } catch (err) {
      setStatus(`Failed: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ fontFamily: 'sans-serif', padding: '2rem', textAlign: 'center' }}>
      <h1>Capstone MDA App</h1>
      <button onClick={testConnection} disabled={isLoading}>
        {isLoading ? 'Checking...' : 'Test Backend Connection'}
      </button>
      <p>Status: {status}</p>
    </div>
  );
}

export default App;
