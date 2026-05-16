import { api } from '@/api/client'
import type { Incident, IncidentCreate } from '@/types/incidents'

export async function listIncidents(): Promise<Incident[]> {
  const { data } = await api.get<Incident[]>('/incidents')
  return data
}

export async function createIncident(payload: IncidentCreate): Promise<Incident> {
  const { data } = await api.post<Incident>('/incidents', payload)
  return data
}
