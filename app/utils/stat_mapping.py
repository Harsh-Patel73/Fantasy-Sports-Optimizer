"""
Centralized stat type normalization for consistent naming across all scrapers.

This module provides a single source of truth for mapping various stat name
variations to canonical forms. Both Pinnacle and PrizePicks scrapers should
use this module to ensure data can be compared across sources.
"""

# Canonical stat names mapped to their known aliases
# Aliases should be lowercase with spaces and underscores removed
STAT_MAPPING = {
    # Game Lines (for moneyline, spread, totals)
    "Moneyline": [
        "moneyline",
        "h2h",
        "head2head",
        "headtohead",
        "ml",
    ],
    "Spread": [
        "spread",
        "spreads",
        "pointspread",
        "handicap",
    ],
    "Total": [
        "total",
        "totals",
        "overunder",
        "ou",
    ],

    # Football stats
    "Passing Yards": [
        "passingyards",
        "passyds",
        "player_pass_yds",
        "playerpassyds",
    ],
    "Rushing Yards": [
        "rushingyards",
        "rushyds",
        "player_rush_yds",
        "playerrushyds",
    ],
    "Receiving Yards": [
        "receivingyards",
        "recyds",
        "player_reception_yds",
        "playerreceptionyds",
    ],
    "Receptions": [
        "receptions",
        "catches",
        "rec",
        "player_receptions",
        "playerreceptions",
    ],
    "Passing TDs": [
        "passingtds",
        "passtouchdowns",
        "player_pass_tds",
        "playerpasstds",
    ],
    "Rushing TDs": [
        "rushingtds",
        "rushtouchdowns",
        "player_rush_tds",
        "playerrushtds",
    ],
    "Anytime TD": [
        "anytimetd",
        "anytimetouchdown",
        "player_anytime_td",
        "playeranytimetd",
    ],

    # Baseball stats
    "Home Runs": [
        "homeruns",
        "hrs",
        "hr",
        "batter_home_runs",
        "batterhomeruns",
    ],
    "Hits": [
        "hits",
        "batter_hits",
        "batterhits",
    ],
    "RBIs": [
        "rbis",
        "rbi",
        "runsbattedin",
        "batter_rbis",
        "batterrbis",
    ],
    "Strikeouts (Pitching)": [
        "strikeouts",
        "ks",
        "pitcher_strikeouts",
        "pitcherstrikeouts",
    ],
    "Total Bases": [
        "totalbases",
        "tb",
        "batter_total_bases",
        "battertotalbases",
    ],

    # Hockey stats
    "Goals": [
        "goals",
        "player_goals",
        "playergoals",
    ],
    "Shots On Goal": [
        "shotsongoal",
        "sog",
        "player_shots_on_goal",
        "playershotsongoal",
    ],
    "Power Play Points": [
        "powerplaypoints",
        "ppp",
        "player_power_play_points",
        "playerpowerplaypoints",
    ],

    # Combo stats
    "Pts+Rebs+Asts": [
        "pointsreboundsassists",
        "pointsreboundsassist",
        "ptsrebsasts",
        "pra",
        "pts+rebs+asts",
    ],
    "Pts+Asts": [
        "pointsassists",
        "ptsasts",
        "pa",
        "pts+asts",
    ],
    "Pts+Rebs": [
        "pointsrebounds",
        "ptsrebs",
        "pr",
        "pts+rebs",
    ],
    "Rebs+Asts": [
        "reboundsassists",
        "rebsasts",
        "ra",
        "rebs+asts",
    ],

    # Basic stats
    "Points": [
        "points",
        "pts",
    ],
    "Rebounds": [
        "rebounds",
        "rebs",
        "totalrebounds",
    ],
    "Assists": [
        "assists",
        "asts",
        "ast",
    ],
    "Steals": [
        "steals",
        "stl",
    ],
    "Blocked Shots": [
        "blocks",
        "blockedshots",
        "blk",
    ],
    "Turnovers": [
        "turnovers",
        "to",
        "tov",
    ],

    # Shooting stats
    "3-PT Made": [
        "threepointersmade",
        "threepointfieldgoals",
        "3ptmade",
        "3pm",
        "3pointersmade",
        "threeptmade",
    ],
    "3-PT Attempted": [
        "threepointersattempted",
        "3ptattempted",
        "3pa",
    ],
    "FG Made": [
        "fieldgoalsmade",
        "fgmade",
        "fgm",
    ],
    "FG Attempted": [
        "fieldgoalsattempted",
        "fgattempted",
        "fga",
    ],
    "Free Throws Made": [
        "freethrowsmade",
        "ftmade",
        "ftm",
    ],
    "Free Throws Attempted": [
        "freethrowsattempted",
        "ftattempted",
        "fta",
    ],
    "Two Pointers Attempted": [
        "twopointersattempted",
        "2ptattempted",
        "2pa",
    ],

    # Rebound breakdown
    "Defensive Rebounds": [
        "defensiverebounds",
        "drebs",
        "dreb",
    ],
    "Offensive Rebounds": [
        "offensiverebounds",
        "orebs",
        "oreb",
    ],

    # Other stats
    "Dunks": [
        "dunks",
        "dunk",
    ],
    "Fantasy Score": [
        "fantasyscore",
        "fantasypoints",
        "fantasy",
    ],
    "Personal Fouls": [
        "personalfouls",
        "fouls",
        "pf",
    ],
    "Double-Double": [
        "doubledouble",
        "dd",
    ],
    "Triple-Double": [
        "tripledouble",
        "td",
    ],
    "Minutes": [
        "minutes",
        "mins",
        "min",
    ],

    # Combo variants (for special markets)
    "Points (Combo)": [
        "pointscombo",
    ],
    "Rebounds (Combo)": [
        "reboundscombo",
    ],
    "Assists (Combo)": [
        "assistscombo",
    ],
    "3-PT Made (Combo)": [
        "threeptmadecombo",
        "3ptmadecombo",
    ],
}

# Build reverse lookup for O(1) normalization
_REVERSE_LOOKUP = {}
for canonical, aliases in STAT_MAPPING.items():
    for alias in aliases:
        _REVERSE_LOOKUP[alias] = canonical
    # Also map the canonical name to itself (normalized form)
    canonical_key = canonical.lower().replace(" ", "").replace("-", "").replace("+", "")
    _REVERSE_LOOKUP[canonical_key] = canonical


def normalize_stat_type(stat: str) -> str:
    """
    Normalize any stat name to its canonical form.

    Args:
        stat: Raw stat name from any source (Pinnacle, PrizePicks, etc.)

    Returns:
        Canonical stat name for consistent comparison across sources.
        Returns "Unknown" if stat is None/empty, or the original stat
        in title case if no mapping is found.

    Examples:
        >>> normalize_stat_type("pointsreboundsassists")
        'Pts+Rebs+Asts'
        >>> normalize_stat_type("3PM")
        '3-PT Made'
        >>> normalize_stat_type("Points")
        'Points'
    """
    if not stat:
        return "Unknown"

    # Normalize input: lowercase, remove spaces, underscores, hyphens, plus signs
    normalized_key = stat.lower().replace(" ", "").replace("_", "").replace("-", "").replace("+", "")

    # Try exact match in reverse lookup
    if normalized_key in _REVERSE_LOOKUP:
        return _REVERSE_LOOKUP[normalized_key]

    # If not found, return original with title case
    return stat.title()
