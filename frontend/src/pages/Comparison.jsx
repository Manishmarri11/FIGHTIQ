import { useState } from 'react'
import FighterSelect from '../components/FighterSelect'
import Spinner from '../components/Spinner'
import { predictMatch } from '../api/predict'
import { createComparison } from '../api/comparisons'
import { useAuth } from '../context/AuthContext'

function StatRow({ label, a, b }) {
  return (
    <div className="stat-row">
      <span className="stat-value">{a ?? '—'}</span>
      <span className="stat-label">{label}</span>
      <span className="stat-value">{b ?? '—'}</span>
    </div>
  )
}

function ProbabilityBar({ name, probability, isWinner }) {
  const pct = Math.round(probability * 100)
  return (
    <div className={`probability-bar${isWinner ? ' is-winner' : ''}`}>
      <div className="probability-bar-label">
        <span>
          {name}
          {isWinner && <span className="winner-badge">Predicted winner</span>}
        </span>
        <span>{pct}%</span>
      </div>
      <div className="probability-bar-track">
        <div className="probability-bar-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

export default function Comparison() {
  const { user } = useAuth()
  const [fighter1, setFighter1] = useState(null)
  const [fighter2, setFighter2] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [saveStatus, setSaveStatus] = useState(null)

  async function handlePredict() {
    setError(null)
    setResult(null)
    setSaveStatus(null)

    if (!fighter1 || !fighter2) {
      setError('Select two fighters first.')
      return
    }

    setLoading(true)
    try {
      const data = await predictMatch(fighter1.id, fighter2.id)
      setResult(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Prediction failed.')
    } finally {
      setLoading(false)
    }
  }

  async function handleSave() {
    setSaveStatus(null)
    try {
      await createComparison(fighter1.id, fighter2.id)
      setSaveStatus('saved')
    } catch {
      setSaveStatus('error')
    }
  }

  const fighter1IsWinner = result && fighter1 && result.winner_id === fighter1.id
  const fighter2IsWinner = result && fighter2 && result.winner_id === fighter2.id

  return (
    <div className="comparison-page page">
      <div className="page-header">
        <h1>Compare Fighters</h1>
        <p className="page-subtitle">Pick two fighters in the same weight class to predict a winner.</p>
      </div>

      <div className="card comparison-form">
        <div className="comparison-pickers">
          <FighterSelect label="Fighter 1" value={fighter1} onChange={setFighter1} />
          <span className="vs">VS</span>
          <FighterSelect label="Fighter 2" value={fighter2} onChange={setFighter2} />
        </div>

        <button className="btn-primary" onClick={handlePredict} disabled={loading || !fighter1 || !fighter2}>
          {loading ? 'Predicting...' : 'Predict'}
        </button>

        {loading && <Spinner />}
        {error && <p className="error-text">{error}</p>}
      </div>

      {result && fighter1 && fighter2 && (
        <div className="card comparison-result">
          <div className="stat-table">
            <div className="stat-table-header">
              <span className={fighter1IsWinner ? 'is-winner' : ''}>{fighter1.name}</span>
              <span className="stat-label">Stat</span>
              <span className={fighter2IsWinner ? 'is-winner' : ''}>{fighter2.name}</span>
            </div>
            <StatRow label="Weight class" a={fighter1.weight_class} b={fighter2.weight_class} />
            <StatRow
              label="Record (W-L, career avg)"
              a={`${Math.round(fighter1.wins ?? 0)}-${Math.round(fighter1.losses ?? 0)}`}
              b={`${Math.round(fighter2.wins ?? 0)}-${Math.round(fighter2.losses ?? 0)}`}
            />
            <StatRow
              label="Height (cm)"
              a={fighter1.height_cms?.toFixed(1)}
              b={fighter2.height_cms?.toFixed(1)}
            />
            <StatRow
              label="Reach (cm)"
              a={fighter1.reach_cms?.toFixed(1)}
              b={fighter2.reach_cms?.toFixed(1)}
            />
            <StatRow
              label="Avg win streak"
              a={fighter1.current_win_streak?.toFixed(2)}
              b={fighter2.current_win_streak?.toFixed(2)}
            />
          </div>

          <div className="prediction-result">
            <h2>Predicted winner: {result.winner_name}</h2>
            <div className="probability-bars">
              <ProbabilityBar
                name={fighter1.name}
                probability={result.fighter1_win_probability}
                isWinner={fighter1IsWinner}
              />
              <ProbabilityBar
                name={fighter2.name}
                probability={result.fighter2_win_probability}
                isWinner={fighter2IsWinner}
              />
            </div>
          </div>

          <div className="comparison-save">
            {user ? (
              <button className="btn-primary" onClick={handleSave}>
                Save this comparison
              </button>
            ) : (
              <p className="muted-text">Log in to save this comparison.</p>
            )}
            {saveStatus === 'saved' && <p className="success-text">Saved.</p>}
            {saveStatus === 'error' && <p className="error-text">Could not save comparison.</p>}
          </div>
        </div>
      )}
    </div>
  )
}
