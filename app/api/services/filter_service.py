from sqlalchemy import func, distinct, or_
from app.db.session import get_session
from app.models.statlines import Statlines
from app.models.books import Books
from app.models.matchups import Matchups
from app.models.props import Props

# Sport inference from team names
TEAM_TO_SPORT = {
    # NFL Teams
    'Arizona Cardinals': 'NFL', 'Atlanta Falcons': 'NFL', 'Baltimore Ravens': 'NFL',
    'Buffalo Bills': 'NFL', 'Carolina Panthers': 'NFL', 'Chicago Bears': 'NFL',
    'Cincinnati Bengals': 'NFL', 'Cleveland Browns': 'NFL', 'Dallas Cowboys': 'NFL',
    'Denver Broncos': 'NFL', 'Detroit Lions': 'NFL', 'Green Bay Packers': 'NFL',
    'Houston Texans': 'NFL', 'Indianapolis Colts': 'NFL', 'Jacksonville Jaguars': 'NFL',
    'Kansas City Chiefs': 'NFL', 'Las Vegas Raiders': 'NFL', 'Los Angeles Chargers': 'NFL',
    'Los Angeles Rams': 'NFL', 'Miami Dolphins': 'NFL', 'Minnesota Vikings': 'NFL',
    'New England Patriots': 'NFL', 'New Orleans Saints': 'NFL', 'New York Giants': 'NFL',
    'New York Jets': 'NFL', 'Philadelphia Eagles': 'NFL', 'Pittsburgh Steelers': 'NFL',
    'San Francisco 49ers': 'NFL', 'Seattle Seahawks': 'NFL', 'Tampa Bay Buccaneers': 'NFL',
    'Tennessee Titans': 'NFL', 'Washington Commanders': 'NFL',
    # NBA Teams
    'Atlanta Hawks': 'NBA', 'Boston Celtics': 'NBA', 'Brooklyn Nets': 'NBA',
    'Charlotte Hornets': 'NBA', 'Chicago Bulls': 'NBA', 'Cleveland Cavaliers': 'NBA',
    'Dallas Mavericks': 'NBA', 'Denver Nuggets': 'NBA', 'Detroit Pistons': 'NBA',
    'Golden State Warriors': 'NBA', 'Houston Rockets': 'NBA', 'Indiana Pacers': 'NBA',
    'Los Angeles Clippers': 'NBA', 'Los Angeles Lakers': 'NBA', 'Memphis Grizzlies': 'NBA',
    'Miami Heat': 'NBA', 'Milwaukee Bucks': 'NBA', 'Minnesota Timberwolves': 'NBA',
    'New Orleans Pelicans': 'NBA', 'New York Knicks': 'NBA', 'Oklahoma City Thunder': 'NBA',
    'Orlando Magic': 'NBA', 'Philadelphia 76ers': 'NBA', 'Phoenix Suns': 'NBA',
    'Portland Trail Blazers': 'NBA', 'Sacramento Kings': 'NBA', 'San Antonio Spurs': 'NBA',
    'Toronto Raptors': 'NBA', 'Utah Jazz': 'NBA', 'Washington Wizards': 'NBA',
    # NHL Teams
    'Anaheim Ducks': 'NHL', 'Arizona Coyotes': 'NHL', 'Boston Bruins': 'NHL',
    'Buffalo Sabres': 'NHL', 'Calgary Flames': 'NHL', 'Carolina Hurricanes': 'NHL',
    'Chicago Blackhawks': 'NHL', 'Colorado Avalanche': 'NHL', 'Columbus Blue Jackets': 'NHL',
    'Dallas Stars': 'NHL', 'Detroit Red Wings': 'NHL', 'Edmonton Oilers': 'NHL',
    'Florida Panthers': 'NHL', 'Los Angeles Kings': 'NHL', 'Minnesota Wild': 'NHL',
    'Montréal Canadiens': 'NHL', 'Nashville Predators': 'NHL', 'New Jersey Devils': 'NHL',
    'New York Islanders': 'NHL', 'New York Rangers': 'NHL', 'Ottawa Senators': 'NHL',
    'Philadelphia Flyers': 'NHL', 'Pittsburgh Penguins': 'NHL', 'San Jose Sharks': 'NHL',
    'Seattle Kraken': 'NHL', 'St. Louis Blues': 'NHL', 'Tampa Bay Lightning': 'NHL',
    'Toronto Maple Leafs': 'NHL', 'Vancouver Canucks': 'NHL', 'Vegas Golden Knights': 'NHL',
    'Washington Capitals': 'NHL', 'Winnipeg Jets': 'NHL', 'Utah Mammoth': 'NHL',
    # MLB Teams
    'Arizona Diamondbacks': 'MLB', 'Atlanta Braves': 'MLB', 'Baltimore Orioles': 'MLB',
    'Boston Red Sox': 'MLB', 'Chicago Cubs': 'MLB', 'Chicago White Sox': 'MLB',
    'Cincinnati Reds': 'MLB', 'Cleveland Guardians': 'MLB', 'Colorado Rockies': 'MLB',
    'Detroit Tigers': 'MLB', 'Houston Astros': 'MLB', 'Kansas City Royals': 'MLB',
    'Los Angeles Angels': 'MLB', 'Los Angeles Dodgers': 'MLB', 'Miami Marlins': 'MLB',
    'Milwaukee Brewers': 'MLB', 'Minnesota Twins': 'MLB', 'New York Mets': 'MLB',
    'New York Yankees': 'MLB', 'Oakland Athletics': 'MLB', 'Philadelphia Phillies': 'MLB',
    'Pittsburgh Pirates': 'MLB', 'San Diego Padres': 'MLB', 'San Francisco Giants': 'MLB',
    'Seattle Mariners': 'MLB', 'St. Louis Cardinals': 'MLB', 'Tampa Bay Rays': 'MLB',
    'Texas Rangers': 'MLB', 'Toronto Blue Jays': 'MLB', 'Washington Nationals': 'MLB',
}


