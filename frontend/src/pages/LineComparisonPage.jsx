import { useState, useEffect, useMemo } from 'react';
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

  // Apply client-side search filtering
  const filteredData = useMemo(() => {
    if (!filters.search || !data.data) return data.data;

    const searchLower = filters.search.toLowerCase();
    return data.data.filter(row =>
      row.player_name?.toLowerCase().includes(searchLower) ||
      row.stat_type?.toLowerCase().includes(searchLower) ||
      row.matchup?.toLowerCase().includes(searchLower) ||
      row.lines?.some(line => line.book?.toLowerCase().includes(searchLower))
    );
  }, [data.data, filters.search]);

  // Get selected books for column display
  const selectedBooks = filters.books && filters.books.length > 0 ? filters.books : null;

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Line Comparison</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Compare betting lines across different sportsbooks side-by-side.
        </p>
      </div>

      <FilterPanel showSearch={true} />

      {error && (
        <div className="card bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 mb-6">
          {error}
        </div>
      )}

      {data.meta && !loading && (
        <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
          Found <span className="font-semibold">{filteredData.length}</span> player props across books
          {filters.search && ` (filtered from ${data.meta.count})`}
        </div>
      )}

      <ComparisonTable
        data={filteredData}
        loading={loading}
        selectedBooks={selectedBooks}
      />
    </div>
  );
}

export default LineComparisonPage;
