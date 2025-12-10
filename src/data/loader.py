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
        Safely fetches data. Ensures the return value is ALWAYS a Dictionary.
        """
        try:
            url = f"{BASE_URL}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except:
                    return {"response": [], "error": "Invalid JSON"}

                # --- CRITICAL SAFETY CHECKS ---
                
                # Case 1: API returns a String (The source of your error)
                # Example: "You have exceeded the DAILY quota"
                if isinstance(data, str):
                    print(f"⚠️ API Warning ({endpoint}): returned a string -> {data}")
                    return {"response": [], "message": data}
                
                # Case 2: API returns a List (Wrap it)
                if isinstance(data, list):
                    return {"response": data}
                
                # Case 3: API returns None
                if data is None:
                    return {"response": []}
                    
                # Case 4: Standard Dict
                return data
                
            print(f"⚠️ API Error {endpoint}: {response.status_code}")
            return {"response": []}
        except Exception as e:
            print(f"❌ Connection Error {endpoint}: {str(e)}")
            return {"response": []}

    def fetch_full_match_context(self, event_id: int, home_id: int, away_id: int, league_id: int):
        print(f"🔄 Fetching Deep Data for Event {event_id}...")

        # 1. Fetch Raw Data (Now guaranteed to be Dicts)
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

        # 2. Extract Data Safely
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

    def _safe_extract_formation(self, data):
        try:
            # We use .get() safely because data is guaranteed to be a dict
            resp = data.get('response', [])
            if isinstance(resp, list) and len(resp) > 0:
                # Some endpoints return list of objects
                return str(resp[0].get('formation', 'Unknown'))
            if isinstance(resp, dict):
                return str(resp.get('formation', 'Unknown'))
            return "Unknown"
        except: return "Unknown"

    def _safe_extract_coach(self, data):
        try:
            resp = data.get('response', [])
            if isinstance(resp, list) and len(resp) > 0:
                return str(resp[0].get('coach', {}).get('name', 'Unknown'))
            return "Unknown"
        except: return "Unknown"

    def _safe_extract_venue(self, data):
        try:
            resp = data.get('response', [])
            if isinstance(resp, list) and len(resp) > 0:
                return str(resp[0].get('stadium', 'Unknown Stadium'))
            return "Unknown Stadium"
        except: return "Unknown Stadium"

    def _safe_extract_referee(self, data):
        try:
            resp = data.get('response', {})
            if isinstance(resp, dict):
                return str(resp.get('referee', 'Unknown Referee'))
            return "Unknown Referee"
        except: return "Unknown Referee"

    def _safe_parse_standings(self, data, home_id, away_id):
        try:
            resp = data.get('response')
            if not resp or not isinstance(resp, list): return "Standings Unavailable"
            
            # Navigating the nested structure
            # Likely: response[0]['league']['standings'][0]
            if len(resp) == 0: return "Standings Unavailable"
            
            item = resp[0]
            if 'league' in item: item = item['league']
            if 'standings' in item: item = item['standings']
            
            # Standings is usually a list of lists (groups)
            if isinstance(item, list) and len(item) > 0:
                teams_list = item[0]
                
                h_rank, a_rank = "?", "?"
                for t in teams_list:
                    if isinstance(t, dict) and t.get('team', {}).get('id') == home_id:
                        h_rank = t.get('rank', '?')
                    if isinstance(t, dict) and t.get('team', {}).get('id') == away_id:
                        a_rank = t.get('rank', '?')
                
                return f"Home Rank: {h_rank} | Away Rank: {a_rank}"
            return "Standings Unavailable"
        except: return "Standings Unavailable"

    def _safe_parse_form(self, data, home_id):
        try:
            resp = data.get('response')
            if not resp or not isinstance(resp, list): return ""
            # simplified check
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
                 item = resp[0]
                 # Structure check for player list
                 if 'list' in item:
                     players = item['list']
                     if isinstance(players, list) and len(players) > 0:
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