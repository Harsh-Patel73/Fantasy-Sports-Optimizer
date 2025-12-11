function LineTable({ lines, loading }) {
  if (loading) {
    return (
      <div className="card">
        <div className="animate-pulse space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-12 bg-gray-200 dark:bg-gray-700 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!lines || lines.length === 0) {
    return (
      <div className="card text-center py-12">
        <p className="text-gray-500 dark:text-gray-400">No betting lines found.</p>
        <p className="text-gray-400 dark:text-gray-500 text-sm mt-2">Try adjusting your filters.</p>
      </div>
    );
  }

  return (
    <div className="card table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th>Player</th>
            <th>Book</th>
            <th>Matchup</th>
            <th>Stat Type</th>
            <th>Line</th>
            <th>Price</th>
            <th>Side</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
          {lines.map((line) => (
            <tr key={line.id}>
              <td className="font-medium text-gray-900 dark:text-gray-100">{line.player_name}</td>
              <td>
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    line.book === 'Pinnacle'
                      ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300'
                      : 'bg-purple-100 text-purple-800 dark:bg-purple-900/50 dark:text-purple-300'
                  }`}
                >
                  {line.book}
                </span>
              </td>
              <td className="text-gray-600 dark:text-gray-400">
                {line.home_team && line.away_team
                  ? `${line.away_team} @ ${line.home_team}`
                  : 'N/A'}
              </td>
              <td className="text-gray-600 dark:text-gray-400">{line.stat_type}</td>
              <td className="font-mono font-medium">{line.points}</td>
              <td className="font-mono text-gray-600 dark:text-gray-400">
                {line.price ? line.price : '-'}
              </td>
              <td>
                <span
                  className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                    line.designation?.toLowerCase() === 'over'
                      ? 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300'
                      : 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300'
                  }`}
                >
                  {line.designation || '-'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default LineTable;
