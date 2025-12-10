import { Routes, Route } from 'react-router-dom'
import { FilterProvider } from './context/FilterContext'
import Header from './components/Layout/Header'
import Footer from './components/Layout/Footer'
import HomePage from './pages/HomePage'
import LinesPage from './pages/LinesPage'
import DiscrepanciesPage from './pages/DiscrepanciesPage'

function App() {
  return (
    <FilterProvider>
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1 container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/lines" element={<LinesPage />} />
            <Route path="/discrepancies" element={<DiscrepanciesPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </FilterProvider>
  )
}

export default App
