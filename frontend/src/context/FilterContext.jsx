import { createContext, useContext, useReducer } from 'react';

const FilterContext = createContext();

const initialState = {
  book: 'all',
  team: '',
  player: '',
  statType: '',
  minDiff: 0.5,
  page: 1,
  perPage: 50,
};

function filterReducer(state, action) {
  switch (action.type) {
    case 'SET_BOOK':
      return { ...state, book: action.payload, page: 1 };
    case 'SET_TEAM':
      return { ...state, team: action.payload, page: 1 };
    case 'SET_PLAYER':
      return { ...state, player: action.payload, page: 1 };
    case 'SET_STAT_TYPE':
      return { ...state, statType: action.payload, page: 1 };
    case 'SET_MIN_DIFF':
      return { ...state, minDiff: action.payload };
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

  const setBook = (book) => dispatch({ type: 'SET_BOOK', payload: book });
  const setTeam = (team) => dispatch({ type: 'SET_TEAM', payload: team });
  const setPlayer = (player) => dispatch({ type: 'SET_PLAYER', payload: player });
  const setStatType = (statType) => dispatch({ type: 'SET_STAT_TYPE', payload: statType });
  const setMinDiff = (minDiff) => dispatch({ type: 'SET_MIN_DIFF', payload: minDiff });
  const setPage = (page) => dispatch({ type: 'SET_PAGE', payload: page });
  const setPerPage = (perPage) => dispatch({ type: 'SET_PER_PAGE', payload: perPage });
  const resetFilters = () => dispatch({ type: 'RESET' });

  return (
    <FilterContext.Provider
      value={{
        filters,
        setBook,
        setTeam,
        setPlayer,
        setStatType,
        setMinDiff,
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
