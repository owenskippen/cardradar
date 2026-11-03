import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { RegionProvider } from './lib/region-context'
import Discover from './pages/Discover'
import MapPage from './pages/MapPage'
import Saved from './pages/Saved'
import ShowDetail from './pages/ShowDetail'

export default function App() {
  return (
    <RegionProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<Discover />} />
            <Route path="map" element={<MapPage />} />
            <Route path="saved" element={<Saved />} />
            <Route path="show/:id" element={<ShowDetail />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </RegionProvider>
  )
}
