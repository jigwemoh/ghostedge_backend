import os
import requests
import logging
from typing import Dict, Any, List, Optional, Union
from w5_engine.soccerdata_client import SoccerdataClient
from w5_engine.team_id_database import find_team_id as find_team_id_in_db

# --- CONFIGURATION ---
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "free-api-live-football-data.p.rapidapi.com"
BASE_URL = "https://free-api-live-football-data.p.rapidapi.com"

class SoccerDataLoader:
    def __init__(self, season: str = "2024"):
        self.headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": API_HOST
        }
        self.soccerdata_client = SoccerdataClient()
        
        if not RAPIDAPI_KEY:
            print("❌ WARNING: RAPIDAPI_KEY not found in environment.")

    def _get(self, endpoint: str, params: Dict) -> Dict:
        """Helper to make API calls safely."""
        try:
            url = f"{BASE_URL}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return {}

    def _validate_team_id(self, team_id: int, expected_team_name: str) -> bool:
        """Verify that the team_id matches the expected team name"""
        if not team_id or not expected_team_name:
            return True  # Skip validation if no expected name
        
        try:
            team_info = self.soccerdata_client.get_team(team_id)
            if team_info:
                actual_name = team_info.get('name', '').lower()
                expected_lower = expected_team_name.lower()
                # Check if expected team name is in actual name or vice versa
                if expected_lower in actual_name or actual_name in expected_lower:
                    return True
                else:
                    print(f"⚠️  Team ID mismatch: Expected '{expected_team_name}' but got '{team_info.get('name', 'Unknown')}'")
                    return False
        except Exception as e:
            print(f"⚠️  Could not validate team {team_id}: {str(e)}")
        
        return True  # Don't fail on validation errors
    
    def _get_correct_team_id(self, team_name: str, league_id: int) -> Optional[int]:
        """Automatically find the correct team ID by searching local database first, then API"""
        if not team_name:
            return None
        
        # Try local database first (instant, no API call)
        try:
            print(f"🔍 Looking up {team_name} in team database...")
            correct_id = find_team_id_in_db(team_name)
            
            if correct_id:
                print(f"✅ Found in database: {team_name} (ID: {correct_id})")
                return correct_id
        except Exception as e:
            print(f"⚠️  Error searching database: {str(e)}")
        
        # Fall back to API search if database fails
        try:
            print(f"🔍 Searching API for {team_name} in league {league_id}...")
            results = self.soccerdata_client.search_team_by_name(team_name, league_id)
            
            if results and len(results) > 0:
                correct_id = results[0]['id']
                print(f"✅ Found via API: {results[0]['name']} (ID: {correct_id})")
                return correct_id
            else:
                print(f"❌ Could not find team '{team_name}' in league {league_id}")
                return None
        except Exception as e:
            print(f"⚠️  Error searching API: {str(e)}")
            return None

    def fetch_full_match_context(self, home_team: Union[str, int], away_team: Union[str, int], *args, **kwargs) -> Dict[str, Any]:
        """Fetch match context using Soccerdata API for proper enrichment"""
        print(f"🔄 Fetching Data (Soccerdata API) for {home_team} vs {away_team}...")

        event_id = kwargs.get('event_id')
        league_id = kwargs.get('league_id')
        home_team_id = kwargs.get('home_team_id')
        away_team_id = kwargs.get('away_team_id')
        
        # AUTO-CORRECT TEAM IDs IF THEY DON'T MATCH
        if home_team and league_id:
            if not self._validate_team_id(home_team_id, home_team):
                print(f"⚠️  Auto-correcting home team ID...")
                correct_id = self._get_correct_team_id(home_team, league_id)
                if correct_id:
                    print(f"   Changing {home_team_id} → {correct_id}")
                    home_team_id = correct_id
        
        if away_team and league_id:
            if not self._validate_team_id(away_team_id, away_team):
                print(f"⚠️  Auto-correcting away team ID...")
                correct_id = self._get_correct_team_id(away_team, league_id)
                if correct_id:
                    print(f"   Changing {away_team_id} → {correct_id}")
                    away_team_id = correct_id
        
        quantitative_features = {}
        qualitative_context = {}
        
        try:
            # Fetch league standing
            if league_id:
                standing = self.soccerdata_client.get_standing(league_id)
                if standing and standing.get('stage'):
                    for stage in standing['stage']:
                        standings_list = stage.get('standings', [])
                        if standings_list:
                            quantitative_features['league_teams_count'] = len(standings_list)
                            quantitative_features['league_leader_points'] = standings_list[0].get('points')
                            quantitative_features['standings_summary'] = [
                                {
                                    "rank": row.get('rank'),
                                    "team": row.get('team', {}).get('name'),
                                    "points": row.get('points')
                                } for row in standings_list[:6]
                            ]
            
            # Fetch head-to-head stats
            if home_team_id and away_team_id:
                h2h = self.soccerdata_client.get_head_to_head(home_team_id, away_team_id)
                if h2h:
                    h2h_summary = self.soccerdata_client.extract_h2h_stats(home_team_id, away_team_id)
                    if h2h_summary:
                        quantitative_features['h2h_overall_games'] = h2h_summary['overall_games']
                        quantitative_features['h2h_team1_wins'] = h2h_summary['team1_wins']
                        quantitative_features['h2h_team2_wins'] = h2h_summary['team2_wins']
                        quantitative_features['h2h_draws'] = h2h_summary['draws']
                        quantitative_features['h2h_team1_win_pct'] = h2h_summary['team1_win_percentage']
                        quantitative_features['h2h_team1_home_wins'] = h2h_summary['team1_home_wins']
            
            # Fetch team transfers
            if home_team_id:
                home_transfers = self.soccerdata_client.get_transfers(home_team_id)
                if home_transfers and home_transfers.get('transfers'):
                    transfers_in = home_transfers['transfers'].get('transfers_in', [])
                    transfers_out = home_transfers['transfers'].get('transfers_out', [])
                    quantitative_features['home_recent_signings'] = len(transfers_in[:5])
                    quantitative_features['home_recent_departures'] = len(transfers_out[:5])
            
            if away_team_id:
                away_transfers = self.soccerdata_client.get_transfers(away_team_id)
                if away_transfers and away_transfers.get('transfers'):
                    transfers_in = away_transfers['transfers'].get('transfers_in', [])
                    transfers_out = away_transfers['transfers'].get('transfers_out', [])
                    quantitative_features['away_recent_signings'] = len(transfers_in[:5])
                    quantitative_features['away_recent_departures'] = len(transfers_out[:5])
            
            # Fetch stadiums for qualitative context
            if home_team_id:
                home_stadium = self.soccerdata_client.get_stadium(team_id=home_team_id)
                if home_stadium:
                    qualitative_context['home_venue'] = home_stadium.get('name', 'Unknown')
                    qualitative_context['home_capacity'] = home_stadium.get('capacity')
            
            if away_team_id:
                away_stadium = self.soccerdata_client.get_stadium(team_id=away_team_id)
                if away_stadium:
                    qualitative_context['away_venue'] = away_stadium.get('name', 'Unknown')
                    qualitative_context['away_capacity'] = away_stadium.get('capacity')
            
            # Fetch match preview for weather and AI insights
            if event_id:
                preview = self.soccerdata_client.get_match_preview(event_id)
                if preview and preview.get('match_data'):
                    match_data = preview['match_data']
                    qualitative_context['weather'] = match_data.get('weather')
                    qualitative_context['excitement_rating'] = match_data.get('excitement_rating')
                    qualitative_context['ai_prediction'] = match_data.get('prediction', {}).get('choice')
        
        except Exception as e:
            print(f"❌ Error fetching from Soccerdata API: {str(e)}")
        
        # Set sensible defaults if data is empty
        if not quantitative_features:
            quantitative_features = {
                "h2h_summary": "No H2H data found.",
                "standings": [],
                "home_form": "Form Data Unavailable",
            }
        
        if not qualitative_context:
            qualitative_context = {
                "news_headlines": "Live news requires paid tier",
                "venue": "Venue info available in fixture details",
                "referee": "Referee info available in fixture details"
            }
        
        return {
            "match_id": str(event_id) if event_id else "Unknown",
            "home_team": home_team,
            "away_team": away_team,
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "league_id": league_id,
            "quantitative_features": quantitative_features,
            "qualitative_context": qualitative_context
        }

# --- INSTANTIATE ---
real_data_loader = SoccerDataLoader()