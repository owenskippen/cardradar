import { Link } from 'react-router-dom'
import { useAllShows } from '../lib/api'
import { useSaved } from '../lib/saved'
import { ShowCard } from '../components/ShowCard'

export default function Saved() {
  const saved = useSaved()
  const shows = useAllShows()
    .filter((s) => saved.includes(s.id))
    .sort((a, b) => (a.date ?? '9999').localeCompare(b.date ?? '9999'))

  return (
    <div className="pt-safe px-4 pt-6">
      <h1 className="text-2xl font-extrabold">Saved shows</h1>
      <p className="mt-1 text-sm text-muted">Shows you’ve bookmarked, soonest first.</p>

      {shows.length === 0 ? (
        <div className="py-20 text-center">
          <p className="text-4xl">🔖</p>
          <p className="mt-3 font-semibold">Nothing saved yet</p>
          <p className="mt-1 text-sm text-muted">Tap the bookmark on any show to keep it here.</p>
          <Link to="/" className="mt-5 inline-block rounded-full bg-accent px-5 py-2.5 text-sm font-semibold">
            Find shows
          </Link>
        </div>
      ) : (
        <div className="mt-5 space-y-2.5">
          {shows.map((s) => (
            <ShowCard key={s.id} show={s} />
          ))}
        </div>
      )}
    </div>
  )
}
