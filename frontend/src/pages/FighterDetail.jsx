import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getFighter } from '../api/fighters'
import Spinner from '../components/Spinner'
import { formatRecord } from '../utils'

function Detail({ label, value }) {
  return (
    <div className="detail-item">
      <span className="detail-label">{label}</span>
      <span className="detail-value">{value ?? '—'}</span>
    </div>
  )
}

export default function FighterDetail() {
  const { id } = useParams()
  const [fighter, setFighter] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setFighter(null)
    setError(null)

    getFighter(id)
      .then((data) => {
        if (!cancelled) setFighter(data)
      })
      .catch((err) => {
        if (cancelled) return
        setError(err.response?.status === 404 ? 'Fighter not found.' : 'Could not load this fighter.')
      })

    return () => {
      cancelled = true
    }
  }, [id])

  return (
    <div className="fighter-detail-page page">
      <Link to="/" className="back-link">
        &larr; All fighters
      </Link>

      {error && <p className="error-text">{error}</p>}
      {!fighter && !error && <Spinner label="Loading fighter..." />}

      {fighter && (
        <>
          <div className="page-header fighter-detail-header">
            <div>
              <h1>{fighter.name}</h1>
              <p className="page-subtitle">
                {[fighter.weight_class, fighter.stance].filter(Boolean).join(' · ')}
              </p>
            </div>
            <Link to={`/compare?fighter1=${fighter.id}`} className="btn-primary">
              Compare
            </Link>
          </div>

          <div className="card">
            <div className="detail-grid">
              <Detail label="UFC record (W-L-D)" value={formatRecord(fighter)} />
              <Detail label="Fights in dataset" value={fighter.total_fights} />
              <Detail label="Last fight" value={fighter.last_fight_date} />
              <Detail label="Age at last fight" value={fighter.age} />
              <Detail label="Height" value={fighter.height_cms && `${fighter.height_cms.toFixed(1)} cm`} />
              <Detail label="Reach" value={fighter.reach_cms && `${fighter.reach_cms.toFixed(1)} cm`} />
              <Detail label="Weight" value={fighter.weight_lbs && `${Math.round(fighter.weight_lbs)} lbs`} />
            </div>
          </div>

          <h2 className="section-title">Model inputs</h2>
          <p className="muted-text">
            The prediction model uses these values averaged across every fight in the dataset, not the
            fighter&apos;s current numbers.
          </p>
          <div className="card">
            <div className="detail-grid">
              <Detail label="Avg betting odds" value={fighter.avg_odds?.toFixed(0)} />
              <Detail label="Avg win streak" value={fighter.current_win_streak?.toFixed(2)} />
              <Detail label="Avg wins by KO" value={fighter.wins_by_ko?.toFixed(2)} />
              <Detail label="Avg wins by submission" value={fighter.wins_by_submission?.toFixed(2)} />
              <Detail label="Avg wins" value={fighter.wins?.toFixed(2)} />
              <Detail label="Avg losses" value={fighter.losses?.toFixed(2)} />
            </div>
          </div>
        </>
      )}
    </div>
  )
}
