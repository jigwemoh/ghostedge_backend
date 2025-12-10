import requests
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Union

# --- CONFIGURATION ---
API_KEY = os.getenv("RAPIDAPI_KEY", "60edfa019emshc63513f3ead9a39p154a49jsn49afa8723b29")
API_HOST = "english-premiere-league1.p.rapidapi.com"
BASE_URL = "https://english-premiere-league1.p.rapidapi.com"

class RealDataLoader:
    def __init__(self):
        self.headers = {
            "x-rapidapi-host": API_HOST,
            "x-rapidapi-key": API_KEY
        }

    def _get(self, endpoint: str, params: Dict[str, Any] = None):
        """Helper to fire requests safely"""
        try:
            url = f"{BASE_URL}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            print(f"⚠️ API Error {endpoint}: {response.status_code}")
            return {}
        except Exception as e:
            print(f"❌ Connection Error {endpoint}: {str(e)}")
            return {}

    def _ensure_dict(self, data: Union[Dict, List]) -> Dict:
        """
        CRITICAL FIX: Converts a List to a Dict if the API returns [ {} ].
        If it's already a Dict, returns it as is.
        If empty, returns {}.
        """
        if isinstance(data, list):
            if len(data) > 0:
                return data[0] # Take the first item
            return {}
        return data

    def fetch_full_match_context(self, home_id: int, away_id: int, home_name: str, away_name: str):
        """
        Aggregates data using the English Premier League API.
        """
        print(f"🔄 Fetching EPL Data for {home_name} vs {away_name}...")
        
        current_year = datetime.now().year
        season_year = current_year if datetime.now().month > 7 else current_year - 1

        # --- 1. TEAM INTELLIGENCE ---
        # Get raw data
        home_results = self._get("team/results", {"teamId": home_id})
        away_results = self._get("team/results", {"teamId": away_id})
        
        # FIX: The scoring/info endpoints often return Lists, so we sanitize them
        home_scoring = self._ensure_dict(self._get("team/statistic/scoring", {"teamId": home_id}))
        away_scoring = self._ensure_dict(self._get("team/statistic/scoring", {"teamId": away_id}))
        home_info = self._ensure_dict(self._get("team/info", {"teamId": home_id}))
        
        # --- 2. LEAGUE CONTEXT ---
        scoreboard = self._get("scoreboard", {"year": season_year})
        all_injuries = self._get("injuries")
        news_feed = self._get("news")

        # --- BUILD THE W-5 DATA PACKET ---
        return {
            "match_id": f"{home_id}-{away_id}",
            "quantitative_features": {
                "standings_context": self._parse_standings(scoreboard, home_name, away_name),
                "home_form": self._parse_recent_results(home_results),
                "away_form": self._parse_recent_results(away_results),
                "scoring_stats": {
                    "home_attack": self._extract_scoring_stat(home_scoring),
                    "away_attack": self._extract_scoring_stat(away_scoring)
                }
            },
            "qualitative_context": {
                "injuries": self._filter_injuries(all_injuries, home_name, away_name),
                "recent_news": self._summarize_news(news_feed),
                # FIX: Now safe to use .get because we ran _ensure_dict
                "venue_info": home_info.get('venue', {}).get('name', 'Unknown Stadium')
            }
        }

    # --- PARSING HELPERS ---

    def _parse_standings(self, data, home_name, away_name):
        try:
            # Scoreboard is usually a list of team dicts
            teams = data if isinstance(data, list) else data.get('standings', [])
            
            # Helper to find rank safely
            def find_rank(name):
                for t in teams:
                    # Check nested structure often found in football APIs
                    t_name = t.get('team', {}).get('name', '')
                    if not t_name: t_name = t.get('teamName', '')
                    
                    if name.lower() in t_name.lower():
                        return t.get('rank', 'N/A')
                return "N/A"

            h_rank = find_rank(home_name)
            a_rank = find_rank(away_name)
            
            return f"Home Rank: {h_rank} | Away Rank: {a_rank}"
        except:
            return "Standings parsing failed."

    def _parse_recent_results(self, data):
        try:
            # Expecting a list of matches
            if not isinstance(data, list): return "No recent form data."
            
            matches = data[:5]
            form = []
            for m in matches:
                # Handle different API keys for scores
                h_score = m.get('homeScore', m.get('goalsHomeTeam', '?'))
                a_score = m.get('awayScore', m.get('goalsAwayTeam', '?'))
                form.append(f"{h_score}-{a_score}")
            return "Last 5 scores: " + ", ".join(form)
        except:
            return "Recent form unavailable."

    def _extract_scoring_stat(self, data):
        try:
            # Data is already ensured to be a dict
            goals = data.get('goals', data.get('total', 'N/A'))
            return f"Goals: {goals} (Season)"
        except:
            return "N/A"

    def _filter_injuries(self, injuries_data, home_name, away_name):
        relevant = []
        try:
            # Injuries usually come as a list
            if not isinstance(injuries_data, list): return "No injury data."

            for player in injuries_data:
                # Safely dig for team name
                team = player.get('team', {}).get('name', '')
                if home_name in team or away_name in team:
                    status = player.get('status', 'Injured')
                    p_name = player.get('name', 'Unknown')
                    relevant.append(f"{p_name} ({team}): {status}")
            
            if not relevant: return "No major injuries reported."
            return "; ".join(relevant[:5])
        except:
            return "Injury parsing error."

    def _summarize_news(self, news_data):
        try:
            if not isinstance(news_data, list): return "No news."
            headlines = [n.get('title') for n in news_data[:3] if n.get('title')]
            return ". ".join(headlines)
        except:
            return "No recent news."

# Global instance
real_data_loader = RealDataLoader()