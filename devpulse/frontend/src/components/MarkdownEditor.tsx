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
  const [mode, setMode] = React.useState<'edit' | 'preview'>(readOnly ? 'preview' : 'edit')

  return (
    <div className="w-full rounded border border-gray-200 bg-white">
      <div className="flex items-center justify-between border-b border-gray-200 px-3 py-2">
        <div className="text-sm font-medium">Markdown</div>
        <div className="flex gap-2">
          {!readOnly && (
            <button
              className={`rounded px-2 py-1 text-sm ${mode === 'edit' ? 'bg-gray-900 text-white' : 'bg-gray-100'}`}
              onClick={() => setMode('edit')}
              type="button"
            >
              Edit
            </button>
          )}
          <button
            className={`rounded px-2 py-1 text-sm ${mode === 'preview' ? 'bg-gray-900 text-white' : 'bg-gray-100'}`}
            onClick={() => setMode('preview')}
            type="button"
          >
            Preview
          </button>
        </div>
      </div>

      <div className="p-3">
        {mode === 'edit' && !readOnly ? (
          <textarea
            className="h-64 w-full resize-y rounded border border-gray-200 p-2 font-mono text-sm"
            value={value}
            onChange={(e) => onChange?.(e.target.value)}
          />
        ) : (
          <div className="prose max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{value || '—'}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  )
}
