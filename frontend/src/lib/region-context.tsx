import { createContext, useContext, useState, type ReactNode } from 'react'
import { DEFAULT_REGION, REGIONS, type Region } from './regions'

const KEY = 'cardradar:region'

const Ctx = createContext<{ region: Region; setRegion: (r: Region) => void }>({
  region: DEFAULT_REGION,
  setRegion: () => {},
})

export function RegionProvider({ children }: { children: ReactNode }) {
  const [region, setRegionState] = useState<Region>(
    () => REGIONS.find((r) => r.id === localStorage.getItem(KEY) && r.live) ?? DEFAULT_REGION,
  )
  const setRegion = (r: Region) => {
    localStorage.setItem(KEY, r.id)
    setRegionState(r)
  }
  return <Ctx.Provider value={{ region, setRegion }}>{children}</Ctx.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export const useRegion = () => useContext(Ctx)
