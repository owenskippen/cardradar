import { useState } from 'react'
import { REGIONS, type Region } from '../lib/regions'
import { useRegion } from '../lib/region-context'
import { IconChevronDown, IconPin } from './Icons'

export function RegionPicker() {
  const { region, setRegion } = useRegion()
  const [open, setOpen] = useState(false)

  const pick = (r: Region) => {
    if (!r.live) return
    setRegion(r)
    setOpen(false)
  }

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-1.5 rounded-full bg-surface-2 py-1.5 pr-2.5 pl-3 text-sm font-medium"
      >
        <IconPin width={15} height={15} className="text-accent-2" />
        {region.label}
        <IconChevronDown width={15} height={15} className="text-muted" />
      </button>

      {open && (
        <div className="fixed inset-0 z-[1000] flex items-end bg-black/60 sm:items-center sm:justify-center" onClick={() => setOpen(false)}>
          <div
            className="pb-safe w-full rounded-t-3xl border-t border-line bg-surface p-5 sm:max-w-sm sm:rounded-3xl sm:border"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mx-auto mb-4 h-1 w-10 rounded-full bg-line sm:hidden" />
            <h2 className="mb-3 text-lg font-bold">Choose your area</h2>
            <ul className="space-y-2">
              {REGIONS.map((r) => (
                <li key={r.id}>
                  <button
                    disabled={!r.live}
                    onClick={() => pick(r)}
                    className={`flex w-full items-center justify-between rounded-xl px-4 py-3 text-left ${
                      r.id === region.id ? 'bg-accent/20 ring-1 ring-accent' : 'bg-surface-2'
                    } ${r.live ? '' : 'opacity-50'}`}
                  >
                    <span className="font-medium">{r.label}</span>
                    {!r.live && <span className="text-xs text-muted">Coming soon</span>}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </>
  )
}
