function DiscrepancyTable({ discrepancies, loading }) {
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

  if (!discrepancies || discrepancies.length === 0) {
    return (
      <div className="card text-center py-12">
        <p className="text-gray-500 dark:text-gray-400">No discrepancies found.</p>
        <p className="text-gray-400 dark:text-gray-500 text-sm mt-2">
          Try lowering the minimum difference threshold or adjusting filters.
        </p>
      </div>
    );
  }

  const getDiffClass = (diff) => {
    if (diff >= 2) return 'diff-high';
    if (diff >= 1) return 'diff-medium';
    return 'diff-low';
  };

  return (
    <div className="card table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th>Player</th>
            <th>Stat</th>
            <th>Matchup</th>
            <th>Pinnacle</th>
            <th>PrizePicks</th>
            <th>Difference</th>
            <th>Higher</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
          {discrepancies.map((disc, index) => (
            <tr key={index}>
              <td className="font-medium text-gray-900 dark:text-gray-100">{disc.player_name}</td>
              <td className="text-gray-600 dark:text-gray-400">{disc.stat_type}</td>
              <td className="text-gray-600 dark:text-gray-400">{disc.matchup}</td>
              <td className="font-mono">
                <span className="bg-blue-50 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300 px-2 py-0.5 rounded">
                  {disc.pinnacle_line}
                </span>
              </td>
              <td className="font-mono">
                <span className="bg-purple-50 text-purple-700 dark:bg-purple-900/50 dark:text-purple-300 px-2 py-0.5 rounded">
                  {disc.prizepicks_line}
                </span>
              </td>
              <td>
                <span className={`px-2 py-0.5 rounded font-medium ${getDiffClass(disc.difference)}`}>
                  {disc.difference} ({disc.percent_diff}%)
                </span>
              </td>
              <td>
                <span
                  className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                    disc.higher_book === 'Pinnacle'
                      ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300'
                      : 'bg-purple-100 text-purple-800 dark:bg-purple-900/50 dark:text-purple-300'
                  }`}
                >
                  {disc.higher_book}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default DiscrepancyTable;
