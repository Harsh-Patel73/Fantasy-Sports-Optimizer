// Format stat types: "Player_Steals" -> "Player Steals"
const formatStatType = (stat) => {
  if (!stat) return '';
  return stat.replace(/_/g, ' ');
};

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
          Try lowering the minimum odds difference threshold or adjusting filters.
        </p>
      </div>
    );
  }

  const getProbDiffClass = (probDiff) => {
    if (probDiff >= 15) return 'diff-high';
    if (probDiff >= 10) return 'diff-medium';
    return 'diff-low';
  };

  const formatOdds = (odds) => {
    if (odds === null || odds === undefined) return '—';
    return odds > 0 ? `+${odds}` : odds;
  };

  return (
    <div className="card table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th>Player</th>
            <th>Stat</th>
            <th>Matchup</th>
            <th>Best Odds</th>
            <th>Comparison</th>
            <th>Edge</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
          {discrepancies.map((disc, index) => (
            <tr key={index}>
              <td className="font-medium text-gray-900 dark:text-gray-100">{disc.player_name}</td>
              <td className="text-gray-600 dark:text-gray-400">{formatStatType(disc.stat_type)}</td>
              <td className="text-gray-600 dark:text-gray-400">{disc.matchup}</td>
              <td>
                <div className="flex flex-col">
                  <span className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">{disc.book1_name}</span>
                  <span className="font-mono bg-green-50 text-green-700 dark:bg-green-900/50 dark:text-green-300 px-2 py-0.5 rounded inline-block">
                    Over {disc.book1_line} ({formatOdds(disc.book1_odds)})
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {disc.book1_implied}% implied
                  </span>
                </div>
              </td>
              <td>
                <div className="flex flex-col">
                  <span className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">{disc.book2_name}</span>
                  <span className="font-mono bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 px-2 py-0.5 rounded inline-block">
                    Over {disc.book2_line} ({formatOdds(disc.book2_odds)})
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {disc.book2_implied}% implied
                  </span>
                </div>
              </td>
              <td>
                <span className={`px-2 py-0.5 rounded font-medium ${getProbDiffClass(disc.prob_difference)}`}>
                  {disc.prob_difference}%
                </span>
                {disc.line_difference > 0 && (
                  <span className="block text-xs text-gray-400 dark:text-gray-500 mt-1">
                    (±{disc.line_difference} pts)
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default DiscrepancyTable;
