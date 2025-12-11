import { useState, useEffect } from 'react';
import { calculateParlayOdds, fetchCalculatorParlayTypes } from '../../api/client';

const PARLAY_TYPE_LABELS = {
  '5-pick-flex': '5-Pick Flex',
  '6-pick-flex': '6-Pick Flex',
  '3-pick-flex': '3-Pick Flex',
  '2-pick-power': '2-Pick Power Play',
};

function ParlayOddsCalculator() {
  const [parlayType, setParlayType] = useState('5-pick-flex');
  const [result, setResult] = useState(null);
  const [allTypes, setAllTypes] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Load all parlay types on mount
    fetchCalculatorParlayTypes()
      .then((data) => setAllTypes(data.parlay_types || []))
      .catch(console.error);
  }, []);

  async function handleCalculate() {
    setLoading(true);
    try {
      const data = await calculateParlayOdds({ parlay_type: parlayType });
      setResult(data);
    } catch (err) {
      console.error('Failed to calculate:', err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // Auto-calculate on type change
    handleCalculate();
  }, [parlayType]);

  const formatOdds = (odds) => (odds > 0 ? `+${odds}` : odds);

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">Parlay Odds Calculator</h2>
      <p className="text-gray-600 dark:text-gray-400 mb-6">
        Calculate the break-even probability and implied odds per pick for PrizePicks-style parlays.
        This helps you understand what win rate you need to be profitable.
      </p>

      <div className="flex items-end gap-4 mb-6">
        <div className="flex-1 max-w-xs">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Parlay Type
          </label>
          <select
            value={parlayType}
            onChange={(e) => setParlayType(e.target.value)}
            className="select-field"
          >
            {Object.entries(PARLAY_TYPE_LABELS).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </div>
        <button
          onClick={handleCalculate}
          disabled={loading}
          className="btn-primary"
        >
          {loading ? 'Calculating...' : 'Calculate'}
        </button>
      </div>

      {result && !result.error && (
        <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
          <h3 className="font-semibold mb-4 text-gray-900 dark:text-gray-100">
            Results for {PARLAY_TYPE_LABELS[result.parlay_type] || result.parlay_type}
          </h3>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white dark:bg-gray-800 p-3 rounded shadow-sm">
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Picks</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{result.total_picks}</p>
            </div>
            <div className="bg-white dark:bg-gray-800 p-3 rounded shadow-sm">
              <p className="text-sm text-gray-600 dark:text-gray-400">Break-Even Probability</p>
              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{result.breakeven_percent}%</p>
            </div>
            <div className="bg-white dark:bg-gray-800 p-3 rounded shadow-sm">
              <p className="text-sm text-gray-600 dark:text-gray-400">Break-Even Odds</p>
              <p className="text-2xl font-bold font-mono text-blue-600 dark:text-blue-400">
                {formatOdds(result.breakeven_odds)}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 p-3 rounded shadow-sm">
              <p className="text-sm text-gray-600 dark:text-gray-400">Edge vs 50%</p>
              <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                {result.edge_vs_coinflip > 0 ? '+' : ''}{result.edge_vs_coinflip}%
              </p>
            </div>
          </div>

          <div className="mb-6">
            <h4 className="font-medium mb-2 text-gray-900 dark:text-gray-100">Payout Structure</h4>
            <div className="flex gap-2 flex-wrap">
              {Object.entries(result.payout_structure).map(([hits, payout]) => (
                <span
                  key={hits}
                  className="bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300 px-3 py-1 rounded font-medium"
                >
                  {hits}/{result.total_picks}: {payout}x
                </span>
              ))}
            </div>
          </div>

          <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded">
            <p className="text-sm text-yellow-800 dark:text-yellow-300">
              <strong>Key Insight:</strong> {result.explanation}
            </p>
            <p className="text-sm text-yellow-700 dark:text-yellow-400 mt-2">
              This means if you're picking props at 50/50 odds, you're giving up{' '}
              <strong>{Math.abs(result.edge_vs_coinflip).toFixed(1)}%</strong> edge to the house on every pick.
              To be profitable, your picks need to hit at better than{' '}
              <strong>{result.breakeven_percent}%</strong>.
            </p>
          </div>
        </div>
      )}

      {/* Quick Reference Table */}
      {allTypes.length > 0 && (
        <div className="mt-6">
          <h3 className="font-semibold mb-3 text-gray-900 dark:text-gray-100">Quick Reference: All Parlay Types</h3>
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Parlay Type</th>
                  <th>Picks</th>
                  <th>Break-Even %</th>
                  <th>Break-Even Odds</th>
                </tr>
              </thead>
              <tbody>
                {allTypes.map((type) => (
                  <tr
                    key={type.type}
                    className={type.type === parlayType ? 'bg-blue-50 dark:bg-blue-900/30' : ''}
                  >
                    <td className="font-medium">
                      {PARLAY_TYPE_LABELS[type.type] || type.type}
                    </td>
                    <td>{type.total_picks}</td>
                    <td className="font-mono">{type.breakeven_percent}%</td>
                    <td className="font-mono">{formatOdds(type.breakeven_odds)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default ParlayOddsCalculator;
