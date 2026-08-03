import { apiClient } from './client'

export async function listFighters({ search, weightClass, page = 1, pageSize = 20 } = {}) {
  const { data } = await apiClient.get('/fighters', {
    params: {
      search: search || undefined,
      weight_class: weightClass || undefined,
      page,
      page_size: pageSize,
    },
  })
  return data
}

export async function getFighter(id) {
  const { data } = await apiClient.get(`/fighters/${id}`)
  return data
}
