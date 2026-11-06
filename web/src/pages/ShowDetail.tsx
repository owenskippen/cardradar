import type { ReactNode } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useShow } from '../lib/api'
import { formatDateRange, formatTimeRange, mapsUrl, relativeDay } from '../lib/format'
import { downloadIcs } from '../lib/ics'
import { SaveButton } from '../components/ShowCard'
import {
  IconBack,
  IconCalendar,
  IconClock,
  IconDollar,
  IconGlobe,
  IconPin,
  IconShare,
  IconTable,
  IconTicket,
} from '../components/Icons'

function Row({ icon, label, children }: { icon: ReactNode; label: string; children: ReactNode }) {
  return (
    <div className="flex gap-3 py-3">
      <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-surface-2 text-accent">{icon}</div>
      <div className="min-w-0">
        <p className="text-xs text-muted">{label}</p>
        <div className="text-sm font-medium">{children}</div>
      </div>
    </div>
  )
}

export default function ShowDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const show = useShow(Number(id))

  if (show === undefined) return <div className="m-4 h-64 animate-pulse rounded-3xl bg-surface" />
  if (show === null)
    return (
      <div className="p-8 text-center">
        <p className="font-semibold">Show not found</p>
        <Link to="/" className="mt-3 inline-block text-accent">
          Back to Discover
        </Link>
      </div>
    )

  const rel = relativeDay(show)
  const time = formatTimeRange(show)

  const share = async () => {
    const data = { title: show.name, text: `${show.name} — ${formatDateRange(show)}`, url: location.href }
    if (navigator.share) await navigator.share(data).catch(() => {})
    else await navigator.clipboard.writeText(location.href)
  }

  return (
    <div className="pb-28">
      <div className="pt-safe relative overflow-hidden bg-gradient-to-b from-accent/50 via-accent/10 to-bg px-4 pb-6">
        {show.image_url && (
          <img src={show.image_url} alt="" className="absolute inset-0 h-full w-full object-cover opacity-30" />
        )}
        <div className="relative flex items-center justify-between pt-4">
          <button
            onClick={() => (history.length > 1 ? navigate(-1) : navigate('/'))}
            className="grid h-9 w-9 place-items-center rounded-full bg-black/30 backdrop-blur"
            aria-label="Back"
          >
            <IconBack />
          </button>
          <div className="flex gap-2">
            <button onClick={share} className="grid h-9 w-9 place-items-center rounded-full bg-black/30 backdrop-blur" aria-label="Share">
              <IconShare width={18} height={18} />
            </button>
            <SaveButton id={show.id} />
          </div>
        </div>
        <div className="relative mt-8">
          {rel && (
            <span className="rounded-full bg-accent-2/20 px-2.5 py-1 text-[11px] font-semibold tracking-wide text-accent-2 uppercase">
              {rel}
            </span>
          )}
          <h1 className="mt-3 text-2xl leading-tight font-extrabold">{show.name}</h1>
          {show.organizer && <p className="mt-1 text-sm text-white/70">by {show.organizer}</p>}
          {show.tags.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {show.tags.map((t) => (
                <span key={t} className="rounded-full bg-white/10 px-2.5 py-0.5 text-[11px] font-medium capitalize">
                  {t}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="px-4">
        <div className="divide-y divide-line rounded-2xl border border-line bg-surface px-4">
          <Row icon={<IconCalendar width={18} height={18} />} label="Date">
            {formatDateRange(show)}
          </Row>
          {time && (
            <Row icon={<IconClock width={18} height={18} />} label="Hours">
              {time}
            </Row>
          )}
          <Row icon={<IconPin width={18} height={18} />} label="Location">
            <p>{show.venue ?? 'Venue TBA'}</p>
            <p className="text-muted">{[show.address, show.city, show.province].filter(Boolean).join(', ')}</p>
            <a href={mapsUrl(show)} target="_blank" rel="noreferrer" className="mt-1 inline-block text-xs font-semibold text-accent">
              Get directions →
            </a>
          </Row>
          {show.admission && (
            <Row icon={<IconDollar width={18} height={18} />} label="Admission">
              {show.admission}
            </Row>
          )}
          {show.table_count != null && (
            <Row icon={<IconTable width={18} height={18} />} label="Vendor tables">
              {show.table_count}
            </Row>
          )}
          {show.website_url && (
            <Row icon={<IconGlobe width={18} height={18} />} label="Website">
              <a href={show.website_url} target="_blank" rel="noreferrer" className="break-all text-accent">
                {show.website_url.replace(/^https?:\/\//, '').replace(/\/$/, '')}
              </a>
            </Row>
          )}
        </div>

        {show.description && (
          <section className="mt-5">
            <h2 className="mb-2 text-xs font-bold tracking-wider text-muted uppercase">About</h2>
            <p className="text-sm leading-relaxed text-white/85">{show.description}</p>
          </section>
        )}
      </div>

      {/* sticky action bar sits above the tab bar */}
      <div className="fixed inset-x-0 bottom-[64px] z-[450] border-t border-line bg-bg/95 p-3 backdrop-blur-lg">
        <div className="mx-auto flex max-w-xl gap-2">
          <button
            onClick={() => downloadIcs(show)}
            className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-surface-2 py-3 text-sm font-semibold"
          >
            <IconCalendar width={18} height={18} /> Add to calendar
          </button>
          {(show.ticket_url ?? show.website_url) && (
            <a
              href={(show.ticket_url ?? show.website_url)!}
              target="_blank"
              rel="noreferrer"
              className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-accent py-3 text-sm font-semibold"
            >
              <IconTicket width={18} height={18} /> {show.ticket_url ? 'Get tickets' : 'Visit site'}
            </a>
          )}
        </div>
      </div>
    </div>
  )
}
