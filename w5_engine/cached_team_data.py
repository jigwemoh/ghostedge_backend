"""
Cached team data for when API is throttled
Provides realistic fallback data for testing
"""

CACHED_TEAM_DATA = {
    50: {  # Manchester City
        "name": "Manchester City",
        "stadium": "Etihad Stadium",
        "capacity": 55097,
        "country": "England",
        "recent_signings": [
            {"name": "Kalvin Phillips", "date": "2022-07-01"},
            {"name": "Erling Haaland", "date": "2022-06-15"},
            {"name": "Sergio Gómez", "date": "2022-07-13"},
            {"name": "Manuel Akanji", "date": "2022-09-01"},
        ],
        "recent_departures": [
            {"name": "Gabriel Jesus", "date": "2022-07-06"},
            {"name": "Oleksandr Zinchenko", "date": "2022-08-31"},
        ]
    },
    48: {  # West Ham
        "name": "West Ham United",
        "stadium": "London Stadium",
        "capacity": 62500,
        "country": "England",
        "recent_signings": [
            {"name": "Gianluca Scamacca", "date": "2022-07-24"},
            {"name": "Alphonse Areola", "date": "2022-08-30"},
            {"name": "Nayef Aguerd", "date": "2022-07-24"},
        ],
        "recent_departures": [
            {"name": "Jesse Lingard", "date": "2022-06-01"},
        ]
    },
    64: {  # Liverpool
        "name": "Liverpool FC",
        "stadium": "Anfield",
        "capacity": 61294,
        "country": "England",
        "recent_signings": [
            {"name": "Luis Diaz", "date": "2022-01-28"},
            {"name": "Fabio Carvalho", "date": "2022-07-01"},
            {"name": "Darwin Núñez", "date": "2022-07-01"},
        ],
        "recent_departures": [
            {"name": "Sadio Mané", "date": "2022-06-08"},
            {"name": "Naby Keïta", "date": "2022-07-01"},
        ]
    },
    42: {  # Arsenal
        "name": "Arsenal FC",
        "stadium": "Emirates Stadium",
        "capacity": 60260,
        "country": "England",
        "recent_signings": [
            {"name": "Gabriel Jesus", "date": "2022-07-06"},
            {"name": "Lisandro Martínez", "date": "2022-08-05"},
            {"name": "Oleksandr Zinchenko", "date": "2022-08-31"},
        ],
        "recent_departures": [
            {"name": "Pierre-Emerick Aubameyang", "date": "2022-02-01"},
        ]
    },
}

CACHED_H2H_DATA = {
    (50, 48): {  # Man City vs West Ham
        "overall_games": 48,
        "team1_wins": 26,
        "team2_wins": 10,
        "draws": 12,
        "team1_home_wins": 16,
        "team1_win_percentage": 54.17,
    },
    (64, 48): {  # Liverpool vs West Ham
        "overall_games": 42,
        "team1_wins": 24,
        "team2_wins": 8,
        "draws": 10,
        "team1_home_wins": 14,
        "team1_win_percentage": 57.14,
    },
    (42, 48): {  # Arsenal vs West Ham
        "overall_games": 39,
        "team1_wins": 20,
        "team2_wins": 9,
        "draws": 10,
        "team1_home_wins": 12,
        "team1_win_percentage": 51.28,
    },
}

CACHED_LEAGUE_DATA = {
    39: {  # Premier League
        "name": "Premier League",
        "season": "2024-25",
        "standings": [
            {"rank": 1, "name": "Arsenal", "points": 80, "games_played": 30},
            {"rank": 2, "name": "Manchester City", "points": 78, "games_played": 30},
            {"rank": 3, "name": "Liverpool", "points": 74, "games_played": 30},
            {"rank": 4, "name": "Aston Villa", "points": 71, "games_played": 30},
            {"rank": 5, "name": "Tottenham", "points": 68, "games_played": 30},
            {"rank": 6, "name": "Chelsea", "points": 65, "games_played": 30},
        ]
    }
}

def get_cached_team_data(team_id: int):
    """Get cached team data"""
    return CACHED_TEAM_DATA.get(team_id)

def get_cached_h2h_data(team1_id: int, team2_id: int):
    """Get cached H2H data"""
    # Try both orders
    return CACHED_H2H_DATA.get((team1_id, team2_id)) or CACHED_H2H_DATA.get((team2_id, team1_id))

def get_cached_league_data(league_id: int):
    """Get cached league data"""
    return CACHED_LEAGUE_DATA.get(league_id)
