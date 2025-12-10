function LineTable({ lines, loading }) {
  if (loading) {
    return (
      <div className="card">
        <div className="animate-pulse space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-12 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!lines || lines.length === 0) {
    return (
      <div className="card text-center py-12">
        <p className="text-gray-500">No betting lines found.</p>
        <p className="text-gray-400 text-sm mt-2">Try adjusting your filters.</p>
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
        <tbody className="divide-y divide-gray-200">
          {lines.map((line) => (
            <tr key={line.id}>
              <td className="font-medium text-gray-900">{line.player_name}</td>
              <td>
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    line.book === 'Pinnacle'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-purple-100 text-purple-800'
                  }`}
                >
                  {line.book}
                </span>
              </td>
              <td className="text-gray-600">
                {line.home_team && line.away_team
                  ? `${line.away_team} @ ${line.home_team}`
                  : 'N/A'}
              </td>
              <td className="text-gray-600">{line.stat_type}</td>
              <td className="font-mono font-medium">{line.points}</td>
              <td className="font-mono text-gray-600">
                {line.price ? line.price : '-'}
              </td>
              <td>
                <span
                  className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                    line.designation?.toLowerCase() === 'over'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
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
