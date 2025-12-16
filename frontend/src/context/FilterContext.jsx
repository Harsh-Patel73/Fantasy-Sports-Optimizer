import { createContext, useContext, useReducer } from 'react';

const FilterContext = createContext();

const initialState = {
  books: [],  // Empty array means "all books"
  sport: '',
  team: '',
  player: '',
  statType: '',
  search: '',
  minProbDiff: 5,
  page: 1,
  perPage: 50,
};

function filterReducer(state, action) {
  switch (action.type) {
    case 'SET_BOOKS':
      return { ...state, books: action.payload, page: 1 };
    case 'SET_SPORT':
      // Clear team and player when sport changes
      return { ...state, sport: action.payload, team: '', player: '', page: 1 };
    case 'SET_TEAM':
      // Clear player when team changes
      return { ...state, team: action.payload, player: '', page: 1 };
    case 'SET_PLAYER':
      return { ...state, player: action.payload, page: 1 };
    case 'SET_STAT_TYPE':
      return { ...state, statType: action.payload, page: 1 };
    case 'SET_SEARCH':
      return { ...state, search: action.payload, page: 1 };
    case 'SET_MIN_PROB_DIFF':
      return { ...state, minProbDiff: action.payload };
    case 'SET_PAGE':
      return { ...state, page: action.payload };
    case 'SET_PER_PAGE':
      return { ...state, perPage: action.payload, page: 1 };
    case 'RESET':
      return initialState;
    default:
      return state;
  }
}

export function FilterProvider({ children }) {
  const [filters, dispatch] = useReducer(filterReducer, initialState);

  const setBooks = (books) => dispatch({ type: 'SET_BOOKS', payload: books });
  const setSport = (sport) => dispatch({ type: 'SET_SPORT', payload: sport });
  const setTeam = (team) => dispatch({ type: 'SET_TEAM', payload: team });
  const setPlayer = (player) => dispatch({ type: 'SET_PLAYER', payload: player });
  const setStatType = (statType) => dispatch({ type: 'SET_STAT_TYPE', payload: statType });
  const setSearch = (search) => dispatch({ type: 'SET_SEARCH', payload: search });
  const setMinProbDiff = (minProbDiff) => dispatch({ type: 'SET_MIN_PROB_DIFF', payload: minProbDiff });
  const setPage = (page) => dispatch({ type: 'SET_PAGE', payload: page });
  const setPerPage = (perPage) => dispatch({ type: 'SET_PER_PAGE', payload: perPage });
  const resetFilters = () => dispatch({ type: 'RESET' });

  return (
    <FilterContext.Provider
      value={{
        filters,
        setBooks,
        setSport,
        setTeam,
        setPlayer,
        setStatType,
        setSearch,
        setMinProbDiff,
        setPage,
        setPerPage,
        resetFilters,
      }}
    >
      {children}
    </FilterContext.Provider>
  );
}

export function useFilters() {
  const context = useContext(FilterContext);
  if (!context) {
    throw new Error('useFilters must be used within a FilterProvider');
  }
  return context;
}
