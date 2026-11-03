export interface Region {
  id: string
  label: string
  province: string
  country: 'CA' | 'US'
  /** cities that belong to this region; empty = whole province/state */
  cities: string[]
  center: [number, number]
  zoom: number
  live: boolean
}

// Launch region first; the others are placeholders so the expansion path is built in.
export const REGIONS: Region[] = [
  {
    id: 'metro-van',
    label: 'Vancouver & Richmond',
    province: 'BC',
    country: 'CA',
    cities: ['Vancouver', 'Richmond', 'Burnaby', 'Surrey', 'Coquitlam', 'New Westminster', 'North Vancouver', 'Langley', 'Delta'],
    center: [49.22, -123.05],
    zoom: 10,
    live: true,
  },
  { id: 'bc', label: 'All of BC', province: 'BC', country: 'CA', cities: [], center: [49.6, -123.4], zoom: 7, live: true },
  { id: 'ab', label: 'Alberta', province: 'AB', country: 'CA', cities: [], center: [52.3, -113.8], zoom: 6, live: false },
  { id: 'gta', label: 'Toronto / GTA', province: 'ON', country: 'CA', cities: [], center: [43.7, -79.4], zoom: 9, live: false },
  { id: 'wa', label: 'Seattle / WA', province: 'WA', country: 'US', cities: [], center: [47.6, -122.3], zoom: 8, live: false },
]

export const DEFAULT_REGION = REGIONS[0]
