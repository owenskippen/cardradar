import { Link } from 'react-router-dom'
import type { CardShow } from '../lib/types'
import { dateBadge, formatTimeRange, relativeDay } from '../lib/format'
import { toggleSaved, useSaved } from '../lib/saved'
import { IconBookmark, IconPin, IconTable } from './Icons'

export function SaveButton({ id, className = '' }: { id: number; className?: string }) {
  const saved = useSaved().includes(id)
  return (
    <button
      aria-label={saved ? 'Remove from saved' : 'Save show'}
      onClick={(e) => {
        e.preventDefault()
        toggleSaved(id)
      }}
      className={`grid h-9 w-9 place-items-center rounded-full transition active:scale-90 ${
        saved ? 'bg-accent text-white' : 'bg-surface-2 text-muted hover:text-white'
      } ${className}`}
    >
      <IconBookmark filled={saved} width={18} height={18} />
    </button>
  )
}

export function ShowCard({ show }: { show: CardShow }) {
  const badge = dateBadge(show)
  const rel = relativeDay(show)
  const time = formatTimeRange(show)
  const free = show.admission?.toLowerCase().includes('free entry') || show.tags.includes('free')

  return (
    <Link
      to={`/show/${show.id}`}
      className="flex gap-3 rounded-2xl border border-line bg-surface p-3 transition hover:border-accent/50 active:scale-[0.99]"
    >
      <div className="flex w-14 shrink-0 flex-col items-center justify-center rounded-xl bg-gradient-to-b from-accent/25 to-accent/5 py-2">
        <span className="text-[10px] font-bold tracking-wider text-accent">{badge.month}</span>
        <span className="text-2xl leading-none font-extrabold">{badge.day}</span>
      </div>

      <div className="min-w-0 flex-1">
        <div className="flex items-start justify-between gap-2">
          <h3 className="line-clamp-2 text-[15px] leading-snug font-semibold">{show.name}</h3>
          <SaveButton id={show.id} className="-mt-1 -mr-1 shrink-0" />
        </div>
        <p className="mt-1 flex items-center gap-1 truncate text-xs text-muted">
          <IconPin width={13} height={13} className="shrink-0" />
          <span className="truncate">{[show.venue, show.city].filter(Boolean).join(' · ')}</span>
        </p>
        <div className="mt-2 flex flex-wrap items-center gap-1.5 text-[11px] font-medium">
          {rel && <span className="rounded-full bg-accent-2/15 px-2 py-0.5 text-accent-2">{rel}</span>}
          {time && <span className="rounded-full bg-surface-2 px-2 py-0.5 text-muted">{time}</span>}
          {show.table_count != null && (
            <span className="flex items-center gap-1 rounded-full bg-surface-2 px-2 py-0.5 text-muted">
              <IconTable width={11} height={11} />
              {show.table_count} tables
            </span>
          )}
          {free && <span className="rounded-full bg-accent-2/15 px-2 py-0.5 text-accent-2">Free</span>}
        </div>
      </div>
    </Link>
  )
}
