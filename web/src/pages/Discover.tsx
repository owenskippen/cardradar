import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useShows } from '../lib/api'
import { formatDateRange, formatTimeRange, monthKey, parseDate, relativeDay, todayIso } from '../lib/format'
import { useRegion } from '../lib/region-context'
import type { CardShow } from '../lib/types'
import { RegionPicker } from '../components/RegionPicker'
import { SaveButton, ShowCard } from '../components/ShowCard'
import { IconPin, IconSearch, IconTable } from '../components/Icons'

type FilterId = 'all' | 'weekend' | 'month' | 'pokemon' | 'free' | 'big'

const FILTERS: { id: FilterId; label: string }[] = [
  { id: 'all', label: 'All' },
  { id: 'weekend', label: 'This weekend' },
  { id: 'month', label: 'Next 30 days' },
  { id: 'pokemon', label: 'Pokémon' },
  { id: 'free', label: 'Free entry' },
  { id: 'big', label: '100+ tables' },
]

function matches(s: CardShow, f: FilterId): boolean {
  const today = parseDate(todayIso())
  const start = s.date ? parseDate(s.date) : null
  const end = s.end_date ? parseDate(s.end_date) : start
  switch (f) {
    case 'weekend': {
      if (!start || !end) return false
      const dow = today.getDay()
      const sat = new Date(today)
      sat.setDate(today.getDate() + (dow === 0 ? -1 : 6 - dow)) // on Sunday, "this weekend" = yesterday + today
      const sun = new Date(sat)
      sun.setDate(sat.getDate() + 1)
      return start <= sun && end >= sat
    }
    case 'month': {
      if (!start) return false
      const lim = new Date(today)
      lim.setDate(today.getDate() + 30)
      return start <= lim
    }
    case 'pokemon':
      return s.tags.some((t) => t.toLowerCase().includes('pok'))
    case 'free':
      return !!s.admission?.toLowerCase().includes('free entry') || s.tags.includes('free')
    case 'big':
      return (s.table_count ?? 0) >= 100
    default:
      return true
  }
}

function FeaturedCard({ show }: { show: CardShow }) {
  const rel = relativeDay(show)
  return (
    <Link
      to={`/show/${show.id}`}
      className="relative block overflow-hidden rounded-3xl border border-accent/30 bg-gradient-to-br from-accent/40 via-surface to-surface p-5"
    >
      <div className="absolute -top-10 -right-10 h-40 w-40 rounded-full bg-accent-2/20 blur-3xl" />
      <div className="relative">
        <div className="flex items-center justify-between">
          <span className="rounded-full bg-black/30 px-2.5 py-1 text-[11px] font-semibold tracking-wide text-accent-2 uppercase">
            {rel ?? 'Next up'}
          </span>
          <SaveButton id={show.id} />
        </div>
        <h2 className="mt-3 text-xl leading-tight font-bold">{show.name}</h2>
        <p className="mt-1 text-sm text-white/80">
          {formatDateRange(show)}
          {formatTimeRange(show) && ` · ${formatTimeRange(show)}`}
        </p>
        <div className="mt-4 flex flex-wrap gap-3 text-xs text-white/80">
          <span className="flex items-center gap-1">
            <IconPin width={14} height={14} />
            {[show.venue, show.city].filter(Boolean).join(', ')}
          </span>
          {show.table_count != null && (
            <span className="flex items-center gap-1">
              <IconTable width={14} height={14} />
              {show.table_count} tables
            </span>
          )}
        </div>
      </div>
    </Link>
  )
}

export default function Discover() {
  const { region } = useRegion()
  const { shows, loading, demo } = useShows(region)
  const [filter, setFilter] = useState<FilterId>('all')
  const [q, setQ] = useState('')

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase()
    return shows
      .filter((s) => matches(s, filter))
      .filter(
        (s) =>
          !needle ||
          [s.name, s.venue, s.city, s.organizer, ...s.tags].some((v) => v?.toLowerCase().includes(needle)),
      )
      .sort((a, b) => (a.date ?? '9999').localeCompare(b.date ?? '9999'))
  }, [shows, filter, q])

  const [featured, ...rest] = filtered
  const groups = useMemo(() => {
    const m = new Map<string, CardShow[]>()
    for (const s of rest) m.set(monthKey(s), [...(m.get(monthKey(s)) ?? []), s])
    return [...m.entries()]
  }, [rest])

  return (
    <div className="pt-safe">
      <header className="sticky top-0 z-10 bg-bg/90 px-4 pt-4 pb-3 backdrop-blur-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <img src="/favicon.svg" alt="" className="h-8 w-8" />
            <span className="text-lg font-extrabold tracking-tight">
              Card<span className="text-accent">Radar</span>
            </span>
          </div>
          <RegionPicker />
        </div>

        <label className="mt-4 flex items-center gap-2 rounded-xl border border-line bg-surface px-3 py-2.5 focus-within:border-accent">
          <IconSearch width={18} height={18} className="text-muted" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search shows, venues, games…"
            className="w-full bg-transparent text-sm outline-none placeholder:text-muted"
          />
        </label>

        <div className="no-scrollbar -mx-4 mt-3 flex gap-2 overflow-x-auto px-4">
          {FILTERS.map((f) => (
            <button
              key={f.id}
              onClick={() => setFilter(f.id)}
              className={`shrink-0 rounded-full px-3.5 py-1.5 text-xs font-semibold transition ${
                filter === f.id ? 'bg-white text-bg' : 'bg-surface-2 text-muted hover:text-white'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </header>

      <div className="space-y-6 px-4 pt-2">
        {demo && (
          <p className="rounded-xl border border-yellow-500/30 bg-yellow-500/10 px-3 py-2 text-xs text-yellow-200">
            Showing demo data — the API isn’t connected yet.
          </p>
        )}

        {loading ? (
          <div className="space-y-3">
            {[0, 1, 2].map((i) => (
              <div key={i} className="h-24 animate-pulse rounded-2xl bg-surface" />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="py-16 text-center">
            <p className="text-4xl">🃏</p>
            <p className="mt-3 font-semibold">No shows found</p>
            <p className="mt-1 text-sm text-muted">Try a different filter or area.</p>
          </div>
        ) : (
          <>
            {featured && <FeaturedCard show={featured} />}
            {groups.map(([month, list]) => (
              <section key={month}>
                <h2 className="mb-2 text-xs font-bold tracking-wider text-muted uppercase">{month}</h2>
                <div className="space-y-2.5">
                  {list.map((s) => (
                    <ShowCard key={s.id} show={s} />
                  ))}
                </div>
              </section>
            ))}
          </>
        )}
      </div>
    </div>
  )
}
