import { apiClient } from './client'

export async function predictMatch(fighter1Id, fighter2Id) {
  const { data } = await apiClient.post('/predict', {
    fighter1_id: fighter1Id,
    fighter2_id: fighter2Id,
  })
  return data
}
