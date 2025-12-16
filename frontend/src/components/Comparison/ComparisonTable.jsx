const BOOK_COLORS = {
  'Pinnacle': 'bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300',
  'PrizePicks': 'bg-purple-100 text-purple-800 dark:bg-purple-900/50 dark:text-purple-300',
  'DraftKings': 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300',
  'FanDuel': 'bg-orange-100 text-orange-800 dark:bg-orange-900/50 dark:text-orange-300',
  'Caesars': 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300',
  'BetMGM': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300',
  'Bovada': 'bg-pink-100 text-pink-800 dark:bg-pink-900/50 dark:text-pink-300',
  'Fliff': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/50 dark:text-indigo-300',
  'Hard Rock Bet': 'bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300',
  'BetRivers': 'bg-teal-100 text-teal-800 dark:bg-teal-900/50 dark:text-teal-300',
};

// Format stat types: "Player_Steals" -> "Player Steals"
const formatStatType = (stat) => {
  if (!stat) return '';
  return stat.replace(/_/g, ' ');
};

// Format designation: "O" -> "Over", "U" -> "Under"
const formatDesignation = (designation) => {
  if (!designation) return 'Over';
  if (designation === 'O' || designation.toLowerCase() === 'over') return 'Over';
  if (designation === 'U' || designation.toLowerCase() === 'under') return 'Under';
  return designation;
};

function ComparisonTable({ data, loading, selectedBooks }) {
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

  // When specific books are selected, show them as columns
  const showColumnarView = selectedBooks && selectedBooks.length >= 2 && selectedBooks.length <= 5;

  if (showColumnarView) {
    return (
      <div className="card table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Player</th>
              <th>Stat Type</th>
              <th>Matchup</th>
              {selectedBooks.map(book => (
                <th key={book} className="text-center">
                  <span className={`inline-block px-2 py-1 rounded text-xs ${getBookColor(book)}`}>
                    {book}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {data.map((row, index) => {
              // Create a map of book -> line for quick lookup
              const linesByBook = {};
              row.lines.forEach(line => {
                linesByBook[line.book] = line;
              });

              return (
                <tr key={index}>
                  <td className="font-medium text-gray-900 dark:text-gray-100">{row.player_name}</td>
                  <td className="text-gray-600 dark:text-gray-400">{formatStatType(row.stat_type)}</td>
                  <td className="text-gray-600 dark:text-gray-400 text-sm">{row.matchup}</td>
                  {selectedBooks.map(book => {
                    const line = linesByBook[book];
                    if (!line) {
                      return (
                        <td key={book} className="text-center text-gray-400 dark:text-gray-500">
                          —
                        </td>
                      );
                    }
                    const isFantasyApp = line.book_type === 'Fantasy';
                    return (
                      <td key={book} className="text-center">
                        <div className="flex flex-col items-center">
                          <span className="font-mono font-medium text-gray-900 dark:text-gray-100">
                            {formatDesignation(line.designation)} {line.points}
                          </span>
                          {!isFantasyApp && line.price !== null && (
                            <span className={`text-sm font-bold ${line.price > 0 ? 'text-green-600 dark:text-green-400' : 'text-gray-600 dark:text-gray-400'}`}>
                              {formatOdds(line.price)}
                            </span>
                          )}
                        </div>
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    );
  }

  // Default view: lines wrapped in badges
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
              <td className="text-gray-600 dark:text-gray-400">{formatStatType(row.stat_type)}</td>
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
                        <span className="font-mono">{formatDesignation(line.designation)} {line.points}</span>
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
