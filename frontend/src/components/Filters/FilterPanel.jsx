import { useState, useEffect } from 'react';
import { useFilters } from '../../context/FilterContext';
import { fetchTeams, fetchPlayers, fetchStatTypes, fetchBooks } from '../../api/client';

function FilterPanel({ showMinProbDiff = false }) {
  const { filters, setBooks, setTeam, setPlayer, setStatType, setMinProbDiff, resetFilters } = useFilters();

  const [availableBooks, setAvailableBooks] = useState([]);
  const [teams, setTeams] = useState([]);
  const [players, setPlayers] = useState([]);
  const [statTypes, setStatTypes] = useState([]);
  const [loading, setLoading] = useState(true);

  // Load initial filter options (books, teams, stat types)
  useEffect(() => {
    async function loadFilterOptions() {
      try {
        const [booksData, teamsData, statTypesData] = await Promise.all([
          fetchBooks(),
          fetchTeams(),
          fetchStatTypes(),
        ]);
        setAvailableBooks(booksData);
        setTeams(teamsData);
        setStatTypes(statTypesData);
      } catch (error) {
        console.error('Failed to load filter options:', error);
      } finally {
        setLoading(false);
      }
    }

    loadFilterOptions();
  }, []);

  // Load players when team changes
  useEffect(() => {
    async function loadPlayers() {
      try {
        const playersData = await fetchPlayers(filters.team || null);
        setPlayers(playersData);
      } catch (error) {
        console.error('Failed to load players:', error);
      }
    }

    loadPlayers();
  }, [filters.team]);

  const handleBookToggle = (bookName) => {
    const currentBooks = filters.books || [];
    if (currentBooks.includes(bookName)) {
      setBooks(currentBooks.filter(b => b !== bookName));
    } else {
      setBooks([...currentBooks, bookName]);
    }
  };

  const selectAllBooks = () => {
    setBooks([]);  // Empty array means all books
  };

  const clearAllBooks = () => {
    setBooks(availableBooks.map(b => b.name));  // Select all books explicitly
  };

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

  const isAllBooksSelected = !filters.books || filters.books.length === 0;

  return (
    <div className="card mb-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Book Filter - Multi-select */}
        <div className="md:col-span-2 lg:col-span-4">
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Sportsbooks
            </label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={selectAllBooks}
                className={`text-xs px-2 py-1 rounded ${isAllBooksSelected ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'}`}
              >
                All
              </button>
              <button
                type="button"
                onClick={clearAllBooks}
                className="text-xs px-2 py-1 rounded bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600"
              >
                Clear
              </button>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            {availableBooks.map((book) => {
              const isSelected = isAllBooksSelected || filters.books.includes(book.name);
              return (
                <button
                  key={book.name}
                  type="button"
                  onClick={() => handleBookToggle(book.name)}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                    isSelected
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  {book.name}
                </button>
              );
            })}
          </div>
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

        {/* Min Probability Diff Slider (only for discrepancies) */}
        {showMinProbDiff && (
          <div className="md:col-span-2 lg:col-span-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Minimum Odds Difference: {filters.minProbDiff}%
            </label>
            <input
              type="range"
              min="0"
              max="20"
              step="1"
              value={filters.minProbDiff}
              onChange={(e) => setMinProbDiff(parseInt(e.target.value))}
              className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
              <span>0%</span>
              <span>20%</span>
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
