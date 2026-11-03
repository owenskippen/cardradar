import type { CardShow } from './types'

const pad = (n: number) => String(n).padStart(2, '0')
const stamp = (date: string, time?: string | null) => {
  const d = date.replace(/-/g, '')
  return time ? `${d}T${time.slice(0, 5).replace(':', '')}00` : d
}
const esc = (v: string) => v.replace(/[,;\\]/g, (c) => `\\${c}`).replace(/\n/g, '\\n')

/** Download an .ics file so the show lands in the user's phone calendar. */
export function downloadIcs(s: CardShow) {
  if (!s.date) return
  const allDay = !s.start_time
  const endDate = s.end_date ?? s.date
  let dtEnd: string
  if (allDay) {
    const [y, m, d] = endDate.split('-').map(Number)
    const next = new Date(y, m - 1, d + 1)
    dtEnd = `${next.getFullYear()}${pad(next.getMonth() + 1)}${pad(next.getDate())}`
  } else {
    dtEnd = stamp(endDate, s.end_time ?? s.start_time)
  }
  const now = new Date().toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z'
  const lines = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//CardRadar//EN',
    'BEGIN:VEVENT',
    `UID:cardradar-${s.id}@cardradar`,
    `DTSTAMP:${now}`,
    allDay ? `DTSTART;VALUE=DATE:${stamp(s.date)}` : `DTSTART:${stamp(s.date, s.start_time)}`,
    allDay ? `DTEND;VALUE=DATE:${dtEnd}` : `DTEND:${dtEnd}`,
    `SUMMARY:${esc(s.name)}`,
    `LOCATION:${esc([s.venue, s.address, s.city].filter(Boolean).join(', '))}`,
    s.website_url ? `URL:${s.website_url}` : '',
    s.description ? `DESCRIPTION:${esc(s.description)}` : '',
    'END:VEVENT',
    'END:VCALENDAR',
  ].filter(Boolean)
  const blob = new Blob([lines.join('\r\n')], { type: 'text/calendar' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `${s.name.replace(/[^a-z0-9]+/gi, '-').toLowerCase()}.ics`
  a.click()
  URL.revokeObjectURL(a.href)
}
