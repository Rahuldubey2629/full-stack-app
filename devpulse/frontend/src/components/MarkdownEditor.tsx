import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

export default function MarkdownEditor({
  value,
  onChange,
  readOnly,
}: {
  value: string
  onChange?: (next: string) => void
  readOnly?: boolean
}) {
  const [mode, setMode] = React.useState<'markdown' | 'preview'>('preview')

  return (
    <div className="w-full rounded border border-gray-200 bg-white">
      <div className="flex items-center justify-between border-b border-gray-200 px-3 py-2">
        <div className="flex gap-2">
          <button
            className={`rounded px-2 py-1 text-sm ${mode === 'markdown' ? 'bg-gray-900 text-white' : 'bg-gray-100'}`}
            onClick={() => setMode('markdown')}
            type="button"
          >
            Markdown
          </button>
          <button
            className={`rounded px-2 py-1 text-sm ${mode === 'preview' ? 'bg-gray-900 text-white' : 'bg-gray-100'}`}
            onClick={() => setMode('preview')}
            type="button"
          >
            Preview
          </button>
        </div>
        <div className="flex gap-2">
          {!readOnly && <div className="text-sm text-gray-500">Edit enabled</div>}
        </div>
      </div>

      <div className="p-3">
        {mode === 'markdown' ? (
          readOnly ? (
            <pre className="max-h-[26rem] overflow-auto whitespace-pre-wrap rounded border border-gray-200 bg-white p-2 font-mono text-sm">
              {value || '—'}
            </pre>
          ) : (
            <textarea
              className="h-64 w-full resize-y rounded border border-gray-200 p-2 font-mono text-sm"
              value={value}
              onChange={(e) => onChange?.(e.target.value)}
            />
          )
        ) : (
          <div className="prose max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{value || '—'}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  )
}
