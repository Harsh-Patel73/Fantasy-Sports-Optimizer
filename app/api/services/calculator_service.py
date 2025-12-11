"""
Calculator service for betting math operations.

Provides devigging algorithms and parlay break-even calculations.
"""
import math


def american_to_implied(odds):
    """Convert American odds to implied probability.

    Args:
        odds: American odds (e.g., -110, +150)

    Returns:
        Implied probability as decimal (0.0 to 1.0)
    """
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    return 100 / (odds + 100)


def implied_to_american(prob):
    """Convert implied probability to American odds.

    Args:
        prob: Probability as decimal (0.0 to 1.0)

    Returns:
        American odds (negative for favorites, positive for underdogs)
    """
    if prob <= 0 or prob >= 1:
        return None
    if prob >= 0.5:
        return round(-100 * prob / (1 - prob))
    return round(100 * (1 - prob) / prob)


def devig_two_way(odds_1, odds_2, method='multiplicative'):
    """Remove vig from two-way betting lines.

    Args:
        odds_1: American odds for side 1 (e.g., -110)
        odds_2: American odds for side 2 (e.g., -110)
        method: Devigging method - 'multiplicative', 'additive', or 'power'

    Returns:
        Dictionary with true probabilities, fair odds, and vig info

    Methods:
        - multiplicative (proportional): Distribute vig proportionally
          true_prob = implied_prob / sum(implied_probs)

        - additive (equal split): Split vig equally between sides
          true_prob = implied_prob - (vig / 2)

        - power: Better for heavy favorites, uses power function
          Solve for k where: prob1^k + prob2^k = 1
          Then: true_prob = implied_prob^k
    """
    imp_1 = american_to_implied(odds_1)
    imp_2 = american_to_implied(odds_2)
    total_implied = imp_1 + imp_2
    total_vig = (total_implied - 1) * 100  # As percentage

    if method == 'multiplicative':
        true_1 = imp_1 / total_implied
        true_2 = imp_2 / total_implied

    elif method == 'additive':
        vig_per_side = (total_implied - 1) / 2
        true_1 = imp_1 - vig_per_side
        true_2 = imp_2 - vig_per_side
        # Ensure probabilities stay valid
        true_1 = max(0.001, min(0.999, true_1))
        true_2 = max(0.001, min(0.999, true_2))

    elif method == 'power':
        # Solve: imp_1^k + imp_2^k = 1 using bisection method
        # k is typically between 0 and 1 when there's vig
        def equation(k):
            return imp_1**k + imp_2**k - 1

        # Bisection search for k
        k = _bisect(equation, 0.001, 2.0, tolerance=1e-6)
        true_1 = imp_1**k
        true_2 = imp_2**k
    else:
        raise ValueError(f"Unknown method: {method}. Use 'multiplicative', 'additive', or 'power'")

    return {
        'true_prob_1': round(true_1, 4),
        'true_prob_2': round(true_2, 4),
        'true_percent_1': round(true_1 * 100, 2),
        'true_percent_2': round(true_2 * 100, 2),
        'fair_odds_1': implied_to_american(true_1),
        'fair_odds_2': implied_to_american(true_2),
        'total_vig': round(total_vig, 2),
        'method_used': method,
        'input_odds_1': odds_1,
        'input_odds_2': odds_2,
        'implied_prob_1': round(imp_1, 4),
        'implied_prob_2': round(imp_2, 4),
    }


def _bisect(func, a, b, tolerance=1e-6, max_iterations=100):
    """Simple bisection method for finding roots.

    Finds x where func(x) = 0 in the interval [a, b].
    """
    fa = func(a)
    fb = func(b)

    if fa * fb > 0:
        # Same sign, try to find a better interval
        # For the power method, we know k should be near 1
        return 1.0

    for _ in range(max_iterations):
        mid = (a + b) / 2
        fmid = func(mid)

        if abs(fmid) < tolerance:
            return mid

        if fa * fmid < 0:
            b = mid
            fb = fmid
        else:
            a = mid
            fa = fmid

    return (a + b) / 2


# Payout structures for PrizePicks-style parlays
PAYOUT_STRUCTURES = {
    '5-pick-flex': {5: 10.0, 4: 2.0, 3: 0.4},
    '6-pick-flex': {6: 25.0, 5: 2.0, 4: 0.4},
    '3-pick-flex': {3: 2.25, 2: 1.25},
    '2-pick-power': {2: 3.0},
}

# Pre-calculated break-even probabilities for quick reference
BREAKEVEN_PROBS = {
    '5-pick-flex': 0.5425,    # ~-119 odds
    '6-pick-flex': 0.5421,    # ~-118 odds
    '3-pick-flex': 0.5774,    # ~-137 odds
    '2-pick-power': 0.5774,   # ~-137 odds
}


def calculate_parlay_breakeven(parlay_type):
    """Calculate break-even probability for PrizePicks-style parlays.

    Uses the equation: sum(payout * C(n,k) * p^k * (1-p)^(n-k)) = 1
    Solves for p (break-even probability per pick).

    Args:
        parlay_type: One of '5-pick-flex', '6-pick-flex', '3-pick-flex', '2-pick-power'

    Returns:
        Dictionary with parlay info, break-even probability, and odds
    """
    if parlay_type not in PAYOUT_STRUCTURES:
        return {
            'error': f"Unknown parlay type: {parlay_type}",
            'valid_types': list(PAYOUT_STRUCTURES.keys())
        }

    payouts = PAYOUT_STRUCTURES[parlay_type]
    n = max(payouts.keys())  # Total picks

    def expected_value(p):
        """Calculate expected value given probability p."""
        ev = 0
        for k, payout in payouts.items():
            combinations = math.comb(n, k)
            prob_k = combinations * (p ** k) * ((1 - p) ** (n - k))
            ev += payout * prob_k
        return ev - 1  # Subtract 1 (the stake) to find break-even

    # Find break-even probability using bisection
    # p must be between 0 and 1
    breakeven_prob = _bisect(expected_value, 0.01, 0.99, tolerance=1e-6)

    # Calculate edge for reference (if you hit at 50% vs break-even)
    edge_vs_coinflip = breakeven_prob - 0.5

    return {
        'parlay_type': parlay_type,
        'total_picks': n,
        'payout_structure': payouts,
        'breakeven_prob': round(breakeven_prob, 4),
        'breakeven_percent': round(breakeven_prob * 100, 2),
        'breakeven_odds': implied_to_american(breakeven_prob),
        'edge_vs_coinflip': round(edge_vs_coinflip * 100, 2),
        'explanation': f"Each pick must hit at {round(breakeven_prob * 100, 2)}% ({implied_to_american(breakeven_prob)} odds) to break even"
    }


def get_breakeven_prob(parlay_type):
    """Get the pre-calculated break-even probability for a parlay type.

    Args:
        parlay_type: One of '5-pick-flex', '6-pick-flex', '3-pick-flex', '2-pick-power'

    Returns:
        Break-even probability as decimal, or None if invalid type
    """
    return BREAKEVEN_PROBS.get(parlay_type)
