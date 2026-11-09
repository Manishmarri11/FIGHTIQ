import { useEffect, useState } from 'react'
import { listFighters } from '../api/fighters'

const DEBOUNCE_MS = 250

export default function FighterSelect({ label, value, onChange }) {
  const [query, setQuery] = useState(value?.name ?? '')
  const [options, setOptions] = useState([])
  const [open, setOpen] = useState(false)

  // Keep the input in sync when the parent sets a fighter (e.g. pre-filled from a URL).
  useEffect(() => {
    if (value) setQuery(value.name)
  }, [value])

  useEffect(() => {
    if (!query || (value && query === value.name)) {
      setOptions([])
      return
    }
    let cancelled = false
    const timer = setTimeout(() => {
      listFighters({ search: query, pageSize: 10 }).then((data) => {
        if (!cancelled) setOptions(data.fighters)
      })
    }, DEBOUNCE_MS)
    return () => {
      cancelled = true
      clearTimeout(timer)
    }
  }, [query, value])

  function handleInputChange(e) {
    const nextQuery = e.target.value
    setQuery(nextQuery)
    setOpen(true)
    if (value) onChange(null)
  }

  function handleSelect(fighter) {
    onChange(fighter)
    setQuery(fighter.name)
    setOpen(false)
  }

  return (
    <div className="fighter-select">
      <label>{label}</label>
      <input
        type="text"
        value={query}
        onChange={handleInputChange}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
        placeholder="Search fighter by name..."
        autoComplete="off"
      />
      {open && options.length > 0 && (
        <ul className="fighter-select-options">
          {options.map((fighter) => (
            <li
              key={fighter.id}
              // onMouseDown (not onClick) fires before the input's onBlur, and
              // preventDefault stops the blur from happening at all — so selecting
              // an option never races against the dropdown closing itself.
              onMouseDown={(e) => {
                e.preventDefault()
                handleSelect(fighter)
              }}
            >
              {fighter.name} <span className="fighter-select-weight-class">({fighter.weight_class})</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
