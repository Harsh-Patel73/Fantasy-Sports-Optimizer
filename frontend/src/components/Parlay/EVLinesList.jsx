import { useParlay } from '../../context/ParlayContext';

function EVLinesList({ lines, loading }) {
  const { addLine, parlayState } = useParlay();

  if (loading) {
    return (
      <div className="card">
        <div className="animate-pulse space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!lines || lines.length === 0) {
    return (
      <div className="card text-center py-8">
        <p className="text-gray-500 dark:text-gray-400">No +EV lines found with current settings.</p>
        <p className="text-gray-400 dark:text-gray-500 text-sm mt-2">
          Try selecting different sharp books or changing the parlay type.
        </p>
      </div>
    );
  }

  const isSelected = (lineId) =>
    parlayState.selectedLines.some(l => l.id === lineId);

  const formatOdds = (odds) => {
    if (odds === null || odds === undefined) return '—';
    return odds > 0 ? `+${odds}` : odds;
  };

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          +EV Lines
        </h3>
        <span className="text-sm text-green-600 dark:text-green-400 font-medium">
          {lines.length} lines found
        </span>
      </div>

      <div className="space-y-3">
        {lines.map((line) => (
          <div
            key={line.id}
            className={`p-4 rounded-lg border transition-colors ${
              isSelected(line.id)
                ? 'border-green-500 bg-green-50 dark:bg-green-900/20 dark:border-green-600'
                : 'border-gray-200 hover:border-blue-300 bg-white dark:bg-gray-800 dark:border-gray-700 dark:hover:border-blue-500'
            }`}
          >
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <p className="font-medium text-gray-900 dark:text-gray-100">{line.player_name}</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {line.stat_type} <span className="font-mono">{line.points}</span> {line.designation}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-500">{line.matchup}</p>
              </div>

              <div className="text-right ml-4">
                <span className="inline-block bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300 px-2 py-1 rounded text-sm font-medium">
                  +{line.edge_percent}% Edge
                </span>
                <p className="text-sm text-gray-700 dark:text-gray-300 mt-1">
                  Sharp: <span className="font-bold">{formatOdds(line.sharp_implied_odds)}</span>
                  <span className="text-xs text-gray-500 dark:text-gray-400 ml-1">
                    ({line.sharp_implied_percent}% implied)
                  </span>
                </p>

                {!isSelected(line.id) ? (
                  <button
                    onClick={() => addLine(line)}
                    className="mt-2 text-blue-600 dark:text-blue-400 text-sm font-medium hover:underline"
                  >
                    + Add to Parlay
                  </button>
                ) : (
                  <span className="mt-2 inline-block text-green-600 dark:text-green-400 text-sm">
                    Added
                  </span>
                )}
              </div>
            </div>

            {/* Sharp books breakdown */}
            {line.sharp_books_data && line.sharp_books_data.length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-100 dark:border-gray-700">
                <div className="flex flex-wrap gap-2">
                  {line.sharp_books_data.map((sharp, i) => (
                    <span
                      key={i}
                      className="text-sm bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 px-2 py-1 rounded"
                    >
                      {sharp.book}: <span className="font-bold">{formatOdds(sharp.price)}</span>
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default EVLinesList;
