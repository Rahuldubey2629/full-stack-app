import React from 'react'
import { useMutation } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'

import { createIncident } from '@/api/incidents'
import { generateRetrospective, getRetrospectiveTask } from '@/api/retrospectives'
import LLMStatusBar from '@/components/LLMStatusBar'

export default function NewIncidentPage() {
  const navigate = useNavigate()

  const [title, setTitle] = React.useState('')
  const [description, setDescription] = React.useState('')
  const [severity, setSeverity] = React.useState('sev2')
  const [rawInput, setRawInput] = React.useState('')
  const [status, setStatus] = React.useState<'idle' | 'generating' | 'done' | 'error'>('idle')
  const [error, setError] = React.useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: async () => {
      const incident = await createIncident({
        title,
        description,
        raw_input: rawInput,
        severity_label: severity,
      })
      const { task_id } = await generateRetrospective(incident.id)
      return task_id
    },
    onMutate: () => {
      setStatus('generating')
      setError(null)
    },
    onSuccess: async (taskId) => {
      try {
        for (let i = 0; i < 30; i++) {
          const s = await getRetrospectiveTask(taskId)
          if (s.state === 'SUCCESS' && s.retrospective_id) {
            setStatus('done')
            navigate(`/retro/${s.retrospective_id}`)
            return
          }
          if (s.state === 'FAILURE') {
            setStatus('error')
            setError(s.error ?? 'Generation failed')
            return
          }
          await new Promise((r) => setTimeout(r, 1000))
        }
        setStatus('error')
        setError('Timed out waiting for generation')
      } catch (e: any) {
        setStatus('error')
        setError(e?.message ?? 'Generation failed')
      }
    },
    onError: (e: any) => {
      setStatus('error')
      setError(e?.response?.data?.detail ?? 'Failed to create incident')
    },
  })

  return (
    <div className="mx-auto max-w-3xl p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">New Incident</h1>
          <p className="text-sm text-gray-600">Describe what happened; DevPulse will generate a retro + runbook.</p>
        </div>
        <Link className="rounded border border-gray-200 bg-white px-3 py-2 text-sm" to="/dashboard">
          Back
        </Link>
      </div>

      <div className="mb-4">
        <LLMStatusBar state={status} />
        {error && <div className="mt-2 rounded bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div>}
      </div>

      <form
        className="rounded border border-gray-200 bg-white p-4"
        onSubmit={(e) => {
          e.preventDefault()
          mutation.mutate()
        }}
      >
        <div className="mb-3">
          <label className="mb-1 block text-sm font-medium">Title</label>
          <input
            className="w-full rounded border border-gray-200 px-3 py-2"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>
        <div className="mb-3">
          <label className="mb-1 block text-sm font-medium">Description</label>
          <input
            className="w-full rounded border border-gray-200 px-3 py-2"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
          />
        </div>
        <div className="mb-3">
          <label className="mb-1 block text-sm font-medium">Severity</label>
          <select
            className="w-full rounded border border-gray-200 px-3 py-2"
            value={severity}
            onChange={(e) => setSeverity(e.target.value)}
          >
            <option value="sev0">sev0</option>
            <option value="sev1">sev1</option>
            <option value="sev2">sev2</option>
            <option value="sev3">sev3</option>
          </select>
        </div>
        <div className="mb-3">
          <label className="mb-1 block text-sm font-medium">Raw Incident Input</label>
          <textarea
            className="h-48 w-full resize-y rounded border border-gray-200 p-2 font-mono text-sm"
            value={rawInput}
            onChange={(e) => setRawInput(e.target.value)}
            placeholder="Logs, alerts, timelines, symptoms…"
            required
          />
        </div>

        <button
          className="rounded bg-gray-900 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
          type="submit"
          disabled={mutation.isPending}
        >
          {mutation.isPending ? 'Generating…' : 'Create + Generate'}
        </button>
      </form>
    </div>
  )
}
