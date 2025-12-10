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
          min_diff: filters.minDiff,
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
  }, [filters.minDiff, filters.statType, filters.player, filters.team]);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Line Discrepancies</h1>
        <p className="text-gray-600">
          Find lines where Pinnacle and PrizePicks differ significantly.
        </p>
      </div>

      <FilterPanel showMinDiff />

      {data.meta && (
        <div className="mb-4 text-sm text-gray-600">
          Found <span className="font-semibold">{data.meta.count}</span> discrepancies
          with difference &ge; <span className="font-semibold">{data.meta.min_diff_applied}</span>
        </div>
      )}

      {error && (
        <div className="card bg-red-50 border border-red-200 text-red-700 mb-6">
          {error}
        </div>
      )}

      <DiscrepancyTable discrepancies={data.data} loading={loading} />
    </div>
  );
}

export default DiscrepanciesPage;
