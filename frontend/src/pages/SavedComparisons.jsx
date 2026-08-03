import { useEffect, useState } from 'react'
import { deleteComparison, listComparisons } from '../api/comparisons'
import Spinner from '../components/Spinner'

export default function SavedComparisons() {
  const [comparisons, setComparisons] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    load()
  }, [])

  function load() {
    setLoading(true)
    listComparisons()
      .then(setComparisons)
      .catch(() => setError('Could not load saved comparisons.'))
      .finally(() => setLoading(false))
  }

  async function handleDelete(id) {
    await deleteComparison(id)
    setComparisons((prev) => prev.filter((c) => c.id !== id))
  }

  return (
    <div className="saved-comparisons-page page">
      <div className="page-header">
        <h1>Saved Comparisons</h1>
        <p className="page-subtitle">Matchups you've predicted and saved.</p>
      </div>

      {loading && <Spinner label="Loading saved comparisons..." />}
      {error && <p className="error-text">{error}</p>}

      {!loading && !error && (
        <>
          {comparisons.length === 0 ? (
            <p className="empty-state">
              No saved comparisons yet. Head to the Compare page to predict a matchup and save it.
            </p>
          ) : (
            <ul className="saved-comparisons-list">
              {comparisons.map((c) => {
                const winnerProbability =
                  c.predicted_winner_id === c.fighter1_id
                    ? c.fighter1_win_probability
                    : c.fighter2_win_probability
                return (
                  <li key={c.id} className="card saved-comparison-item">
                    <div>
                      <div className="saved-comparison-matchup">
                        <strong>{c.fighter1_name}</strong>
                        <span className="vs-inline">vs</span>
                        <strong>{c.fighter2_name}</strong>
                      </div>
                      <div className="fighter-card-stats">
                        Predicted winner: <strong>{c.predicted_winner_name}</strong>
                        <span className="badge badge-accent">{Math.round(winnerProbability * 100)}%</span>
                      </div>
                    </div>
                    <button className="btn-ghost" onClick={() => handleDelete(c.id)}>
                      Delete
                    </button>
                  </li>
                )
              })}
            </ul>
          )}
        </>
      )}
    </div>
  )
}
