"""
Team ID Database and Mapping
Maps team names to their correct Soccerdata IDs
"""

# Premier League (League ID: 39)
TEAM_ID_DATABASE = {
    "Premier League": {
        "Manchester City": 50,
        "Man City": 50,
        "Liverpool": 64,
        "Arsenal": 42,
        "Manchester United": 33,
        "Man United": 33,
        "Chelsea": 49,
        "Tottenham": 47,
        "Tottenham Hotspur": 47,
        "West Ham": 48,
        "West Ham United": 48,
        "Aston Villa": 74,
        "Brighton": 51,
        "Brighton and Hove Albion": 51,
        "Fulham": 63,
        "Bournemouth": 35,
        "Brentford": 130,
        "Everton": 62,
        "Ipswich": 78,
        "Ipswich Town": 78,
        "Leicester": 34,
        "Leicester City": 34,
        "Southampton": 20,
        "Nottingham": 51,
        "Nottingham Forest": 51,
        "Luton": 81,
        "Luton Town": 81,
        "Wolverhampton": 39,
        "Wolves": 39,
        "Crystal Palace": 52,
    },
    "La Liga": {
        "Real Madrid": 418,
        "Barcelona": 206,
        "Atletico Madrid": 7,
        "Atletico": 7,
        "Sevilla": 541,
        "Valencia": 799,
        "Villarreal": 483,
        "Athletic Club": 205,
        "Athletic Bilbao": 205,
        "Real Betis": 559,
        "Betis": 559,
        "Osasuna": 500,
        "Getafe": 170,
    },
    "Serie A": {
        "Juventus": 496,
        "AC Milan": 98,
        "Milan": 98,
        "Inter Milan": 505,
        "Inter": 505,
        "Roma": 497,
        "AS Roma": 497,
        "Napoli": 484,
        "Lazio": 502,
        "Fiorentina": 110,
        "Atalanta": 344,
        "Torino": 498,
        "Bologna": 485,
        "Sassuolo": 486,
        "Monza": 487,
    },
    "Bundesliga": {
        "Bayern Munich": 25,
        "Bayern": 25,
        "Borussia Dortmund": 16,
        "Dortmund": 16,
        "BVB": 16,
        "Bayer Leverkusen": 143,
        "Leverkusen": 143,
        "RB Leipzig": 173,
        "Leipzig": 173,
        "Schalke 04": 2,
        "Schalke": 2,
        "Hamburg": 181,
        "Werder Bremen": 134,
        "Bremen": 134,
    },
    "Ligue 1": {
        "Paris Saint-Germain": 891,
        "PSG": 891,
        "Paris": 891,
        "Marseille": 892,
        "Lyon": 893,
        "Monaco": 894,
        "Lens": 895,
        "Lille": 896,
        "Nantes": 897,
        "Nice": 898,
    },
}

def find_team_id(team_name: str, league_name: str = None) -> int:
    """
    Find team ID by name and optional league
    
    Args:
        team_name: Name of the team
        league_name: Optional league name (e.g., "Premier League", "La Liga")
    
    Returns:
        Team ID if found, None otherwise
    """
    if not team_name:
        return None
    
    team_lower = team_name.lower().strip()
    
    # If league specified, search within that league first
    if league_name and league_name in TEAM_ID_DATABASE:
        league_teams = TEAM_ID_DATABASE[league_name]
        for name, team_id in league_teams.items():
            if name.lower() == team_lower or team_lower in name.lower() or name.lower() in team_lower:
                return team_id
    
    # Search all leagues
    for league, teams in TEAM_ID_DATABASE.items():
        for name, team_id in teams.items():
            if name.lower() == team_lower or team_lower in name.lower() or name.lower() in team_lower:
                return team_id
    
    return None

def get_all_team_ids(league_name: str) -> dict:
    """Get all team IDs for a specific league"""
    if league_name in TEAM_ID_DATABASE:
        return TEAM_ID_DATABASE[league_name]
    return {}

# Test
if __name__ == "__main__":
    print("Team ID Database Test")
    print("=" * 50)
    
    test_teams = ["Manchester City", "Man City", "Liverpool", "West Ham"]
    for team in test_teams:
        team_id = find_team_id(team)
        print(f"{team:25} → ID: {team_id}")
