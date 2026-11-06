export interface CardShow {
  id: number
  name: string
  date: string | null // YYYY-MM-DD
  end_date?: string | null
  start_time?: string | null // HH:MM:SS
  end_time?: string | null
  venue?: string | null
  address?: string | null
  city?: string | null
  province: string
  country?: string
  postal_code?: string | null
  organizer?: string | null
  website_url?: string | null
  ticket_url?: string | null
  admission?: string | null
  table_count?: number | null
  image_url?: string | null
  description?: string | null
  tags: string[]
  lat?: number | null
  lng?: number | null
}
