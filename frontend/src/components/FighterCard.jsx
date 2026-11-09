import { Link } from 'react-router-dom'
import { formatRecord } from '../utils'

export default function FighterCard({ fighter }) {
  return (
    <Link to={`/fighters/${fighter.id}`} className="fighter-card">
      <div className="fighter-card-top">
        <span className="fighter-card-name">{fighter.name}</span>
        {fighter.weight_class && <span className="badge">{fighter.weight_class}</span>}
      </div>
      <div className="fighter-card-stats">
        <span>
          <strong>{formatRecord(fighter)}</strong> UFC record
        </span>
      </div>
    </Link>
  )
}
