import { useEffect, useMemo, useRef, useState, type MutableRefObject } from 'react'
import { Circle, MapContainer, Marker, TileLayer, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useShows } from '../lib/api'
import { dateBadge } from '../lib/format'
import { useRegion } from '../lib/region-context'
import type { CardShow } from '../lib/types'
import { RegionPicker } from '../components/RegionPicker'
import { ShowCard } from '../components/ShowCard'

/** Shows at the same spot (within ~10 m), in date order — one pin per venue. */
interface Spot {
  key: string
  lat: number
  lng: number
  shows: CardShow[]
}

function groupBySpot(shows: CardShow[]): Spot[] {
  const spots = new Map<string, Spot>()
  for (const s of shows) {
    if (s.lat == null || s.lng == null) continue
    const key = `${s.lat.toFixed(4)},${s.lng.toFixed(4)}`
    const spot = spots.get(key) ?? { key, lat: s.lat, lng: s.lng, shows: [] }
    spot.shows.push(s)
    spots.set(key, spot)
  }
  for (const spot of spots.values()) {
    spot.shows.sort((a, b) => (a.date ?? '9999').localeCompare(b.date ?? '9999'))
  }
  return [...spots.values()]
}

const pin = (spot: Spot, active: boolean) => {
  const b = dateBadge(spot.shows[0])
  const more = spot.shows.length - 1
  return L.divIcon({
    className: '',
    iconSize: [44, 44],
    iconAnchor: [22, 44],
    html: `<div style="position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;width:44px;height:44px;border-radius:14px;
      background:${active ? '#22e39a' : '#7c5cff'};color:${active ? '#0b0d14' : '#fff'};box-shadow:0 6px 20px rgba(0,0,0,.5);
      border:2px solid #0b0d14;font-family:inherit;line-height:1">
      <span style="font-size:9px;font-weight:700">${b.month}</span><span style="font-size:17px;font-weight:800">${b.day}</span>
      ${
        more > 0
          ? `<span title="${more} more date${more > 1 ? 's' : ''} here" style="position:absolute;top:-8px;right:-10px;min-width:20px;height:20px;padding:0 5px;border-radius:10px;
              background:#0b0d14;color:#fff;border:2px solid ${active ? '#22e39a' : '#7c5cff'};font-size:10px;font-weight:800;
              display:flex;align-items:center;justify-content:center;box-sizing:border-box">+${more}</span>`
          : ''
      }</div>`,
  })
}

const youAreHere = L.divIcon({
  className: '',
  iconSize: [22, 22],
  iconAnchor: [11, 11],
  html: `<div style="width:22px;height:22px;border-radius:50%;background:#3b9dff;border:3px solid #fff;
    box-shadow:0 0 0 6px rgba(59,157,255,.25),0 2px 8px rgba(0,0,0,.5)"></div>`,
})

type Fix = { lat: number; lng: number; accuracy: number }
type GeoStatus = 'idle' | 'locating' | 'ok' | 'denied' | 'unavailable'

/** Watches the device position while the map is open. */
function useMyLocation() {
  const [fix, setFix] = useState<Fix | null>(null)
  const [status, setStatus] = useState<GeoStatus>(() =>
    'geolocation' in navigator ? 'locating' : 'unavailable',
  )

  useEffect(() => {
    if (!('geolocation' in navigator)) return
    const id = navigator.geolocation.watchPosition(
      (p) => {
        setFix({ lat: p.coords.latitude, lng: p.coords.longitude, accuracy: p.coords.accuracy })
        setStatus('ok')
      },
      (err) => setStatus(err.code === err.PERMISSION_DENIED ? 'denied' : 'unavailable'),
      { enableHighAccuracy: true, maximumAge: 30_000, timeout: 20_000 },
    )
    return () => navigator.geolocation.clearWatch(id)
  }, [])

  return { fix, status }
}

/** Blue dot + accuracy ring; registers a function to pan the map to the user. */
function MyLocationLayer({ fix, flyRef }: { fix: Fix | null; flyRef: MutableRefObject<(() => void) | null> }) {
  const map = useMap()
  useEffect(() => {
    flyRef.current = fix ? () => map.flyTo([fix.lat, fix.lng], Math.max(map.getZoom(), 13)) : null
  }, [fix, map, flyRef])

  if (!fix) return null
  return (
    <>
      {fix.accuracy < 2000 && (
        <Circle
          center={[fix.lat, fix.lng]}
          radius={fix.accuracy}
          pathOptions={{ color: '#3b9dff', weight: 1, fillColor: '#3b9dff', fillOpacity: 0.12 }}
          interactive={false}
        />
      )}
      <Marker position={[fix.lat, fix.lng]} icon={youAreHere} interactive={false} zIndexOffset={-1000} />
    </>
  )
}

