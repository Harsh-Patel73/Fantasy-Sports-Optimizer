import { useState, useEffect } from 'react';
import { useFilters } from '../context/FilterContext';
import { fetchLines } from '../api/client';
import FilterPanel from '../components/Filters/FilterPanel';
import LineTable from '../components/Lines/LineTable';
import Pagination from '../components/Lines/Pagination';

function LinesPage() {
  const { filters, setPage } = useFilters();
  const [data, setData] = useState({ data: [], pagination: null });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadLines() {
      setLoading(true);
      setError(null);

      try {
        const result = await fetchLines({
          book: filters.book !== 'all' ? filters.book : undefined,
          team: filters.team || undefined,
          player: filters.player || undefined,
          stat_type: filters.statType || undefined,
          page: filters.page,
          per_page: filters.perPage,
        });
        setData(result);
      } catch (err) {
        console.error('Failed to load lines:', err);
        setError('Failed to load betting lines. Please try again.');
      } finally {
        setLoading(false);
      }
    }

    loadLines();
  }, [filters.book, filters.team, filters.player, filters.statType, filters.page, filters.perPage]);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">All Betting Lines</h1>
        <p className="text-gray-600">
          Browse and filter betting lines from Pinnacle and PrizePicks.
        </p>
      </div>

      <FilterPanel />

      {error && (
        <div className="card bg-red-50 border border-red-200 text-red-700 mb-6">
          {error}
        </div>
      )}

      <LineTable lines={data.data} loading={loading} />

      <Pagination pagination={data.pagination} onPageChange={setPage} />
    </div>
  );
}

export default LinesPage;
