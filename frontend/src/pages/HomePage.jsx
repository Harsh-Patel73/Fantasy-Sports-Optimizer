import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { fetchHealth, fetchDiscrepancies } from '../api/client';

function HomePage() {
  const [health, setHealth] = useState(null);
  const [topDiscrepancies, setTopDiscrepancies] = useState([]);
  const [loading, setLoading] = useState(true);

  const formatOdds = (odds) => {
    if (odds === null || odds === undefined) return '—';
    return odds > 0 ? `+${odds}` : odds;
  };

  useEffect(() => {
    async function loadData() {
      try {
        const [healthData, discData] = await Promise.all([
          fetchHealth(),
          fetchDiscrepancies({ min_prob_diff: 5 }),
        ]);
        setHealth(healthData);
        setTopDiscrepancies(discData.data.slice(0, 5));
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  if (loading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
        <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="card bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <h1 className="text-3xl font-bold mb-2">Get started now</h1>
        <p className="text-blue-100 mb-4">
          Data is fabricated with the use of Claude Code to showcase the application.
        </p>
        <div className="flex space-x-4">
          <Link to="/lines" className="bg-white text-blue-600 px-4 py-2 rounded-lg font-medium hover:bg-blue-50 transition-colors">
            View All Lines
          </Link>
          <Link to="/discrepancies" className="bg-blue-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-400 transition-colors">
            Find Discrepancies
          </Link>
        </div>
      </div>

      {/* Top Discrepancies */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">Top Discrepancies</h2>
          <Link to="/discrepancies" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 text-sm font-medium">
            View All &rarr;
          </Link>
        </div>

        {topDiscrepancies.length > 0 ? (
          <div className="space-y-3">
            {topDiscrepancies.map((disc, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900 dark:text-gray-100">{disc.player_name}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{disc.stat_type} O {disc.book1_line} - {disc.matchup}</p>
                </div>
                <div className="text-right">
                  <div className="flex items-center space-x-2">
                    <span className="text-green-600 dark:text-green-400 font-mono text-sm">
                      {disc.book1_name} {formatOdds(disc.book1_odds)}
                    </span>
                    <span className="text-gray-400 dark:text-gray-500">vs</span>
                    <span className="text-gray-600 dark:text-gray-400 font-mono text-sm">
                      {disc.book2_name} {formatOdds(disc.book2_odds)}
                    </span>
                  </div>
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300">
                    {disc.prob_difference}% edge
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 dark:text-gray-400 text-center py-8">
            No significant discrepancies found.
          </p>
        )}
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-gray-100">Line Comparison</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            View and filter betting lines from Pinnacle and PrizePicks. Compare odds across books.
          </p>
          <Link to="/lines" className="btn-secondary inline-block">
            Browse Lines
          </Link>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-gray-100">Discrepancy Finder</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Find lines where the two books differ significantly. Set your threshold and find value.
          </p>
          <Link to="/discrepancies" className="btn-secondary inline-block">
            Find Discrepancies
          </Link>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
