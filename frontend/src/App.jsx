import { Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import { FilterProvider } from './context/FilterContext'
import Header from './components/Layout/Header'
import Footer from './components/Layout/Footer'
import HomePage from './pages/HomePage'
import LinesPage from './pages/LinesPage'
import DiscrepanciesPage from './pages/DiscrepanciesPage'
import LineComparisonPage from './pages/LineComparisonPage'
import ParlayBuilderPage from './pages/ParlayBuilderPage'
import CalculatorsPage from './pages/CalculatorsPage'

function App() {
  return (
    <ThemeProvider>
      <FilterProvider>
        <div className="min-h-screen flex flex-col bg-gray-100 dark:bg-gray-900 transition-colors">
        <Header />
        <main className="flex-1 container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/lines" element={<LinesPage />} />
            <Route path="/discrepancies" element={<DiscrepanciesPage />} />
            <Route path="/compare" element={<LineComparisonPage />} />
            <Route path="/parlay" element={<ParlayBuilderPage />} />
            <Route path="/calculators" element={<CalculatorsPage />} />
          </Routes>
        </main>
        <Footer />
        </div>
      </FilterProvider>
    </ThemeProvider>
  )
}

export default App
