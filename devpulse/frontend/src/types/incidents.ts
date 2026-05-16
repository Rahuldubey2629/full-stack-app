export type Incident = {
  id: number
  title: string
  description: string
  raw_input: string
  severity_label: string
  status: string
  created_by: number
}

export type IncidentCreate = {
  title: string
  description: string
  raw_input: string
  severity_label: string
}