const LOCATE_HINT: Record<GeoStatus, string> = {
  idle: 'Show my location',
  locating: 'Finding your location…',
  ok: 'Centre on my location',
  denied: 'Location permission is blocked. Allow it in your browser settings.',
  unavailable: "Your location isn't available right now",
}

export default function MapPage() {
  const { region } = useRegion()
  const { shows } = useShows(region)
  const spots = useMemo(() => groupBySpot(shows), [shows])
  const [selected, setSelected] = useState<{ key: string; index: number } | null>(null)
  const { fix, status } = useMyLocation()
  const flyToMe = useRef<(() => void) | null>(null)
  const [hint, setHint] = useState<string | null>(null)

  const spot = selected ? spots.find((s) => s.key === selected.key) : undefined
  const show = spot?.shows[selected!.index] ?? spot?.shows[0]

  return (
    <div className="relative" style={{ height: 'calc(100dvh - 64px)' }}>
      <MapContainer
        key={region.id}
        center={region.center}
        zoom={region.zoom}
        zoomControl={false}
        className="h-full w-full"
      >
        <TileLayer
          // OSM tiles are fine for development; swap to MapTiler/Stadia (free tiers) before launch
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {spots.map((s) => (
          <Marker
            key={s.key}
            position={[s.lat, s.lng]}
            icon={pin(s, selected?.key === s.key)}
            eventHandlers={{ click: () => setSelected({ key: s.key, index: 0 }) }}
          />
        ))}
        <MyLocationLayer fix={fix} flyRef={flyToMe} />
      </MapContainer>

      <div className="pt-safe pointer-events-none absolute inset-x-0 top-0 z-[400] flex justify-center p-4">
        <div className="pointer-events-auto">
          <RegionPicker />
        </div>
      </div>

      <div className="pt-safe pointer-events-none absolute right-0 top-16 z-[400] flex flex-col items-end gap-2 p-4">
        <button
          onClick={() => {
            if (flyToMe.current) {
              flyToMe.current()
              setHint(null)
            } else {
              setHint(LOCATE_HINT[status])
            }
          }}
          title={LOCATE_HINT[status]}
          aria-label={LOCATE_HINT[status]}
          className={`pointer-events-auto grid h-11 w-11 place-items-center rounded-full bg-surface-2 shadow-lg transition active:scale-90 ${
            status === 'ok' ? 'text-[#3b9dff]' : 'text-muted'
          } ${status === 'locating' ? 'animate-pulse' : ''}`}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <circle cx="12" cy="12" r="4" fill={status === 'ok' ? 'currentColor' : 'none'} />
            <path d="M12 2v3M12 19v3M2 12h3M19 12h3" />
            <circle cx="12" cy="12" r="8" />
          </svg>
        </button>
        {hint && (
          <div
            className="pointer-events-auto max-w-[220px] rounded-xl bg-surface-2 px-3 py-2 text-xs text-muted shadow-lg"
            onClick={() => setHint(null)}
          >
            {hint}
          </div>
        )}
      </div>

      {spot && show && (
        <div className="absolute inset-x-0 bottom-0 z-[400] p-3">
          {spot.shows.length > 1 && (
            <div className="mb-2 flex gap-2 overflow-x-auto pb-1" role="tablist" aria-label="Dates at this venue">
              {spot.shows.map((s, i) => {
                const b = dateBadge(s)
                const active = s.id === show.id
                return (
                  <button
                    key={s.id}
                    role="tab"
                    aria-selected={active}
                    onClick={() => setSelected({ key: spot.key, index: i })}
                    className={`shrink-0 rounded-full px-3 py-1.5 text-xs font-bold shadow-lg transition active:scale-95 ${
                      active ? 'bg-accent-2 text-[#0b0d14]' : 'bg-surface-2 text-muted hover:text-white'
                    }`}
                  >
                    {b.month} {b.day}
                  </button>
                )
              })}
            </div>
          )}
          <div className="relative">
            <button
              onClick={() => setSelected(null)}
              className="absolute -top-3 right-2 z-10 grid h-7 w-7 place-items-center rounded-full bg-surface-2 text-sm text-muted"
              aria-label="Close"
            >
              ✕
            </button>
            <ShowCard show={show} />
          </div>
        </div>
      )}
    </div>
  )
}
