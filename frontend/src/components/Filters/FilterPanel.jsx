import { useState, useEffect } from 'react';
import { useFilters } from '../../context/FilterContext';
import { fetchTeams, fetchPlayers, fetchStatTypes } from '../../api/client';

function FilterPanel({ showMinDiff = false }) {
  const { filters, setBook, setTeam, setPlayer, setStatType, setMinDiff, resetFilters } = useFilters();

  const [teams, setTeams] = useState([]);
  const [players, setPlayers] = useState([]);
  const [statTypes, setStatTypes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadFilterOptions() {
      try {
        const [teamsData, playersData, statTypesData] = await Promise.all([
          fetchTeams(),
          fetchPlayers(),
          fetchStatTypes(),
        ]);
        setTeams(teamsData);
        setPlayers(playersData);
        setStatTypes(statTypesData);
      } catch (error) {
        console.error('Failed to load filter options:', error);
      } finally {
        setLoading(false);
      }
    }

    loadFilterOptions();
  }, []);

  if (loading) {
    return (
      <div className="card mb-6">
        <div className="animate-pulse flex space-x-4">
          <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded flex-1"></div>
          <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded flex-1"></div>
          <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded flex-1"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="card mb-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Book Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Sportsbook
          </label>
          <select
            value={filters.book}
            onChange={(e) => setBook(e.target.value)}
            className="select-field"
          >
            <option value="all">All Books</option>
            <option value="pinnacle">Pinnacle</option>
            <option value="prizepicks">PrizePicks</option>
          </select>
        </div>

        {/* Team Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Team
          </label>
          <select
            value={filters.team}
            onChange={(e) => setTeam(e.target.value)}
            className="select-field"
          >
            <option value="">All Teams</option>
            {teams.map((team) => (
              <option key={team} value={team}>
                {team}
              </option>
            ))}
          </select>
        </div>

        {/* Player Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Player
          </label>
          <select
            value={filters.player}
            onChange={(e) => setPlayer(e.target.value)}
            className="select-field"
          >
            <option value="">All Players</option>
            {players.map((player) => (
              <option key={player} value={player}>
                {player}
              </option>
            ))}
          </select>
        </div>

        {/* Stat Type Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Stat Type
          </label>
          <select
            value={filters.statType}
            onChange={(e) => setStatType(e.target.value)}
            className="select-field"
          >
            <option value="">All Stats</option>
            {statTypes.map((stat) => (
              <option key={stat} value={stat}>
                {stat}
              </option>
            ))}
          </select>
        </div>

        {/* Min Diff Slider (only for discrepancies) */}
        {showMinDiff && (
          <div className="md:col-span-2 lg:col-span-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Minimum Difference: {filters.minDiff}
            </label>
            <input
              type="range"
              min="0"
              max="5"
              step="0.5"
              value={filters.minDiff}
              onChange={(e) => setMinDiff(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
              <span>0</span>
              <span>5+</span>
            </div>
          </div>
        )}
      </div>

      {/* Reset Button */}
      <div className="mt-4 flex justify-end">
        <button onClick={resetFilters} className="btn-secondary text-sm">
          Reset Filters
        </button>
      </div>
    </div>
  );
}

export default FilterPanel;
