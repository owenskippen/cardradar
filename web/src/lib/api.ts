import { useEffect, useState } from 'react'
import type { CardShow } from './types'
import type { Region } from './regions'
import { todayIso } from './format'
import { SAMPLE_SHOWS } from './sample'

const API = import.meta.env.VITE_API_URL ?? ''

function inRegion(s: CardShow, r: Region) {
  if (s.province !== r.province) return false
  return r.cities.length === 0 || (!!s.city && r.cities.includes(s.city))
}

/**
 * Loads upcoming shows for a region. Falls back to bundled demo data when the
 * backend isn't reachable so the UI can be developed on its own.
 */
export function useShows(region: Region) {
  const [shows, setShows] = useState<CardShow[]>([])
  const [loading, setLoading] = useState(true)
  const [demo, setDemo] = useState(false)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    const today = todayIso()
    const params = new URLSearchParams({
      province: region.province,
      country: region.country,
      start_date: today,
      limit: '200',
    })
    fetch(`${API}/api/events?${params}`)
      .then((r) => {
        if (!r.ok) throw new Error(String(r.status))
        return r.json() as Promise<CardShow[]>
      })
      .then((data) => {
        if (cancelled) return
        setShows(data.filter((s) => inRegion(s, region)))
        setDemo(false)
      })
      .catch(() => {
        if (cancelled) return
        setShows(SAMPLE_SHOWS.filter((s) => inRegion(s, region) && (s.end_date ?? s.date ?? today) >= today))
        setDemo(true)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [region])

  return { shows, loading, demo }
}

export function useShow(id: number) {
  const [show, setShow] = useState<CardShow | null | undefined>(undefined)
  useEffect(() => {
    fetch(`${API}/api/events/${id}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setShow)
      .catch(() => setShow(SAMPLE_SHOWS.find((s) => s.id === id) ?? null))
  }, [id])
  return show
}

/** All shows (any region) — used by the Saved tab. */
export function useAllShows() {
  const [shows, setShows] = useState<CardShow[]>([])
  useEffect(() => {
    fetch(`${API}/api/events?limit=200`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setShows)
      .catch(() => setShows(SAMPLE_SHOWS))
  }, [])
  return shows
}
