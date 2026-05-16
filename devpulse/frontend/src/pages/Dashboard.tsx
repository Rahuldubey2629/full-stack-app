import { useMutation, useQuery } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'

import { clearTokens } from '@/api/client'
import { listIncidents } from '@/api/incidents'
import { generateRetrospective, getRetrospectiveTask } from '@/api/retrospectives'
import LLMStatusBar from '@/components/LLMStatusBar'
import SeverityBadge from '@/components/SeverityBadge'

export default function DashboardPage() {
  const navigate = useNavigate()
  const incidentsQuery = useQuery({ queryKey: ['incidents'], queryFn: listIncidents })

  const generateMutation = useMutation({
    mutationFn: async (incidentId: number) => {
      const { task_id } = await generateRetrospective(incidentId)
      return task_id
    },
    onSuccess: async (taskId) => {
      // Poll until done; keep it simple for the lab.
      for (let i = 0; i < 30; i++) {
        const status = await getRetrospectiveTask(taskId)
        if (status.state === 'SUCCESS' && status.retrospective_id) {
          navigate(`/retro/${status.retrospective_id}`)
          return
        }
        if (status.state === 'FAILURE') {
          throw new Error(status.error ?? 'Generation failed')
        }
        await new Promise((r) => setTimeout(r, 1000))
      }
      throw new Error('Timed out waiting for generation')
    },
  })

  return (
    <div className="mx-auto max-w-5xl p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Dashboard</h1>
          <p className="text-sm text-gray-600">Incidents and AI-generated retrospectives.</p>
        </div>
        <div className="flex gap-2">
          <Link
            className="rounded border border-gray-200 bg-white px-3 py-2 text-sm"
            to="/incidents/new"
          >
            New Incident
          </Link>
          <button
            className="rounded border border-gray-200 bg-white px-3 py-2 text-sm"
            type="button"
            onClick={() => {
              clearTokens()
              navigate('/login', { replace: true })
            }}
          >
            Logout
          </button>
        </div>
      </div>

      <div className="mb-4">
        <LLMStatusBar state={generateMutation.isPending ? 'generating' : 'idle'} />
        {generateMutation.isError && (
          <div className="mt-2 rounded bg-red-50 px-3 py-2 text-sm text-red-800">
            {(generateMutation.error as any)?.message ?? 'Generation failed'}
          </div>
        )}
      </div>

      <div className="rounded border border-gray-200 bg-white">
        <div className="border-b border-gray-200 px-4 py-3 text-sm font-medium">Incidents</div>

        {incidentsQuery.isLoading ? (
          <div className="p-4 text-sm text-gray-600">Loading…</div>
        ) : incidentsQuery.isError ? (
          <div className="p-4 text-sm text-red-700">Failed to load incidents.</div>
        ) : incidentsQuery.data && incidentsQuery.data.length === 0 ? (
          <div className="p-4 text-sm text-gray-600">No incidents yet.</div>
        ) : (
          <ul className="divide-y divide-gray-100">
            {incidentsQuery.data?.map((inc) => (
              <li key={inc.id} className="flex items-center justify-between gap-4 px-4 py-3">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <div className="truncate text-sm font-medium">{inc.title}</div>
                    <SeverityBadge label={inc.severity_label} />
                  </div>
                  <div className="truncate text-xs text-gray-600">{inc.description}</div>
                </div>
                <button
                  className="rounded bg-gray-900 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
                  disabled={generateMutation.isPending}
                  onClick={() => generateMutation.mutate(inc.id)}
                  type="button"
                >
                  Generate
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
