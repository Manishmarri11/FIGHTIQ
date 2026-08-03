export default function FighterCard({ fighter }) {
  const wins = Math.round(fighter.wins ?? 0)
  const losses = Math.round(fighter.losses ?? 0)

  return (
    <div className="fighter-card">
      <div className="fighter-card-top">
        <span className="fighter-card-name">{fighter.name}</span>
        {fighter.weight_class && <span className="badge">{fighter.weight_class}</span>}
      </div>
      <div className="fighter-card-stats">
        <span>
          <strong>{wins}</strong> wins
        </span>
        <span className="dot">&middot;</span>
        <span>
          <strong>{losses}</strong> losses
        </span>
      </div>
    </div>
  )
}
