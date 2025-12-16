import { useState, useEffect, useMemo } from 'react';
import { useFilters } from '../context/FilterContext';
import { fetchDiscrepancies } from '../api/client';
import FilterPanel from '../components/Filters/FilterPanel';
import DiscrepancyTable from '../components/Discrepancies/DiscrepancyTable';

function DiscrepanciesPage() {
  const { filters } = useFilters();
  const [data, setData] = useState({ data: [], meta: null });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadDiscrepancies() {
      setLoading(true);
      setError(null);

      try {
        const result = await fetchDiscrepancies({
          min_prob_diff: filters.minProbDiff,
          stat_type: filters.statType || undefined,
          player: filters.player || undefined,
          team: filters.team || undefined,
          books: filters.books && filters.books.length > 0 ? filters.books.join(',') : undefined,
        });
        setData(result);
      } catch (err) {
        console.error('Failed to load discrepancies:', err);
        setError('Failed to load discrepancies. Please try again.');
      } finally {
        setLoading(false);
      }
    }

    loadDiscrepancies();
  }, [filters.minProbDiff, filters.statType, filters.player, filters.team, filters.books]);

  // Apply client-side search filtering
  const filteredData = useMemo(() => {
    if (!filters.search || !data.data) return data.data;

    const searchLower = filters.search.toLowerCase();
    return data.data.filter(row =>
      row.player_name?.toLowerCase().includes(searchLower) ||
      row.stat_type?.toLowerCase().includes(searchLower) ||
      row.matchup?.toLowerCase().includes(searchLower) ||
      row.book1_name?.toLowerCase().includes(searchLower) ||
      row.book2_name?.toLowerCase().includes(searchLower)
    );
  }, [data.data, filters.search]);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Line Discrepancies</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Find lines where sportsbooks have significant odds differences.
        </p>
      </div>

      <FilterPanel showMinProbDiff showSearch />

      {data.meta && !loading && (
        <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
          Found <span className="font-semibold">{filteredData.length}</span> discrepancies
          with odds difference &ge; <span className="font-semibold">{data.meta.min_prob_diff_applied}%</span>
          {filters.search && ` (filtered from ${data.meta.count})`}
        </div>
      )}

      {error && (
        <div className="card bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 mb-6">
          {error}
        </div>
      )}

      <DiscrepancyTable discrepancies={filteredData} loading={loading} />
    </div>
  );
}

export default DiscrepanciesPage;
