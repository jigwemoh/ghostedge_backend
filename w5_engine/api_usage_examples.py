"""
Example usage of the Soccerdata API integration with ConsensusEngine

This script demonstrates how to use the enhanced ConsensusEngine
with real Soccerdata API statistics for match prediction.
"""

from w5_engine.debate import ConsensusEngine
from w5_engine.soccerdata_client import SoccerdataClient

def example_basic_api_usage():
    """Example: Basic Soccerdata API usage"""
    client = SoccerdataClient()
    
    # Example: Get standings for Premier League (ID: 228)
    standings = client.get_standing(league_id=228)
    print("League Standing:", standings)
    
    # Example: Get head-to-head between Liverpool (4138) and Man United (4137)
    h2h = client.get_head_to_head(team_1_id=4138, team_2_id=4137)
    print("H2H Stats:", h2h)
    
    # Example: Get transfers for Liverpool
    transfers = client.get_transfers(team_id=4138)
    print("Recent Transfers:", transfers)
    
    # Example: Get match preview
    preview = client.get_match_preview(match_id=567518)
    print("Match Preview:", preview)
    
    # Example: Get live scores
    live = client.get_livescores()
    print("Live Scores:", live)


def example_consensus_with_api_enrichment():
    """Example: Using ConsensusEngine with API-enriched data"""
    
    # Initialize the engine (automatically initializes SoccerdataClient)
    engine = ConsensusEngine(debate_rounds=2)
    
    # Prepare match data with team/league IDs for API enrichment
    match_data = {
        'home_team': 'Liverpool',
        'away_team': 'Manchester United',
        'home_team_id': 4138,      # Required for API calls
        'away_team_id': 4137,      # Required for API calls
        'league_id': 228,          # Premier League
        'match_id': 567518,        # For match preview
        'date': '2024-01-15',
        'venue': 'Anfield'
    }
    
    # Run consensus - automatically enriches with API data
    result = engine.run_consensus(match_data)
    
    print("\n" + "="*60)
    print("CONSENSUS RESULT")
    print("="*60)
    print(f"Home Win: {result['consensus_prediction']['home_win']:.1%}")
    print(f"Draw: {result['consensus_prediction']['draw']:.1%}")
    print(f"Away Win: {result['consensus_prediction']['away_win']:.1%}")
    print("\nAgent Analyses:")
    for agent in result['agent_analyses']:
        print(f"  - {agent['agent']}: {agent['reasoning']}")
    
    # Show API enrichment data
    print("\nAPI Enrichment Data:")
    api_stats = result.get('api_enrichment', {})
    if api_stats.get('head_to_head'):
        print("  ✓ H2H Stats Fetched")
    if api_stats.get('league_standing'):
        print("  ✓ League Standing Fetched")
    if api_stats.get('match_preview'):
        print("  ✓ Match Preview Fetched")


def example_statistical_agent_focus():
    """Example: Direct statistical analysis using API data"""
    
    client = SoccerdataClient()
    
    # Get comprehensive stats for two teams
    h2h = client.get_head_to_head(team_1_id=4138, team_2_id=4137)
    h2h_stats = client.extract_h2h_stats(team_1_id=4138, team_2_id=4137)
    
    print("Head-to-Head Analysis:")
    print(f"  {h2h_stats['team1_name']} vs {h2h_stats['team2_name']}")
    print(f"  Overall Games: {h2h_stats['overall_games']}")
    print(f"  {h2h_stats['team1_name']} Wins: {h2h_stats['team1_wins']} ({h2h_stats['team1_win_percentage']}%)")
    print(f"  {h2h_stats['team2_name']} Wins: {h2h_stats['team2_wins']} ({100 - h2h_stats['team1_win_percentage']}%)")
    print(f"  Draws: {h2h_stats['draws']}")
    print(f"  {h2h_stats['team1_name']} Home Wins: {h2h_stats['team1_home_wins']}")
    
    # Get league standings
    standing = client.get_standing(league_id=228)
    print("\nLeague Position Comparison:")
    if standing and standing.get('stage'):
        for team_standing in standing['stage'][0]['standings'][:5]:
            print(f"  #{team_standing['position']}: {team_standing['team_name']} - {team_standing['points']}pts")


def example_all_api_endpoints():
    """Example: Comprehensive overview of all available endpoints"""
    
    client = SoccerdataClient()
    
    print("Available Soccerdata API Endpoints:")
    print("\n1. GET COUNTRY")
    print("   - Get list of 220+ countries")
    countries = client.get_country()
    
    print("\n2. GET LEAGUE")
    print("   - Get leagues by country_id")
    leagues = client.get_league(country_id=8)  # England
    
    print("\n3. GET SEASON")
    print("   - Get seasons for a league")
    seasons = client.get_season(league_id=228)
    
    print("\n4. GET STANDING")
    print("   - Get league table with positions, points, goals")
    standing = client.get_standing(league_id=228)
    
    print("\n5. GET TEAM")
    print("   - Get team information")
    team = client.get_team(team_id=4138)
    
    print("\n6. GET PLAYER")
    print("   - Get player information (requires player_id)")
    
    print("\n7. GET TRANSFERS")
    print("   - Get transfers in/out for a team")
    transfers = client.get_transfers(team_id=4138)
    
    print("\n8. GET STADIUM")
    print("   - Get stadium information for a team")
    stadium = client.get_stadium(team_id=4138)
    
    print("\n9. GET HEAD-TO-HEAD")
    print("   - Get historical stats between two teams")
    h2h = client.get_head_to_head(team_1_id=4138, team_2_id=4137)
    
    print("\n10. GET MATCH")
    print("    - Get detailed match info including lineups, events, odds")
    match = client.get_match(match_id=567518)
    
    print("\n11. GET MATCHES")
    print("    - Get matches by league, date, or season")
    matches = client.get_matches(league_id=228)
    
    print("\n12. GET MATCH PREVIEW")
    print("    - Get AI-generated match preview with weather & predictions")
    preview = client.get_match_preview(match_id=567518)
    
    print("\n13. GET LIVE SCORES")
    print("    - Get live matches for current day")
    live = client.get_livescores()
    
    print("\n14. GET UPCOMING MATCH PREVIEWS")
    print("    - Get previews for upcoming matches")
    upcoming = client.get_upcoming_match_previews()


# ============================================================================
# ENVIRONMENT SETUP REQUIRED:
# ============================================================================
# Before running these examples, set the following environment variables:
#
# export SOCCERDATA_API_KEY="your_api_key_here"
# export OPENAI_API_KEY="your_openai_key"
# export ANTHROPIC_API_KEY="your_anthropic_key"
#
# Add these to your .env file in the project root:
# SOCCERDATA_API_KEY=your_api_key_here
# OPENAI_API_KEY=your_openai_key
# ANTHROPIC_API_KEY=your_anthropic_key
#
# ============================================================================


if __name__ == '__main__':
    # Uncomment the example you want to run:
    
    # example_basic_api_usage()
    example_consensus_with_api_enrichment()
    # example_statistical_agent_focus()
    # example_all_api_endpoints()
