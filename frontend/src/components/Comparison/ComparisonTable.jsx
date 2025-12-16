const BOOK_COLORS = {
  'Pinnacle': 'bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300',
  'PrizePicks': 'bg-purple-100 text-purple-800 dark:bg-purple-900/50 dark:text-purple-300',
  'DraftKings': 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300',
  'FanDuel': 'bg-orange-100 text-orange-800 dark:bg-orange-900/50 dark:text-orange-300',
  'Caesars': 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300',
};

function ComparisonTable({ data, loading }) {
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
        <p className="text-gray-500 dark:text-gray-400">No matching lines found.</p>
        <p className="text-gray-400 dark:text-gray-500 text-sm mt-2">
          Try adjusting your filters.
        </p>
      </div>
    );
  }

  const formatOdds = (price) => {
    if (price === null || price === undefined) return '—';
    return price > 0 ? `+${Math.round(price)}` : Math.round(price);
  };

  const getBookColor = (bookName) => {
    return BOOK_COLORS[bookName] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
  };

  return (
    <div className="card table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th>Player</th>
            <th>Stat Type</th>
            <th>Matchup</th>
            <th>Lines by Book</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
          {data.map((row, index) => (
            <tr key={index}>
              <td className="font-medium text-gray-900 dark:text-gray-100">{row.player_name}</td>
              <td className="text-gray-600 dark:text-gray-400">{row.stat_type}</td>
              <td className="text-gray-600 dark:text-gray-400 text-sm">{row.matchup}</td>
              <td>
                <div className="flex flex-wrap gap-2">
                  {row.lines.map((line, i) => {
                    const isFantasyApp = line.book_type === 'Fantasy';
                    return (
                      <div
                        key={i}
                        className={`inline-flex items-center px-2 py-1 rounded text-sm ${getBookColor(line.book)}`}
                      >
                        <span className="font-medium mr-1">{line.book}:</span>
                        <span className="font-mono">Over {line.points}</span>
                        {!isFantasyApp && line.price !== null && (
                          <span className="ml-1 font-bold">
                            ({formatOdds(line.price)})
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
  );
}

export default ComparisonTable;
