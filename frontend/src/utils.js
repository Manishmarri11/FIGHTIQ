// Formats a fighter's actual UFC record as W-L, adding draws only when there are any.
export function formatRecord(fighter) {
  if (fighter.ufc_wins == null || fighter.ufc_losses == null) return '—'
  const record = `${fighter.ufc_wins}-${fighter.ufc_losses}`
  return fighter.ufc_draws ? `${record}-${fighter.ufc_draws}` : record
}
