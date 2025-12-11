import { useState } from 'react';
import DevigCalculator from '../components/Calculators/DevigCalculator';
import ParlayOddsCalculator from '../components/Calculators/ParlayOddsCalculator';

function CalculatorsPage() {
  const [activeTab, setActiveTab] = useState('devig');

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Betting Calculators</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Tools for devigging lines and calculating parlay odds.
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700 mb-6">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab('devig')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'devig'
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            Devigger Calculator
          </button>
          <button
            onClick={() => setActiveTab('parlay')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'parlay'
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            Parlay Odds Calculator
          </button>
        </nav>
      </div>

      {/* Calculator Content */}
      {activeTab === 'devig' ? <DevigCalculator /> : <ParlayOddsCalculator />}
    </div>
  );
}

export default CalculatorsPage;
