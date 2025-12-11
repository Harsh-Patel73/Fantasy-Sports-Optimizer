import { useState, useEffect } from 'react';
import { useFilters } from '../context/FilterContext';
import { fetchLineComparison, fetchBooks } from '../api/client';
import FilterPanel from '../components/Filters/FilterPanel';
import ComparisonTable from '../components/Comparison/ComparisonTable';

function LineComparisonPage() {
  const { filters } = useFilters();
  const [primaryBook, setPrimaryBook] = useState('PrizePicks');
  const [books, setBooks] = useState([]);
  const [data, setData] = useState({ data: [], meta: null });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load available books
  useEffect(() => {
    fetchBooks()
      .then((bookList) => {
        setBooks(bookList);
        // Set default primary book if available
        if (bookList.length > 0 && !bookList.find(b => b.name === primaryBook)) {
          setPrimaryBook(bookList[0].name);
        }
      })
      .catch(console.error);
  }, []);

  // Load comparison data
  useEffect(() => {
    async function loadComparison() {
      if (!primaryBook) return;

      setLoading(true);
      setError(null);
      try {
        const result = await fetchLineComparison({
          primary_book: primaryBook,
          team: filters.team || undefined,
          player: filters.player || undefined,
          stat_type: filters.statType || undefined,
        });
        setData(result);
      } catch (err) {
        setError('Failed to load line comparison.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadComparison();
  }, [primaryBook, filters.team, filters.player, filters.statType]);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Line Comparison</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Compare betting lines across different books side-by-side.
          Select your primary book and see how other books differ.
        </p>
      </div>

      {/* Primary Book Selector */}
      <div className="card mb-6">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Primary Book (Your Betting Platform)
        </label>
        <select
          value={primaryBook}
          onChange={(e) => setPrimaryBook(e.target.value)}
          className="select-field max-w-xs"
        >
          {books.map((book) => (
            <option key={book.id || book.name} value={book.name}>
              {book.name} {book.type === 'Fantasy' ? '(Fantasy)' : '(Sportsbook)'}
            </option>
          ))}
        </select>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
          This will show lines from {primaryBook} and compare them to other available books.
        </p>
      </div>

      <FilterPanel />

      {error && (
        <div className="card bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 mb-6">
          {error}
        </div>
      )}

      {data.meta && !loading && (
        <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
          Found <span className="font-semibold">{data.meta.count}</span> lines with matches across multiple books
        </div>
      )}

      <ComparisonTable
        data={data.data}
        loading={loading}
        primaryBook={primaryBook}
      />
    </div>
  );
}

export default LineComparisonPage;
