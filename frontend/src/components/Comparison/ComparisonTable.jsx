const BOOK_COLORS = {
  'Pinnacle': 'bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300',
  'PrizePicks': 'bg-purple-100 text-purple-800 dark:bg-purple-900/50 dark:text-purple-300',
  'DraftKings': 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300',
  'FanDuel': 'bg-orange-100 text-orange-800 dark:bg-orange-900/50 dark:text-orange-300',
  'Caesars': 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300',
};

function ComparisonTable({ data, loading, primaryBook }) {
  if (loading) {
    return (
      <div className="card">
        <div className="animate-pulse space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="card text-center py-12">
        <p className="text-gray-500 dark:text-gray-400">No matching lines found across books.</p>
        <p className="text-gray-400 dark:text-gray-500 text-sm mt-2">
          Try adjusting your filters or selecting a different primary book.
        </p>
      </div>
    );
  }

  const formatOdds = (price) => {
    if (price === null || price === undefined) return '—';
    return price > 0 ? `+${price}` : price;
  };

  const getBookColor = (bookName) => {
    return BOOK_COLORS[bookName] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
  };

  return (
    <div className="card">
      <div className="mb-4 flex justify-between items-center">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Showing <span className="font-semibold">{data.length}</span> lines with matches across books
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="data-table">
          <thead>
            <tr>
              <th>Player</th>
              <th>Stat Type</th>
              <th>Matchup</th>
              <th>{primaryBook} (Primary)</th>
              <th>Other Books</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {data.map((row, index) => (
              <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                <td className="font-medium text-gray-900 dark:text-gray-100">{row.player_name}</td>
                <td className="text-gray-600 dark:text-gray-400">{row.stat_type}</td>
                <td className="text-gray-600 dark:text-gray-400 text-sm">{row.matchup}</td>
                <td>
                  <span className={`inline-block px-2 py-1 rounded font-mono text-sm ${getBookColor(primaryBook)}`}>
                    {row.primary_line.points}
                    {row.primary_line.price !== null && (
                      <span className="ml-1 text-xs">
                        ({formatOdds(row.primary_line.price)})
                      </span>
                    )}
                  </span>
                </td>
                <td>
                  <div className="flex flex-wrap gap-2">
                    {row.other_lines.map((line, i) => {
                      const diff = line.points - row.primary_line.points;
                      const diffColor = diff > 0 ? 'text-green-600 dark:text-green-400' : diff < 0 ? 'text-red-600 dark:text-red-400' : '';

                      return (
                        <div
                          key={i}
                          className={`inline-flex items-center px-2 py-1 rounded text-sm ${getBookColor(line.book)}`}
                        >
                          <span className="font-medium mr-1">{line.book}:</span>
                          <span className="font-mono">{line.points}</span>
                          {line.price !== null && (
                            <span className="ml-1 text-xs opacity-75">
                              ({formatOdds(line.price)})
                            </span>
                          )}
                          {diff !== 0 && (
                            <span className={`ml-1 text-xs font-medium ${diffColor}`}>
                              ({diff > 0 ? '+' : ''}{diff.toFixed(1)})
                            </span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ComparisonTable;
