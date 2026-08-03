import { apiClient } from './client'

export async function createComparison(fighter1Id, fighter2Id) {
  const { data } = await apiClient.post('/comparisons', {
    fighter1_id: fighter1Id,
    fighter2_id: fighter2Id,
  })
  return data
}

export async function listComparisons() {
  const { data } = await apiClient.get('/comparisons')
  return data
}

export async function deleteComparison(id) {
  await apiClient.delete(`/comparisons/${id}`)
}
