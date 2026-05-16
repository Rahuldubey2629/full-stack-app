import { api } from '@/api/client'
import type { Retrospective } from '@/types/retrospectives'

export async function generateRetrospective(incidentId: number): Promise<{ task_id: string }> {
  const { data } = await api.post<{ task_id: string }>('/retro/generate', { incident_id: incidentId })
  return data
}

export async function getRetrospective(retroId: number): Promise<Retrospective> {
  const { data } = await api.get<Retrospective>(`/retro/${retroId}`)
  return data
}

export async function getRetrospectiveTask(taskId: string): Promise<{
  task_id: string
  state: string
  retrospective_id?: number
  error?: string
}> {
  const { data } = await api.get(`/retro/tasks/${taskId}`)
  return data
}
