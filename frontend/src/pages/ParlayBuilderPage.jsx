import { useState, useEffect } from 'react';
import { ParlayProvider, useParlay } from '../context/ParlayContext';
import { fetchEVLines } from '../api/client';
import ParlayConfig from '../components/Parlay/ParlayConfig';
import EVLinesList from '../components/Parlay/EVLinesList';
import ManualLineSelector from '../components/Parlay/ManualLineSelector';
import SelectedParlay from '../components/Parlay/SelectedParlay';

function ParlayBuilderContent() {
  const { parlayState, setMode } = useParlay();
  const [evLines, setEvLines] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load EV lines when in auto mode
  useEffect(() => {
    if (parlayState.mode === 'auto') {
      loadEVLines();
    }
  }, [
    parlayState.bettingBook,
    parlayState.sharpBooks,
    parlayState.parlayType,
    parlayState.mode
  ]);

  async function loadEVLines() {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchEVLines({
        betting_book: parlayState.bettingBook,
        sharp_books: parlayState.sharpBooks.join(','),
        parlay_type: parlayState.parlayType,
      });
      setEvLines(result.data || []);
    } catch (err) {
      console.error('Failed to load EV lines:', err);
      setError('Failed to load +EV lines. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Parlay Builder</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Build +EV parlays by comparing lines against sharp books.
          Lines with odds better than the break-even threshold are highlighted.
        </p>
      </div>

      <ParlayConfig />

      {/* Mode Toggle */}
      <div className="card mb-6">
        <div className="flex items-center justify-between">
          <div className="flex space-x-2">
            <button
              onClick={() => setMode('auto')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                parlayState.mode === 'auto'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
              }`}
            >
              Auto-Generate +EV Lines
            </button>
            <button
              onClick={() => setMode('manual')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                parlayState.mode === 'manual'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
              }`}
            >
              Manual Selection
            </button>
          </div>

          <div className="text-sm text-gray-600 dark:text-gray-400">
            {parlayState.mode === 'auto' ? (
              <span>Showing lines where sharp odds beat the break-even threshold</span>
            ) : (
              <span>Browse all lines and validate against sharp books</span>
            )}
          </div>
        </div>
      </div>

      {error && (
        <div className="card bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 mb-6">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          {parlayState.mode === 'auto' ? (
            <EVLinesList lines={evLines} loading={loading} />
          ) : (
            <ManualLineSelector />
          )}
        </div>
        <div>
          <SelectedParlay />
        </div>
      </div>

      {/* Help Info */}
      <div className="mt-6 card bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
        <h4 className="font-medium text-blue-900 dark:text-blue-300 mb-2">How it works</h4>
        <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-1 list-disc ml-4">
          <li>
            <strong>+EV (Positive Expected Value)</strong>: A line is +EV when sharp books
            imply a lower probability than the parlay's break-even requirement.
          </li>
          <li>
            <strong>Edge</strong>: The difference between the break-even probability and
            the sharp book's implied probability. Higher edge = better value.
          </li>
          <li>
            <strong>Sharp Books</strong>: Books known for accurate pricing (Pinnacle, etc.).
            Their odds reflect true probabilities more accurately.
          </li>
        </ul>
      </div>
    </div>
  );
}

function ParlayBuilderPage() {
  return (
    <ParlayProvider>
      <ParlayBuilderContent />
    </ParlayProvider>
  );
}

export default ParlayBuilderPage;
