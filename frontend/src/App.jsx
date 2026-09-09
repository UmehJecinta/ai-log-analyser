import { useState } from 'react'
import axios from 'axios'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [title, setTitle] = useState('')
  const [logs, setLogs] = useState('')
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [history, setHistory] = useState([])
  const [activeTab, setActiveTab] = useState('analyse')

  const handleAnalyse = async () => {
    if (!title.trim() || !logs.trim()) {
      setError('Please provide both a title and logs to analyse')
      return
    }

    setLoading(true)
    setError('')
    setAnalysis(null)

    try {
      const response = await axios.post(`${API_URL}/api/analyse`, {
        title: title,
        original_logs: logs
      })
      setAnalysis(response.data)
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Failed to analyse logs. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/analyses`)
      setHistory(response.data)
    } catch (err) {
      setError('Failed to fetch history')
    }
  }

  const handleTabChange = (tab) => {
    setActiveTab(tab)
    if (tab === 'history') fetchHistory()
  }

  const getSeverityColor = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL': return '#e53e3e'
      case 'HIGH': return '#dd6b20'
      case 'MEDIUM': return '#d69e2e'
      case 'LOW': return '#38a169'
      default: return '#718096'
    }
  }

  return (
    <div className="app">

      <header className="header">
        <h1>🔍 AI Log Analyser</h1>
        <p>Paste your logs and get instant AI-powered root cause analysis</p>
      </header>

      <div className="card">

        <nav className="tabs">
          <button
            className={activeTab === 'analyse' ? 'tab active' : 'tab'}
            onClick={() => handleTabChange('analyse')}
          >
            Analyse Logs
          </button>
          <button
            className={activeTab === 'history' ? 'tab active' : 'tab'}
            onClick={() => handleTabChange('history')}
          >
            History
          </button>
        </nav>

        {activeTab === 'analyse' && (
          <div className="analyse-section">

            <div className="input-group">
              <label>Session Title</label>
              <input
                type="text"
                placeholder="e.g. Production crash 2026-09-08"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="input"
              />
            </div>

            <div className="input-group">
              <label>Paste Your Logs</label>
              <textarea
                placeholder="Paste your application or server logs here..."
                value={logs}
                onChange={(e) => setLogs(e.target.value)}
                className="textarea"
                rows={12}
              />
            </div>

            {error && <div className="error">{error}</div>}

            <button
              onClick={handleAnalyse}
              disabled={loading}
              className="analyse-btn"
            >
              {loading ? 'Analysing...' : '✨ Analyse Logs'}
            </button>

            {loading && (
              <div className="loading">
                <div className="spinner"></div>
                <p>AI is analysing your logs...</p>
              </div>
            )}

            {analysis && (
              <div className="results">
                <h2>Analysis Results</h2>

                <div
                  className="severity-badge"
                  style={{ backgroundColor: getSeverityColor(analysis.severity) }}
                >
                  {analysis.severity}
                </div>

                <div className="result-card">
                  <h3>❌ What Went Wrong</h3>
                  <p>{analysis.what_went_wrong}</p>
                </div>

                <div className="result-card">
                  <h3>📍 Where It Went Wrong</h3>
                  <p>{analysis.where_it_went_wrong}</p>
                </div>

                <div className="result-card">
                  <h3>✅ Suggested Fix</h3>
                  <p>{analysis.suggested_fix}</p>
                </div>

                <details className="raw-analysis">
                  <summary>View Raw Analysis</summary>
                  <pre>{analysis.raw_analysis}</pre>
                </details>
              </div>
            )}

          </div>
        )}

        {activeTab === 'history' && (
          <div className="history-section">
            <h2>Analysis History</h2>
            {history.length === 0 ? (
              <p className="empty">No analyses yet. Start by analysing some logs.</p>
            ) : (
              <div className="history-list">
                {history.map((item) => (
                  <div key={item.id} className="history-item">
                    <div className="history-header">
                      <h3>{item.title}</h3>
                      <span
                        className="severity-badge small"
                        style={{ backgroundColor: getSeverityColor(item.severity) }}
                      >
                        {item.severity || 'UNKNOWN'}
                      </span>
                    </div>
                    <p className="history-date">
                      {new Date(item.created_at).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

      </div>

      <footer className="footer">
        <p>Built with React • FastAPI • AWS Bedrock Claude • PostgreSQL • Kubernetes</p>
      </footer>

    </div>
  )
}

export default App