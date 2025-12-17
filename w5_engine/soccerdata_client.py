"""
Soccerdata API Client for statistical data collection
Integrates endpoints for league standings, head-to-head, transfers, and match data
"""

import requests
import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import gzip
import json

load_dotenv()

class SoccerdataClient:
    """Client for Soccerdata API v1.0.0"""
    
    BASE_URL = "https://api.soccerdataapi.com"
    
    def __init__(self):
        self.api_key = os.getenv('SOCCERDATA_API_KEY')
        if not self.api_key:
            print("⚠️ SOCCERDATA_API_KEY not found in environment")
        self.headers = {
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict]:
        """Make authenticated request to Soccerdata API"""
        if not self.api_key:
            return None
        
        if params is None:
            params = {}
        
        params['auth_token'] = self.api_key
        
        try:
            url = f"{self.BASE_URL}{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                error_data = response.json()
                print(f"API Error: {error_data.get('detail', 'Unknown error')}")
                return None
        except Exception as e:
            print(f"Request failed: {str(e)}")
            return None
    
    # ============= LEAGUE & STANDING ENDPOINTS =============
    
    def get_standing(self, league_id: int, season: Optional[str] = None) -> Optional[Dict]:
        """
        Get league standings by league_id
        Returns position, points, wins/draws/losses, goals for/against for all teams
        """
        params = {'league_id': league_id}
        if season:
            params['season'] = season
        
        data = self._make_request('/standing/', params)
        return data
    
    def get_league(self, country_id: Optional[int] = None) -> Optional[Dict]:
        """Get list of leagues, optionally filtered by country"""
        params = {}
        if country_id:
            params['country_id'] = country_id
        
        return self._make_request('/league/', params)
    
    def get_season(self, league_id: int) -> Optional[Dict]:
        """Get seasons for a specific league"""
        return self._make_request('/season/', {'league_id': league_id})
    
    def get_country(self) -> Optional[Dict]:
        """Get list of all countries"""
        return self._make_request('/country/')
    
    # ============= TEAM ENDPOINTS =============
    
    def get_team(self, team_id: int) -> Optional[Dict]:
        """Get team information by team_id"""
        return self._make_request('/team/', {'team_id': team_id})
    
    def get_transfers(self, team_id: int) -> Optional[Dict]:
        """
        Get transfers for a team
        Returns transfers_in and transfers_out with player names, dates, amounts
        """
        return self._make_request('/transfers/', {'team_id': team_id})
    
    def get_stadium(self, team_id: Optional[int] = None, stadium_id: Optional[int] = None) -> Optional[Dict]:
        """Get stadium information by team_id or stadium_id"""
        params = {}
        if team_id:
            params['team_id'] = team_id
        if stadium_id:
            params['stadium_id'] = stadium_id
        
        return self._make_request('/stadium/', params)
    
    # ============= HEAD-TO-HEAD ENDPOINTS =============
    
    def get_head_to_head(self, team_1_id: int, team_2_id: int) -> Optional[Dict]:
        """
        Get head-to-head stats between two teams
        Returns overall, home, and away statistics
        """
        params = {
            'team_1_id': team_1_id,
            'team_2_id': team_2_id
        }
        return self._make_request('/head-to-head/', params)
    
    # ============= MATCH ENDPOINTS =============
    
    def get_match(self, match_id: int) -> Optional[Dict]:
        """
        Get detailed match information
        Includes lineups, events, odds, and formation data
        """
        return self._make_request('/match/', {'match_id': match_id})
    
    def get_matches(self, league_id: Optional[int] = None, date: Optional[str] = None, 
                   season: Optional[str] = None) -> Optional[Dict]:
        """Get matches by league_id, date, or season"""
        params = {}
        if league_id:
            params['league_id'] = league_id
        if date:
            params['date'] = date
        if season:
            params['season'] = season
        
        return self._make_request('/matches/', params)
    
    def get_livescores(self) -> Optional[Dict]:
        """Get live matches for current day (UTC)"""
        return self._make_request('/livescores/')
    
    # ============= MATCH PREVIEW ENDPOINTS =============
    
    def get_match_preview(self, match_id: int) -> Optional[Dict]:
        """
        Get AI-powered match preview with weather and predictions
        """
        return self._make_request('/match-preview/', {'match_id': match_id})
    
    def get_upcoming_match_previews(self) -> Optional[Dict]:
        """Get all upcoming match previews"""
        return self._make_request('/match-previews-upcoming/')
    
    # ============= HELPER METHODS =============
    
    def extract_standing_for_team(self, league_id: int, team_name: str, season: Optional[str] = None) -> Optional[Dict]:
        """Extract standing data for a specific team"""
        standing_data = self.get_standing(league_id, season)
        if not standing_data:
            return None
        
        # Search through stages for the team
        for stage in standing_data.get('stage', []):
            for team_standing in stage.get('standings', []):
                if team_standing['team_name'].lower() == team_name.lower():
                    return {
                        'stage': stage['stage_name'],
                        'position': team_standing['position'],
                        'points': team_standing['points'],
                        'games_played': team_standing['games_played'],
                        'wins': team_standing['wins'],
                        'draws': team_standing['draws'],
                        'losses': team_standing['losses'],
                        'goals_for': team_standing['goals_for'],
                        'goals_against': team_standing['goals_against'],
                        'goal_difference': team_standing['goals_for'] - team_standing['goals_against']
                    }
        return None
    
    def extract_h2h_stats(self, team_1_id: int, team_2_id: int) -> Optional[Dict]:
        """Extract key H2H statistics"""
        h2h_data = self.get_head_to_head(team_1_id, team_2_id)
        if not h2h_data:
            return None
        
        stats = h2h_data.get('stats', {})
        overall = stats.get('overall', {})
        team1_home = stats.get('team1_at_home', {})
        team2_home = stats.get('team2_at_home', {})
        
        return {
            'team1_name': h2h_data['team1']['name'],
            'team2_name': h2h_data['team2']['name'],
            'overall_games': overall.get('overall_games_played', 0),
            'team1_wins': overall.get('overall_team1_wins', 0),
            'team2_wins': overall.get('overall_team2_wins', 0),
            'draws': overall.get('overall_draws', 0),
            'team1_home_wins': team1_home.get('team1_wins_at_home', 0),
            'team1_home_losses': team1_home.get('team1_losses_at_home', 0),
            'team2_home_wins': team2_home.get('team2_wins_at_home', 0),
            'team2_home_losses': team2_home.get('team2_losses_at_home', 0),
            'team1_win_percentage': round(
                overall.get('overall_team1_wins', 0) / max(1, overall.get('overall_games_played', 1)) * 100, 2
            ),
            'team2_win_percentage': round(
                overall.get('overall_team2_wins', 0) / max(1, overall.get('overall_games_played', 1)) * 100, 2
            )
        }
