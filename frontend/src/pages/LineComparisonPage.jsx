import { useState, useEffect } from 'react';
import { useFilters } from '../context/FilterContext';
import { fetchLineComparison } from '../api/client';
import ComparisonTable from '../components/Comparison/ComparisonTable';
import FilterPanel from '../components/Filters/FilterPanel';

function LineComparisonPage() {
  const { filters } = useFilters();
  const [data, setData] = useState({ data: [], meta: null });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load comparison data when filters change
  useEffect(() => {
    async function loadComparison() {
      setLoading(true);
      setError(null);
      try {
        const result = await fetchLineComparison({
          // Convert books array to comma-separated string, empty array means all
          books: filters.books && filters.books.length > 0 ? filters.books.join(',') : undefined,
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
  }, [filters.books, filters.team, filters.player, filters.statType]);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Line Comparison</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Compare betting lines across different sportsbooks side-by-side.
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
          Found <span className="font-semibold">{data.meta.count}</span> player props across books
        </div>
      )}

      <ComparisonTable
        data={data.data}
        loading={loading}
      />
    </div>
  );
}

export default LineComparisonPage;
