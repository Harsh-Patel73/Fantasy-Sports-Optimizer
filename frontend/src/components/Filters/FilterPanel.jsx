import { useState, useEffect } from 'react';
import { useFilters } from '../../context/FilterContext';
import { fetchSports, fetchTeams, fetchPlayers, fetchStatTypes, fetchBooks } from '../../api/client';

// Format stat types: "Player_Steals" -> "Player Steals"
const formatStatType = (stat) => {
  if (!stat) return '';
  return stat.replace(/_/g, ' ');
};

function FilterPanel({ showMinProbDiff = false, showSearch = false }) {
  const { filters, setBooks, setSport, setTeam, setPlayer, setStatType, setSearch, setMinProbDiff, resetFilters } = useFilters();

  const [availableBooks, setAvailableBooks] = useState([]);
  const [sports, setSports] = useState([]);
  const [teams, setTeams] = useState([]);
  const [players, setPlayers] = useState([]);
  const [statTypes, setStatTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchInput, setSearchInput] = useState('');

  // Load initial filter options (books, sports, stat types)
  useEffect(() => {
    async function loadFilterOptions() {
      try {
        const [booksData, sportsData, statTypesData] = await Promise.all([
          fetchBooks(),
          fetchSports(),
          fetchStatTypes(),
        ]);
        setAvailableBooks(booksData);
        setSports(sportsData);
        setStatTypes(statTypesData);
      } catch (error) {
        console.error('Failed to load filter options:', error);
      } finally {
        setLoading(false);
      }
    }

    loadFilterOptions();
  }, []);

  // Load teams when sport changes
  useEffect(() => {
    async function loadTeams() {
      try {
        const teamsData = await fetchTeams(filters.sport || null);
        setTeams(teamsData);
      } catch (error) {
        console.error('Failed to load teams:', error);
      }
    }

    loadTeams();
  }, [filters.sport]);

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

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearch(searchInput);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchInput, setSearch]);

  const handleBookToggle = (bookName) => {
    const currentBooks = filters.books || [];
    if (currentBooks.includes(bookName)) {
      setBooks(currentBooks.filter(b => b !== bookName));
    } else {
      setBooks([...currentBooks, bookName]);
    }
  };

  const selectAllBooks = () => {
    setBooks(availableBooks.map(b => b.name));  // Select all books explicitly
  };

  const clearAllBooks = () => {
    setBooks([]);  // Empty array means no books selected
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

  const isAllBooksSelected = filters.books.length === availableBooks.length && availableBooks.length > 0;
  const isNoBooksSelected = !filters.books || filters.books.length === 0;

  return (
    <div className="card mb-6">
      {/* Search Bar */}
      {showSearch && (
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Search
          </label>
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search players, teams, stats..."
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      )}

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
              const isSelected = filters.books.includes(book.name);
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

        {/* League Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            League
          </label>
          <select
            value={filters.sport}
            onChange={(e) => setSport(e.target.value)}
            className="select-field"
          >
            <option value="">All Leagues</option>
            {sports.map((sport) => (
              <option key={sport} value={sport}>
                {sport}
              </option>
            ))}
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
                {formatStatType(stat)}
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
              min="5"
              max="30"
              step="2.5"
              value={filters.minProbDiff}
              onChange={(e) => setMinProbDiff(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
              <span>5%</span>
              <span>30%</span>
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
