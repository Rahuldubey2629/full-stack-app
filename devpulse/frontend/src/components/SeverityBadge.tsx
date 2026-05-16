export default function SeverityBadge({ label }: { label: string }) {
  const normalized = label.trim().toLowerCase()
  const base = 'inline-flex items-center rounded px-2 py-0.5 text-xs font-medium'

  const cls =
    normalized === 'sev0'
      ? 'bg-red-100 text-red-800'
      : normalized === 'sev1'
        ? 'bg-orange-100 text-orange-800'
        : normalized === 'sev2'
          ? 'bg-yellow-100 text-yellow-800'
          : 'bg-gray-100 text-gray-800'

  return <span className={`${base} ${cls}`}>{label}</span>
}