def get_sport_for_team(team_name):
    """Get sport for a team name."""
    return TEAM_TO_SPORT.get(team_name, None)


def get_unique_sports():
    """Get all unique sports from matchups based on team names."""
    Session = get_session()
    session = Session()

    try:
        # Get all unique teams
        home_teams = session.query(distinct(Matchups.home_team)).all()
        away_teams = session.query(distinct(Matchups.away_team)).all()

        sports = set()
        for (team,) in home_teams + away_teams:
            if team:
                sport = get_sport_for_team(team)
                if sport:
                    sports.add(sport)

        return sorted(list(sports))

    finally:
        session.close()


def get_unique_teams(sport=None):
    """Get all unique team names from matchups, optionally filtered by sport."""
    Session = get_session()
    session = Session()

    try:
        # Get all home teams
        home_teams = session.query(distinct(Matchups.home_team)).filter(
            Matchups.home_team.isnot(None)
        ).all()

        # Get all away teams
        away_teams = session.query(distinct(Matchups.away_team)).filter(
            Matchups.away_team.isnot(None)
        ).all()

        # Combine and deduplicate
        teams = set()
        for (team,) in home_teams:
            if team:
                # Filter by sport if specified
                if sport:
                    team_sport = get_sport_for_team(team)
                    if team_sport == sport:
                        teams.add(team)
                else:
                    teams.add(team)
        for (team,) in away_teams:
            if team:
                if sport:
                    team_sport = get_sport_for_team(team)
                    if team_sport == sport:
                        teams.add(team)
                else:
                    teams.add(team)

        return sorted(list(teams))

    finally:
        session.close()


def get_unique_players(team=None):
    """Get all unique player names from statlines, optionally filtered by team."""
    Session = get_session()
    session = Session()

    try:
        query = session.query(distinct(Statlines.player_name)).filter(
            Statlines.player_name.isnot(None)
        )

        # Filter by team if provided
        if team:
            from sqlalchemy import or_
            query = query.join(Matchups, Statlines.matchup_id == Matchups.matchup_id).filter(
                or_(
                    Matchups.home_team == team,
                    Matchups.away_team == team
                )
            )

        players = query.order_by(Statlines.player_name).all()
        return [player for (player,) in players if player]

    finally:
        session.close()


def get_unique_stat_types():
    """Get all unique stat types from props."""
    Session = get_session()
    session = Session()

    try:
        stat_types = session.query(distinct(Props.units)).filter(
            Props.units.isnot(None)
        ).order_by(Props.units).all()

        return [stat for (stat,) in stat_types if stat]

    finally:
        session.close()


def get_books():
    """Get all sportsbooks/platforms."""
    Session = get_session()
    session = Session()

    try:
        books = session.query(Books).order_by(Books.book_name).all()

        return [
            {
                'id': book.book_id,
                'name': book.book_name,
                'type': book.book_type
            }
            for book in books
        ]

    finally:
        session.close()
