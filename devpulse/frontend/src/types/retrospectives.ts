export type Retrospective = {
  id: number
  incident_id: number
  postmortem_md: string
  runbook_md: string
  severity_score: number
  mttr_minutes: number
  model_used: string
  tokens_used: number
}
