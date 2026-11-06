import { NavLink, Outlet } from 'react-router-dom'
import { IconBookmark, IconCompass, IconMap } from './Icons'

const tabs = [
  { to: '/', label: 'Discover', Icon: IconCompass },
  { to: '/map', label: 'Map', Icon: IconMap },
  { to: '/saved', label: 'Saved', Icon: IconBookmark },
]

export function Layout() {
  return (
    <div className="mx-auto flex h-full max-w-xl flex-col">
      <main className="flex-1 overflow-y-auto pb-24">
        <Outlet />
      </main>

      <nav className="pb-safe fixed inset-x-0 bottom-0 z-[500] border-t border-line bg-bg/90 backdrop-blur-lg">
        <ul className="mx-auto flex max-w-xl">
          {tabs.map(({ to, label, Icon }) => (
            <li key={to} className="flex-1">
              <NavLink
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  `flex flex-col items-center gap-1 py-2.5 text-[11px] font-medium transition ${
                    isActive ? 'text-accent' : 'text-muted hover:text-white'
                  }`
                }
              >
                <Icon />
                {label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  )
}
