import { useState, useEffect } from 'react';
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
  }, [filters.minProbDiff, filters.statType, filters.player, filters.team]);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Line Discrepancies</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Find lines where Pinnacle and PrizePicks differ significantly.
        </p>
      </div>

      <FilterPanel showMinProbDiff />

      {data.meta && (
        <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
          Found <span className="font-semibold">{data.meta.count}</span> discrepancies
          with odds difference &ge; <span className="font-semibold">{data.meta.min_prob_diff_applied}%</span>
        </div>
      )}

      {error && (
        <div className="card bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 mb-6">
          {error}
        </div>
      )}

      <DiscrepancyTable discrepancies={data.data} loading={loading} />
    </div>
  );
}

export default DiscrepanciesPage;
