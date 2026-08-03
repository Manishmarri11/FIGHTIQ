import { useEffect, useState } from 'react'
import { listFighters } from '../api/fighters'
import FighterCard from '../components/FighterCard'
import Spinner from '../components/Spinner'
import { WEIGHT_CLASSES } from '../constants'

const DEBOUNCE_MS = 300

export default function FighterList() {
  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [weightClass, setWeightClass] = useState('')
  const [page, setPage] = useState(1)
  const [result, setResult] = useState({ total: 0, page: 1, page_size: 20, fighters: [] })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search)
      setPage(1)
    }, DEBOUNCE_MS)
    return () => clearTimeout(timer)
  }, [search])

  useEffect(() => {
    setPage(1)
  }, [weightClass])

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    listFighters({ search: debouncedSearch, weightClass, page })
      .then((data) => {
        if (!cancelled) setResult(data)
      })
      .catch(() => {
        if (!cancelled) setError('Could not load fighters. Is the backend running?')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [debouncedSearch, weightClass, page])

  const totalPages = Math.max(1, Math.ceil(result.total / result.page_size))

  return (
    <div className="fighter-list-page page">
      <div className="page-header">
        <h1>Fighters</h1>
        <p className="page-subtitle">{result.total.toLocaleString()} fighters in the database</p>
      </div>

      <div className="filter-row">
        <input
          type="text"
          className="search-input"
          placeholder="Search fighters by name..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className="select-input"
          value={weightClass}
          onChange={(e) => setWeightClass(e.target.value)}
        >
          <option value="">All weight classes</option>
          {WEIGHT_CLASSES.map((wc) => (
            <option key={wc} value={wc}>
              {wc}
            </option>
          ))}
        </select>
      </div>

      {error && <p className="error-text">{error}</p>}
      {loading && <Spinner label="Loading fighters..." />}

      {!loading && !error && (
        <>
          {result.fighters.length === 0 ? (
            <p className="empty-state">No fighters found. Try a different search or weight class.</p>
          ) : (
            <div className="fighter-grid">
              {result.fighters.map((fighter) => (
                <FighterCard key={fighter.id} fighter={fighter} />
              ))}
            </div>
          )}

          {totalPages > 1 && (
            <div className="pagination">
              <button
                className="btn-ghost"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                Previous
              </button>
              <span className="pagination-status">
                Page {page} of {totalPages}
              </span>
              <button
                className="btn-ghost"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
