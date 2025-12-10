import requests
import os
import json
from typing import Dict, Any, List, Union

# --- CONFIGURATION ---
API_KEY = os.getenv("RAPIDAPI_KEY", "60edfa019emshc63513f3ead9a39p154a49jsn49afa8723b29")
API_HOST = "free-api-live-football-data.p.rapidapi.com"
BASE_URL = "https://free-api-live-football-data.p.rapidapi.com"

class RealDataLoader:
    def __init__(self):
        self.headers = {
            "x-rapidapi-host": API_HOST,
            "x-rapidapi-key": API_KEY
        }

    def _get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict:
        """
        Safely fetches data. Returns a Dict, NEVER a string or list.
        """
        try:
            url = f"{BASE_URL}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except:
                    return {"error": "Invalid JSON"}

                # If API returns a list [ ... ], wrap it
                if isinstance(data, list):
                    return {"response": data}
                
                # If API returns a string (e.g. "No matches"), wrap it
                if isinstance(data, str):
                    return {"response": [], "message": data}
                
                # If null, return empty
                if data is None:
                    return {}
                    
                return data
                
            print(f"⚠️ API Error {endpoint}: {response.status_code}")
            return {}
        except Exception as e:
            print(f"❌ Connection Error {endpoint}: {str(e)}")
            return {}

    def fetch_full_match_context(self, event_id: int, home_id: int, away_id: int, league_id: int):
        print(f"🔄 Fetching Deep Data for Event {event_id}...")

        # 1. Fetch Raw Data
        # We fetch everything first so we have the raw dictionaries
        raw_home_lineup = self._get("football-get-hometeam-lineup", {"eventid": event_id})
        raw_away_lineup = self._get("football-get-awayteam-lineup", {"eventid": event_id})
        raw_h2h = self._get("football-get-head-to-head", {"eventid": event_id})
        raw_standings = self._get("football-get-standing-all", {"leagueid": league_id})
        raw_home_standings = self._get("football-get-standing-home", {"leagueid": league_id})
        raw_details = self._get("football-get-match-detail", {"eventid": event_id})
        raw_location = self._get("football-get-match-location", {"eventid": event_id})
        raw_top_scorers = self._get("football-get-top-players-by-goals", {"leagueid": league_id})
        raw_league_news = self._get("football-get-league-news", {"leagueid": league_id, "page": 1})
        raw_team_news = self._get("football-get-team-news", {"teamid": home_id, "page": 1})

        # 2. Extract Data Safely (The "Nuclear" Try-Except Blocks)
        # Each function below handles its own errors so the main pipeline never stops.
        
        return {
            "match_id": event_id,
            "quantitative_features": {
                "standings": self._safe_parse_standings(raw_standings, home_id, away_id),
                "home_form": self._safe_parse_form(raw_home_standings, home_id),
                "h2h_summary": self._safe_parse_h2h(raw_h2h),
                "tactical_setup": {
                    "home_formation": self._safe_extract_formation(raw_home_lineup),
                    "away_formation": self._safe_extract_formation(raw_away_lineup),
                    "home_coach": self._safe_extract_coach(raw_home_lineup),
                    "away_coach": self._safe_extract_coach(raw_away_lineup)
                },
                "top_scorer": self._safe_extract_top_scorer(raw_top_scorers)
            },
            "qualitative_context": {
                "venue": self._safe_extract_venue(raw_location),
                "referee": self._safe_extract_referee(raw_details),
                "news_headlines": self._safe_merge_news(raw_league_news, raw_team_news)
            }
        }

    # --- ISOLATED PARSING FUNCTIONS ---
    # Even if one of these fails, it returns "Unknown" instead of crashing the app.

    def _safe_extract_formation(self, data):
        try:
            # Path: response[0] -> formation
            resp = data.get('response', [])
            if isinstance(resp, list) and len(resp) > 0:
                return str(resp[0].get('formation', 'Unknown'))
            if isinstance(resp, dict):
                return str(resp.get('formation', 'Unknown'))
            return "Unknown"
        except: return "Unknown"

    def _safe_extract_coach(self, data):
        try:
            # Path: response[0] -> coach -> name
            resp = data.get('response', [])
            if isinstance(resp, list) and len(resp) > 0:
                return str(resp[0].get('coach', {}).get('name', 'Unknown'))
            return "Unknown"
        except: return "Unknown"

    def _safe_extract_venue(self, data):
        try:
            # Path: response[0] -> stadium
            resp = data.get('response', [])
            if isinstance(resp, list) and len(resp) > 0:
                return str(resp[0].get('stadium', 'Unknown Stadium'))
            return "Unknown Stadium"
        except: return "Unknown Stadium"

    def _safe_extract_referee(self, data):
        try:
            # Path: response -> referee
            resp = data.get('response', {})
            if isinstance(resp, dict):
                return str(resp.get('referee', 'Unknown Referee'))
            return "Unknown Referee"
        except: return "Unknown Referee"

    def _safe_parse_standings(self, data, home_id, away_id):
        try:
            # Complex nesting: response[0]['league']['standings'][0] -> list of teams
            resp = data.get('response')
            if not resp or not isinstance(resp, list): return "Standings Unavailable"
            
            league = resp[0].get('league', {})
            standings = league.get('standings', [])
            
            if not standings or not isinstance(standings, list): return "Standings Unavailable"
            
            teams_list = standings[0] # The actual list of teams
            
            h_rank, a_rank = "?", "?"
            
            for t in teams_list:
                if isinstance(t, dict) and t.get('team', {}).get('id') == home_id:
                    h_rank = t.get('rank', '?')
                if isinstance(t, dict) and t.get('team', {}).get('id') == away_id:
                    a_rank = t.get('rank', '?')
            
            return f"Home Rank: {h_rank} | Away Rank: {a_rank}"
        except: return "Standings Unavailable"

    def _safe_parse_form(self, data, home_id):
        try:
            # Similar to standings but for form
            resp = data.get('response')
            if not resp or not isinstance(resp, list): return ""
            
            league = resp[0].get('league', {})
            standings = league.get('standings', [])
            if not standings: return ""
            teams_list = standings[0]

            for t in teams_list:
                if isinstance(t, dict) and t.get('team', {}).get('id') == home_id:
                    return f"{t.get('points', 0)} pts in home games"
            return ""
        except: return ""

    def _safe_parse_h2h(self, data):
        try:
            resp = data.get('response')
            if isinstance(resp, list):
                return f"{len(resp)} recent meetings found."
            return "No H2H data."
        except: return "No H2H data."

    def _safe_extract_top_scorer(self, data):
        try:
            resp = data.get('response')
            if isinstance(resp, list) and len(resp) > 0:
                 # API structure: response[0]['list'][0]['player']['name'] OR response['list']...
                 # We try generic access
                 item = resp[0]
                 if 'list' in item:
                     players = item['list']
                     if players and len(players) > 0:
                         return players[0].get('player', {}).get('name', 'Unknown')
            return "Unknown"
        except: return "Unknown"

    def _safe_merge_news(self, league, team):
        try:
            headlines = []
            
            # League News
            l_resp = league.get('response')
            if isinstance(l_resp, list) and len(l_resp) > 0:
                 l_news = l_resp[0].get('news', [])
                 if isinstance(l_news, list):
                     headlines.extend([n.get('title') for n in l_news[:2] if isinstance(n, dict)])

            # Team News
            t_resp = team.get('response')
            if isinstance(t_resp, list) and len(t_resp) > 0:
                 t_news = t_resp[0].get('news', [])
                 if isinstance(t_news, list):
                     headlines.extend([n.get('title') for n in t_news[:2] if isinstance(n, dict)])

            return "; ".join(headlines) if headlines else "No major news."
        except: return "News Unavailable"

real_data_loader = RealDataLoader()