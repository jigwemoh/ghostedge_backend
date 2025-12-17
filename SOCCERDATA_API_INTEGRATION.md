# Soccerdata API Integration Guide

## Overview

The `ConsensusEngine` in `debate.py` now includes comprehensive integration with the **Soccerdata API**, which provides live scores, league statistics, and in-depth match data for 125+ worldwide leagues.

## What's New

### 1. **SoccerdataClient** (`soccerdata_client.py`)
A complete Python client for the Soccerdata API with support for:
- League standings and seasons
- Team information and transfers
- Head-to-head statistics
- Match data and previews
- Stadium information
- Live scores

### 2. **API-Enriched ConsensusEngine** 
The `ConsensusEngine.run_consensus()` method now:
- Automatically enriches match data with real API statistics
- Fetches standings, H2H, transfers, and previews
- Converts API data into quantitative and qualitative features
- Provides agents with comprehensive statistical context

### 3. **Automatic Data Enrichment**
When calling `run_consensus()`, the engine automatically:
```python
# Fetches these statistics from the API:
- League standings and positions
- Head-to-head historical data
- Recent transfers for both teams
- Team stadium information
- AI-generated match previews
- Recent match results
```

## Setup

### 1. Get API Key
- Sign up at: https://soccerdataapi.com
- Obtain your `auth_token` API key

### 2. Configure Environment
Create a `.env` file in your project root:
```
SOCCERDATA_API_KEY=your_api_key_here
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### 3. Install Dependencies
```bash
pip install requests python-dotenv
```

## Available API Endpoints

### Country & League Management
- **GET COUNTRY** - List all 220+ countries
- **GET LEAGUE** - Get leagues by country
- **GET SEASON** - Get seasons for a league
- **GET SEASON STAGES** - Get competition stages

### Team Information
- **GET TEAM** - Team details (name, country, stadium, status)
- **GET STADIUM** - Stadium information (name, city, capacity)
- **GET PLAYER** - Individual player information
- **GET TRANSFERS** - Recent transfers in/out with amounts

### Match Data
- **GET MATCHES** - Matches by league, date, or season
- **GET MATCH** - Detailed match info (lineups, events, odds, formation)
- **GET LIVE SCORES** - Live matches for current day (UTC)
- **GET HEAD-TO-HEAD** - Historical stats between two teams

### Advanced Features
- **GET STANDING** - League table with positions, points, goals
- **GET MATCH PREVIEW** - AI-powered preview with weather & predictions
- **GET UPCOMING MATCH PREVIEWS** - All upcoming match previews

## Usage Examples

### Basic API Usage
```python
from w5_engine.soccerdata_client import SoccerdataClient

client = SoccerdataClient()

# Get league standings
standings = client.get_standing(league_id=228)  # Premier League

# Get head-to-head stats
h2h = client.get_head_to_head(team_1_id=4138, team_2_id=4137)

# Get match preview
preview = client.get_match_preview(match_id=567518)

# Extract useful summary data
h2h_summary = client.extract_h2h_stats(4138, 4137)
print(f"Liverpool wins: {h2h_summary['team1_wins']}%")
```

### Using with ConsensusEngine
```python
from w5_engine.debate import ConsensusEngine

engine = ConsensusEngine()

# Prepare match data with team IDs
match_data = {
    'home_team': 'Liverpool',
    'away_team': 'Manchester United',
    'home_team_id': 4138,       # Required for API
    'away_team_id': 4137,       # Required for API
    'league_id': 228,           # Optional but recommended
    'match_id': 567518,         # Optional but recommended
    'date': '2024-01-15'
}

# Run consensus - automatically enriches with API data
result = engine.run_consensus(match_data)

