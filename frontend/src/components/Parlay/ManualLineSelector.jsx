import { useState, useEffect } from 'react';
import { useParlay } from '../../context/ParlayContext';
import { fetchParlayLines, validateParlay } from '../../api/client';

function ManualLineSelector() {
  const { parlayState, addLine } = useParlay();
  const [lines, setLines] = useState([]);
  const [validationResults, setValidationResults] = useState({});
  const [loading, setLoading] = useState(true);
  const [validating, setValidating] = useState(false);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState(null);
  const [filters, setFilters] = useState({ player: '', stat_type: '' });

  // Load lines from betting book
  useEffect(() => {
    async function loadLines() {
      setLoading(true);
      try {
        const result = await fetchParlayLines({
          betting_book: parlayState.bettingBook,
          page,
          per_page: 20,
          player: filters.player || undefined,
          stat_type: filters.stat_type || undefined,
        });
        setLines(result.data || []);
        setPagination(result.pagination);
      } catch (err) {
        console.error('Failed to load lines:', err);
      } finally {
        setLoading(false);
      }
    }
    loadLines();
  }, [parlayState.bettingBook, page, filters]);

  // Validate displayed lines against sharp books
  useEffect(() => {
    async function validateLines() {
      if (lines.length === 0) return;

      setValidating(true);
      try {
        const result = await validateParlay({
          line_ids: lines.map(l => l.id),
          sharp_books: parlayState.sharpBooks,
          parlay_type: parlayState.parlayType,
        });

        // Create lookup by line ID
        const lookup = {};
        (result.validated_lines || []).forEach(vl => {
          lookup[vl.id] = vl;
        });
        setValidationResults(lookup);
      } catch (err) {
        console.error('Failed to validate lines:', err);
      } finally {
        setValidating(false);
      }
    }
    validateLines();
  }, [lines, parlayState.sharpBooks, parlayState.parlayType]);

  const isSelected = (lineId) =>
    parlayState.selectedLines.some(l => l.id === lineId);

  const formatOdds = (odds) => {
    if (odds === null || odds === undefined) return '—';
    return odds > 0 ? `+${odds}` : odds;
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPage(1);
  };

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Select Lines</h3>
        {validating && (
          <span className="text-sm text-gray-500 dark:text-gray-400">Validating...</span>
        )}
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-4">
        <input
          type="text"
          placeholder="Filter by player..."
          value={filters.player}
          onChange={(e) => handleFilterChange('player', e.target.value)}
          className="input-field flex-1"
        />
        <input
          type="text"
          placeholder="Filter by stat..."
          value={filters.stat_type}
          onChange={(e) => handleFilterChange('stat_type', e.target.value)}
          className="input-field flex-1"
        />
      </div>

      {loading ? (
        <div className="animate-pulse space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
          ))}
        </div>
      ) : lines.length === 0 ? (
        <p className="text-center text-gray-500 dark:text-gray-400 py-8">
          No lines found for {parlayState.bettingBook}
        </p>
      ) : (
        <div className="space-y-2">
          {lines.map((line) => {
            const validation = validationResults[line.id];
            const selected = isSelected(line.id);

            return (
              <div
                key={line.id}
                className={`p-3 rounded border transition-colors ${
                  selected
                    ? 'border-green-500 bg-green-50 dark:bg-green-900/20 dark:border-green-600'
                    : validation?.is_ev
                    ? 'border-green-200 bg-green-50/50 hover:border-green-400 dark:border-green-700 dark:bg-green-900/10 dark:hover:border-green-500'
                    : 'border-gray-200 hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-600'
                }`}
              >
                <div className="flex justify-between items-center">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">{line.player_name}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {line.stat_type} <span className="font-mono">{line.points}</span> {line.designation}
                    </p>
                  </div>

                  <div className="flex items-center gap-3">
                    {validation && (
                      <div className="text-right">
                        {validation.is_ev ? (
                          <span className="text-green-600 dark:text-green-400 text-sm font-medium">
                            +{validation.edge_percent}% EV
                          </span>
                        ) : validation.has_sharp_data ? (
                          <span className="text-red-500 dark:text-red-400 text-sm">
                            {validation.edge_percent}% (Not +EV)
                          </span>
                        ) : (
                          <span className="text-gray-400 dark:text-gray-500 text-sm">
                            No sharp data
                          </span>
                        )}
                      </div>
                    )}

                    {!selected ? (
                      <button
                        onClick={() => addLine({
                          ...line,
                          edge: validation?.edge,
                          edge_percent: validation?.edge_percent,
                          is_ev: validation?.is_ev,
                        })}
                        className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                      >
                        Add
                      </button>
                    ) : (
                      <span className="px-3 py-1 text-sm bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-300 rounded">
                        Added
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Pagination */}
      {pagination && pagination.total_pages > 1 && (
        <div className="flex justify-center gap-2 mt-4 pt-4 border-t dark:border-gray-700">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1 text-sm border rounded disabled:opacity-50 dark:border-gray-600 dark:text-gray-300"
          >
            Previous
          </button>
          <span className="px-3 py-1 text-sm text-gray-600 dark:text-gray-400">
            Page {page} of {pagination.total_pages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(pagination.total_pages, p + 1))}
            disabled={page === pagination.total_pages}
            className="px-3 py-1 text-sm border rounded disabled:opacity-50 dark:border-gray-600 dark:text-gray-300"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

export default ManualLineSelector;
