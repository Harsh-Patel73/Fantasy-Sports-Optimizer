import { useParlay } from '../../context/ParlayContext';

const PICK_COUNTS = {
  '5-pick-flex': 5,
  '6-pick-flex': 6,
  '3-pick-flex': 3,
  '2-pick-power': 2,
};

const PARLAY_LABELS = {
  '5-pick-flex': '5-Pick Flex',
  '6-pick-flex': '6-Pick Flex',
  '3-pick-flex': '3-Pick Flex',
  '2-pick-power': '2-Pick Power Play',
};

function SelectedParlay() {
  const { parlayState, removeLine, clearLines } = useParlay();
  const targetPicks = PICK_COUNTS[parlayState.parlayType] || 5;
  const currentPicks = parlayState.selectedLines.length;

  // Calculate total edge
  const totalEdge = parlayState.selectedLines.reduce((sum, line) => {
    return sum + (line.edge_percent || 0);
  }, 0);

  const evLines = parlayState.selectedLines.filter(l => l.is_ev || l.edge_percent > 0);

  return (
    <div className="card sticky top-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Your Parlay</h3>
        <span className={`text-sm font-medium ${
          currentPicks === targetPicks ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'
        }`}>
          {currentPicks}/{targetPicks} picks
        </span>
      </div>

      <div className="mb-4 p-2 bg-gray-50 dark:bg-gray-700/50 rounded text-sm">
        <p className="text-gray-600 dark:text-gray-400">
          Type: <span className="font-medium text-gray-900 dark:text-gray-100">{PARLAY_LABELS[parlayState.parlayType]}</span>
        </p>
        <p className="text-gray-600 dark:text-gray-400">
          Book: <span className="font-medium text-gray-900 dark:text-gray-100">{parlayState.bettingBook}</span>
        </p>
      </div>

      {parlayState.selectedLines.length === 0 ? (
        <div className="text-center py-6">
          <p className="text-gray-500 dark:text-gray-400 text-sm">
            No lines selected yet.
          </p>
          <p className="text-gray-400 dark:text-gray-500 text-xs mt-1">
            Add lines from the list to build your parlay.
          </p>
        </div>
      ) : (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {parlayState.selectedLines.map((line) => (
            <div
              key={line.id}
              className={`p-2 rounded border ${
                line.is_ev || line.edge_percent > 0
                  ? 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-700'
                  : 'bg-gray-50 border-gray-200 dark:bg-gray-700/50 dark:border-gray-600'
              }`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm truncate text-gray-900 dark:text-gray-100">{line.player_name}</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    {line.stat_type} {line.points} {line.designation}
                  </p>
                  {line.edge_percent !== undefined && (
                    <p className={`text-xs ${
                      line.edge_percent > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-500 dark:text-red-400'
                    }`}>
                      {line.edge_percent > 0 ? '+' : ''}{line.edge_percent}% edge
                    </p>
                  )}
                </div>
                <button
                  onClick={() => removeLine(line.id)}
                  className="text-red-500 dark:text-red-400 text-xs hover:underline ml-2"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Summary */}
      {parlayState.selectedLines.length > 0 && (
        <div className="mt-4 pt-4 border-t dark:border-gray-700">
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">+EV Picks:</span>
              <span className={evLines.length === currentPicks ? 'text-green-600 dark:text-green-400 font-medium' : 'text-yellow-600 dark:text-yellow-400'}>
                {evLines.length}/{currentPicks}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Total Edge:</span>
              <span className={`font-medium ${totalEdge > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-500 dark:text-red-400'}`}>
                {totalEdge > 0 ? '+' : ''}{totalEdge.toFixed(2)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Avg Edge/Pick:</span>
              <span className={`font-medium ${totalEdge > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-500 dark:text-red-400'}`}>
                {currentPicks > 0 ? (totalEdge / currentPicks).toFixed(2) : 0}%
              </span>
            </div>
          </div>

          {currentPicks === targetPicks && (
            <div className={`mt-3 p-2 rounded text-sm ${
              evLines.length === currentPicks
                ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
            }`}>
              {evLines.length === currentPicks ? (
                <p>All picks are +EV! This parlay looks good.</p>
              ) : (
                <p>
                  {currentPicks - evLines.length} pick(s) are not +EV.
                  Consider replacing them for better value.
                </p>
              )}
            </div>
          )}

          <button
            onClick={clearLines}
            className="w-full mt-3 btn-secondary text-sm"
          >
            Clear All
          </button>
        </div>
      )}

      {/* Progress bar */}
      <div className="mt-4">
        <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-300 ${
              currentPicks === targetPicks ? 'bg-green-500' : 'bg-blue-500'
            }`}
            style={{ width: `${(currentPicks / targetPicks) * 100}%` }}
          />
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 text-center">
          {targetPicks - currentPicks > 0
            ? `${targetPicks - currentPicks} more pick(s) needed`
            : 'Parlay complete!'}
        </p>
      </div>
    </div>
  );
}

export default SelectedParlay;