print(f"Home Win: {result['consensus_prediction']['home_win']:.1%}")
print(f"API Enrichment: {result['api_enrichment']}")
```

## Data Structure

### Quantitative Features Extracted
From the API, these features are automatically extracted:
- `h2h_overall_games` - Total games between teams
- `h2h_team1_wins` - Home team historical wins
- `h2h_team2_wins` - Away team historical wins
- `h2h_draws` - Number of draws in H2H
- `h2h_team1_win_pct` - Home team win percentage
- `h2h_team1_home_wins` - Home wins at home stadium
- `league_teams_count` - Number of teams in league
- `league_leader_points` - League leader's point total

### Qualitative Context Extracted
- `weather` - Match day weather forecast (temp, condition)
- `excitement_rating` - AI-calculated match excitement (1-10)
- `ai_prediction` - AI match winner prediction
- `home_recent_signings` - Recent transfer ins count
- `home_recent_departures` - Recent transfer outs count

## Team IDs Reference

Common Premier League teams:
- Arsenal: 3068
- Liverpool: 4138
- Manchester United: 4137
- Manchester City: 4136
- Chelsea: 3170
- Brighton: 3059
- Tottenham: 2909

Common International Leagues:
- Premier League: 228
- La Liga: 206
- Serie A: 207
- Bundesliga: 204
- Ligue 1: 205
- UEFA Champions League: 310

## API Response Examples

### Standing Response
```json
{
  "stage": [{
    "stage_name": "Regular Season",
    "standings": [
      {
        "position": 1,
        "team_name": "Liverpool",
        "points": 45,
        "games_played": 18,
        "wins": 14,
        "draws": 3,
        "losses": 1,
        "goals_for": 52,
        "goals_against": 15
      }
    ]
  }]
}
```

### Head-to-Head Response
```json
{
  "stats": {
    "overall": {
      "overall_games_played": 82,
      "overall_team1_wins": 41,
      "overall_team2_wins": 24,
      "overall_draws": 17
    },
    "team1_at_home": {
      "team1_wins_at_home": 25,
      "team1_scored_at_home": 89
    }
  }
}
```

## Error Handling

The API client includes built-in error handling:
```python
# Returns None on error, prints warning
data = client.get_standing(league_id=999)  # Invalid ID
# Output: API Error: Invalid league_id

# Check for None
if data:
    process_data(data)
else:
    print("API call failed")
```

## Rate Limiting

The Soccerdata API includes rate limiting:
- Check response for: `"detail": "Request was throttled. Expected available in 60 seconds."`
- Implement exponential backoff in production

## Best Practices

1. **Cache Results** - Store API responses to avoid duplicate calls
2. **Validate IDs** - Ensure team/league IDs are correct before API calls
3. **Handle Missing Data** - Some fields may be optional (e.g., transfers)
4. **Use Extractors** - Use `extract_h2h_stats()` for processed summaries
5. **Error Handling** - Always check for None returns

## Integration with Statistical Agent

The statistical agent (`LLMAgent` with provider='deterministic') receives:
- `quantitative_features` - Numerical stats from API
- `qualitative_context` - Contextual data (weather, transfers)
- `h2h_summary` - Historical H2H text summary

This enables data-driven predictions without LLM calls.

## Advanced: Custom Data Extraction

Add custom extraction methods to `SoccerdataClient`:
```python
def get_team_form(self, team_id: int, league_id: int) -> Dict:
    """Get last 5 matches for form analysis"""
    matches = self.get_matches(league_id=league_id)
    # Filter for team_id's recent matches
    return {"wins": 3, "draws": 1, "losses": 1}
```

## API Documentation Reference

Full API docs: https://soccerdataapi.com/docs

## Troubleshooting

### "SOCCERDATA_API_KEY not found"
- Ensure `.env` file exists in project root
- Check file has: `SOCCERDATA_API_KEY=your_key`
- Run: `source .env` (if needed)

### No data returned
- Verify team/league IDs are correct
- Check API key is valid
- Review response in debug: `print(response)`

### Slow API calls
- API may be throttled
- Implement caching layer
- Batch requests efficiently

## Support

For API issues: https://soccerdataapi.com/support
For integration questions: See `api_usage_examples.py`
