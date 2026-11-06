import type { CardShow } from './types'

export const parseDate = (d: string) => {
  const [y, m, day] = d.split('-').map(Number)
  return new Date(y, m - 1, day)
}

export const todayIso = () => {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

export const showStart = (s: CardShow) => (s.date ? parseDate(s.date) : null)

export function formatDateRange(s: CardShow): string {
  if (!s.date) return 'Date TBA'
  const start = parseDate(s.date)
  const opts: Intl.DateTimeFormatOptions = { weekday: 'short', month: 'short', day: 'numeric' }
  if (s.end_date && s.end_date !== s.date) {
    const end = parseDate(s.end_date)
    return `${start.toLocaleDateString(undefined, opts)} – ${end.toLocaleDateString(undefined, opts)}`
  }
  return start.toLocaleDateString(undefined, { ...opts, weekday: 'long' })
}

export function formatTime(t?: string | null): string | null {
  if (!t) return null
  const [h, m] = t.split(':').map(Number)
  const d = new Date()
  d.setHours(h, m)
  return d.toLocaleTimeString(undefined, { hour: 'numeric', minute: m ? '2-digit' : undefined })
}

export function formatTimeRange(s: CardShow): string | null {
  const a = formatTime(s.start_time)
  const b = formatTime(s.end_time)
  if (a && b) return `${a} – ${b}`
  return a
}

export function dateBadge(s: CardShow) {
  const d = showStart(s)
  if (!d) return { month: 'TBA', day: '?' }
  return {
    month: d.toLocaleDateString(undefined, { month: 'short' }).toUpperCase(),
    day: String(d.getDate()),
  }
}

/** "Happening now", "Tomorrow", "In 5 days", or null if further out */
export function relativeDay(s: CardShow): string | null {
  const d = showStart(s)
  if (!d) return null
  const today = parseDate(todayIso())
  const diff = Math.round((d.getTime() - today.getTime()) / 86_400_000)
  const endDiff = s.end_date ? Math.round((parseDate(s.end_date).getTime() - today.getTime()) / 86_400_000) : diff
  if (diff <= 0 && endDiff >= 0) return 'Happening now'
  if (diff === 1) return 'Tomorrow'
  if (diff > 1 && diff <= 7) return `In ${diff} days`
  return null
}

export const monthKey = (s: CardShow) => {
  const d = showStart(s)
  return d ? d.toLocaleDateString(undefined, { month: 'long', year: 'numeric' }) : 'Date TBA'
}

export const mapsUrl = (s: CardShow) =>
  `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
    [s.venue, s.address, s.city, s.province].filter(Boolean).join(', '),
  )}`
