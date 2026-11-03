import { useSyncExternalStore } from 'react'

const KEY = 'cardradar:saved'
const listeners = new Set<() => void>()
let cache: number[] = JSON.parse(localStorage.getItem(KEY) ?? '[]')

const subscribe = (fn: () => void) => {
  listeners.add(fn)
  return () => {
    listeners.delete(fn)
  }
}

export function toggleSaved(id: number) {
  cache = cache.includes(id) ? cache.filter((x) => x !== id) : [...cache, id]
  localStorage.setItem(KEY, JSON.stringify(cache))
  listeners.forEach((fn) => fn())
}

export const useSaved = () => useSyncExternalStore(subscribe, () => cache)
