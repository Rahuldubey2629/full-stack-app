export default function LLMStatusBar({
  state,
  tokenCount,
}: {
  state: 'idle' | 'generating' | 'done' | 'error'
  tokenCount?: number
}) {
  const text =
    state === 'idle'
      ? 'Idle'
      : state === 'generating'
        ? `Generating…${typeof tokenCount === 'number' ? ` (${tokenCount} tokens)` : ''}`
        : state === 'done'
          ? 'Done'
          : 'Error'

  const cls =
    state === 'generating'
      ? 'bg-blue-50 text-blue-800'
      : state === 'done'
        ? 'bg-green-50 text-green-800'
        : state === 'error'
          ? 'bg-red-50 text-red-800'
          : 'bg-gray-50 text-gray-800'

  return (
    <div className={`w-full rounded border border-gray-200 px-3 py-2 text-sm ${cls}`}>{text}</div>
  )
}
