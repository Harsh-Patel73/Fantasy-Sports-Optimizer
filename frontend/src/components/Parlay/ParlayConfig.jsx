import { useState, useEffect } from 'react';
import { useParlay } from '../../context/ParlayContext';
import { fetchBooks } from '../../api/client';

const PARLAY_TYPES = [
  { value: '5-pick-flex', label: '5-Pick Flex', odds: '-119', percent: '54.25%' },
  { value: '6-pick-flex', label: '6-Pick Flex', odds: '-118', percent: '54.21%' },
  { value: '3-pick-flex', label: '3-Pick Flex', odds: '-137', percent: '57.74%' },
  { value: '2-pick-power', label: '2-Pick Power Play', odds: '-137', percent: '57.74%' },
];

function ParlayConfig() {
  const { parlayState, setBettingBook, setSharpBooks, setParlayType } = useParlay();
  const [books, setBooks] = useState([]);

  useEffect(() => {
    fetchBooks().then(setBooks).catch(console.error);
  }, []);

  const fantasyBooks = books.filter(b => b.type === 'Fantasy');
  const sharpBookOptions = books.filter(b => b.type === 'Sports Book');

  const handleSharpBookToggle = (bookName) => {
    if (parlayState.sharpBooks.includes(bookName)) {
      // Don't allow removing all sharp books
      if (parlayState.sharpBooks.length > 1) {
        setSharpBooks(parlayState.sharpBooks.filter(b => b !== bookName));
      }
    } else {
      setSharpBooks([...parlayState.sharpBooks, bookName]);
    }
  };

  const selectedParlayType = PARLAY_TYPES.find(t => t.value === parlayState.parlayType);

  return (
    <div className="card mb-6">
      <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">Configuration</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Betting Book */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Your Betting App
          </label>
          <select
            value={parlayState.bettingBook}
            onChange={(e) => setBettingBook(e.target.value)}
            className="select-field"
          >
            {fantasyBooks.map(book => (
              <option key={book.id || book.name} value={book.name}>
                {book.name}
              </option>
            ))}
          </select>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            The platform where you'll place your parlay
          </p>
        </div>

        {/* Sharp Books */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Sharp Books to Compare
          </label>
          <div className="flex flex-wrap gap-2">
            {sharpBookOptions.map(book => (
              <button
                key={book.id || book.name}
                onClick={() => handleSharpBookToggle(book.name)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                  parlayState.sharpBooks.includes(book.name)
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
                }`}
              >
                {book.name}
              </button>
            ))}
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Lines from these books determine if a pick is +EV
          </p>
        </div>

        {/* Parlay Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Parlay Type
          </label>
          <select
            value={parlayState.parlayType}
            onChange={(e) => setParlayType(e.target.value)}
            className="select-field"
          >
            {PARLAY_TYPES.map(type => (
              <option key={type.value} value={type.value}>
                {type.label} ({type.odds})
              </option>
            ))}
          </select>
          {selectedParlayType && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Break-even: {selectedParlayType.percent} win rate per pick
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default ParlayConfig;
