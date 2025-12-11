import { useState } from 'react';
import { calculateDevig } from '../../api/client';

function DevigCalculator() {
  const [odds1, setOdds1] = useState('-110');
  const [odds2, setOdds2] = useState('-110');
  const [method, setMethod] = useState('multiplicative');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleCalculate() {
    setLoading(true);
    setError(null);
    try {
      const data = await calculateDevig({
        odds_1: parseInt(odds1),
        odds_2: parseInt(odds2),
        method,
      });
      setResult(data);
    } catch (err) {
      setError('Failed to calculate. Please check your inputs.');
    } finally {
      setLoading(false);
    }
  }

  const formatOdds = (odds) => (odds > 0 ? `+${odds}` : odds);

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">Devigger Calculator</h2>
      <p className="text-gray-600 dark:text-gray-400 mb-6">
        Remove the vig (juice) from betting lines to find true fair odds.
        Enter the odds for both sides of a two-way market.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Side 1 Odds
          </label>
          <input
            type="number"
            value={odds1}
            onChange={(e) => setOdds1(e.target.value)}
            className="input-field"
            placeholder="-110"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Side 2 Odds
          </label>
          <input
            type="number"
            value={odds2}
            onChange={(e) => setOdds2(e.target.value)}
            className="input-field"
            placeholder="-110"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Method
          </label>
          <select
            value={method}
            onChange={(e) => setMethod(e.target.value)}
            className="select-field"
          >
            <option value="multiplicative">Multiplicative (Proportional)</option>
            <option value="additive">Additive (Equal Split)</option>
            <option value="power">Power Method (Better for Favorites)</option>
          </select>
        </div>
      </div>

      <button
        onClick={handleCalculate}
        disabled={loading}
        className="btn-primary"
      >
        {loading ? 'Calculating...' : 'Calculate'}
      </button>

      {error && (
        <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 rounded">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <h3 className="font-semibold mb-3 text-gray-900 dark:text-gray-100">Results</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white dark:bg-gray-800 p-3 rounded shadow-sm">
              <p className="text-sm text-gray-600 dark:text-gray-400">Side 1 True Probability</p>
              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{result.true_percent_1}%</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Fair Odds: <span className="font-mono">{formatOdds(result.fair_odds_1)}</span>
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 p-3 rounded shadow-sm">
              <p className="text-sm text-gray-600 dark:text-gray-400">Side 2 True Probability</p>
              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{result.true_percent_2}%</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Fair Odds: <span className="font-mono">{formatOdds(result.fair_odds_2)}</span>
              </p>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t dark:border-gray-600 grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Total Vig: <span className="font-semibold text-red-600 dark:text-red-400">{result.total_vig}%</span>
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Method Used: <span className="font-semibold">{result.method_used}</span>
              </p>
            </div>
          </div>

          <div className="mt-4 text-sm text-gray-500 dark:text-gray-400">
            <p className="font-medium mb-1">Method Explanations:</p>
            <ul className="list-disc ml-4 space-y-1">
              <li><strong>Multiplicative:</strong> Distributes vig proportionally - most common approach</li>
              <li><strong>Additive:</strong> Splits vig equally between both sides</li>
              <li><strong>Power:</strong> More accurate for heavy favorites/underdogs</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default DevigCalculator;
