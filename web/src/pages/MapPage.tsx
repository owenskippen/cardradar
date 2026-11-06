import { useState } from 'react'
import { MapContainer, Marker, TileLayer } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useShows } from '../lib/api'
import { dateBadge } from '../lib/format'
import { useRegion } from '../lib/region-context'
import type { CardShow } from '../lib/types'
import { RegionPicker } from '../components/RegionPicker'
import { ShowCard } from '../components/ShowCard'

const pin = (s: CardShow, active: boolean) => {
  const b = dateBadge(s)
  return L.divIcon({
    className: '',
    iconSize: [44, 44],
    iconAnchor: [22, 44],
    html: `<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;width:44px;height:44px;border-radius:14px;
      background:${active ? '#22e39a' : '#7c5cff'};color:${active ? '#0b0d14' : '#fff'};box-shadow:0 6px 20px rgba(0,0,0,.5);
      border:2px solid #0b0d14;font-family:inherit;line-height:1">
      <span style="font-size:9px;font-weight:700">${b.month}</span><span style="font-size:17px;font-weight:800">${b.day}</span></div>`,
  })
}

export default function MapPage() {
  const { region } = useRegion()
  const { shows } = useShows(region)
  const [selected, setSelected] = useState<CardShow | null>(null)
  const located = shows.filter((s) => s.lat != null && s.lng != null)

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
        {located.map((s) => (
          <Marker
            key={s.id}
            position={[s.lat!, s.lng!]}
            icon={pin(s, selected?.id === s.id)}
            eventHandlers={{ click: () => setSelected(s) }}
          />
        ))}
      </MapContainer>

      <div className="pt-safe pointer-events-none absolute inset-x-0 top-0 z-[400] flex justify-center p-4">
        <div className="pointer-events-auto">
          <RegionPicker />
        </div>
      </div>

      {selected && (
        <div className="absolute inset-x-0 bottom-0 z-[400] p-3">
          <div className="relative">
            <button
              onClick={() => setSelected(null)}
              className="absolute -top-3 right-2 z-10 grid h-7 w-7 place-items-center rounded-full bg-surface-2 text-sm text-muted"
              aria-label="Close"
            >
              ✕
            </button>
            <ShowCard show={selected} />
          </div>
        </div>
      )}
    </div>
  )
}
