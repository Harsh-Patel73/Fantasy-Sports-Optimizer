import { createContext, useContext, useReducer } from 'react';

const ParlayContext = createContext();

const initialState = {
  bettingBook: 'DraftKings',
  sharpBooks: ['Pinnacle', 'Bovada'],
  parlayType: '5-pick-flex',
  selectedLines: [],
  mode: 'auto', // 'auto' or 'manual'
};

function parlayReducer(state, action) {
  switch (action.type) {
    case 'SET_BETTING_BOOK':
      return { ...state, bettingBook: action.payload, selectedLines: [] };
    case 'SET_SHARP_BOOKS':
      return { ...state, sharpBooks: action.payload };
    case 'SET_PARLAY_TYPE':
      return { ...state, parlayType: action.payload };
    case 'SET_MODE':
      return { ...state, mode: action.payload };
    case 'ADD_LINE':
      // Check if already added
      if (state.selectedLines.some(l => l.id === action.payload.id)) {
        return state;
      }
      return { ...state, selectedLines: [...state.selectedLines, action.payload] };
    case 'REMOVE_LINE':
      return {
        ...state,
        selectedLines: state.selectedLines.filter(l => l.id !== action.payload)
      };
    case 'CLEAR_LINES':
      return { ...state, selectedLines: [] };
    case 'RESET':
      return initialState;
    default:
      return state;
  }
}

export function ParlayProvider({ children }) {
  const [parlayState, dispatch] = useReducer(parlayReducer, initialState);

  const setBettingBook = (book) => dispatch({ type: 'SET_BETTING_BOOK', payload: book });
  const setSharpBooks = (books) => dispatch({ type: 'SET_SHARP_BOOKS', payload: books });
  const setParlayType = (type) => dispatch({ type: 'SET_PARLAY_TYPE', payload: type });
  const setMode = (mode) => dispatch({ type: 'SET_MODE', payload: mode });
  const addLine = (line) => dispatch({ type: 'ADD_LINE', payload: line });
  const removeLine = (id) => dispatch({ type: 'REMOVE_LINE', payload: id });
  const clearLines = () => dispatch({ type: 'CLEAR_LINES' });
  const resetParlay = () => dispatch({ type: 'RESET' });

  return (
    <ParlayContext.Provider value={{
      parlayState,
      setBettingBook,
      setSharpBooks,
      setParlayType,
      setMode,
      addLine,
      removeLine,
      clearLines,
      resetParlay,
    }}>
      {children}
    </ParlayContext.Provider>
  );
}

export function useParlay() {
  const context = useContext(ParlayContext);
  if (!context) {
    throw new Error('useParlay must be used within a ParlayProvider');
  }
  return context;
}
