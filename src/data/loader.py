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
        Safely fetches data. Ensures return value is ALWAYS a Dict, never a string or list.
        """
        try:
            url = f"{BASE_URL}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except:
                    return {"response": [], "error": "Invalid JSON"}

                # SAFETY LAYER 1: Handle Top-Level Types
                if isinstance(data, str):
                    return {"response": [], "message": data}
                if isinstance(data, list):
                    return {"response": data}
                if data is None:
                    return {"response": []}
                    
                return data
                
            print(f"⚠️ API Error {endpoint}: {response.status_code}")
            return {"response": []}
        except Exception as e:
            print(f"❌ Connection Error {endpoint}: {str(e)}")
            return {"response": []}

    def _deep_safe_get(self, data: Any, *keys, default="Unknown"):
        """
        CRITICAL FIX: Recursively digs through JSON safely.
        Checks type at EVERY step to prevent 'str object has no attribute get'.
        """
        current = data
        for key in keys:
            # If we hit a dead end (None), return default
            if current is None:
                return default

            # If we are trying to read a Dict key
            if isinstance(key, str):
                if isinstance(current, dict):
                    current = current.get(key)
                else:
                    # We tried to .get() on a string/list -> STOP immediately
                    return default

            # If we are trying to read a List index
            elif isinstance(key, int):
                if isinstance(current, list):
                    if len(current) > key:
                        current = current[key]
                    else:
                        return default
                else:
                    # We tried to index a dict/string -> STOP immediately
                    return default
        
        # Final result check
        if current is None:
            return default
        # Ensure we don't return complex objects to the frontend text fields
        if isinstance(current, (dict, list)):
            return default
            
        return str(current)

    def fetch_full_match_context(self, event_id: int, home_id: int, away_id: int, league_id: int):
        print(f"🔄 Fetching Deep Data for Event {event_id}...")

        # 1. Fetch Raw Data
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

        # 2. Extract Data using Deep Safe Get
        return {
            "match_id": event_id,
            "quantitative_features": {
                "standings": self._parse_standings(raw_standings, home_id, away_id),
                "home_form": self._parse_form(raw_home_standings, home_id),
                "h2h_summary": self._parse_h2h_len(raw_h2h),
                "tactical_setup": {
                    # We dig deep: response -> [0] -> formation
                    "home_formation": self._deep_safe_get(raw_home_lineup, 'response', 0, 'formation', default="Unknown"),
                    "away_formation": self._deep_safe_get(raw_away_lineup, 'response', 0, 'formation', default="Unknown"),
                    # We dig deep: response -> [0] -> coach -> name
                    "home_coach": self._deep_safe_get(raw_home_lineup, 'response', 0, 'coach', 'name', default="Unknown"),
                    "away_coach": self._deep_safe_get(raw_away_lineup, 'response', 0, 'coach', 'name', default="Unknown")
                },
                # Dig: response -> list -> [0] -> player -> name
                "top_scorer": self._deep_safe_get(raw_top_scorers, 'response', 'list', 0, 'player', 'name', default="Unknown")
            },
            "qualitative_context": {
                "venue": self._deep_safe_get(raw_location, 'response', 0, 'stadium', default="Unknown Stadium"),
                "referee": self._deep_safe_get(raw_details, 'response', 'referee', default="Unknown Referee"),
                "news_headlines": self._merge_news(raw_league_news, raw_team_news)
            }
        }

    # --- ISOLATED PARSING HELPERS ---

    def _parse_h2h_len(self, data):
        # Manual check because we need the LENGTH of the list
        try:
            resp = data.get('response')
            if isinstance(resp, list):
                return f"{len(resp)} recent meetings found."
            return "No H2H data."
        except: return "No H2H data."

    def _parse_standings(self, data, home_id, away_id):
        try:
            # Standings path: response[0]['league']['standings'][0] -> List of teams
            resp = data.get('response')
            if not isinstance(resp, list) or len(resp) == 0: return "N/A"
            
            league = resp[0].get('league')
            if not isinstance(league, dict): return "N/A"
            
            standings = league.get('standings')
            if not isinstance(standings, list) or len(standings) == 0: return "N/A"
            
            teams_list = standings[0]
            if not isinstance(teams_list, list): return "N/A"

            h_rank, a_rank = "?", "?"
            for t in teams_list:
                if not isinstance(t, dict): continue
                team_info = t.get('team', {})
                if not isinstance(team_info, dict): continue
                
                tid = team_info.get('id')
                if tid == home_id: h_rank = t.get('rank', '?')
                if tid == away_id: a_rank = t.get('rank', '?')

            return f"Home Rank: {h_rank} | Away Rank: {a_rank}"
        except: return "Standings Unavailable"

    def _parse_form(self, data, home_id):
        try:
            resp = data.get('response')
            if not isinstance(resp, list) or len(resp) == 0: return ""
            
            league = resp[0].get('league', {})
            if not isinstance(league, dict): return ""

            standings = league.get('standings', [])
            if not standings or not isinstance(standings, list): return ""
            
            teams_list = standings[0]
            for t in teams_list:
                if isinstance(t, dict) and t.get('team', {}).get('id') == home_id:
                    return f"{t.get('points', 0)} pts in home games"
            return ""
        except: return ""

    def _merge_news(self, league, team):
        headlines = []
        try:
            # Helper to extract news from API response
            def extract(d):
                r = d.get('response')
                if isinstance(r, list) and len(r) > 0:
                    news = r[0].get('news')
                    if isinstance(news, list):
                        return news
                return []

            l_news = extract(league)
            t_news = extract(team)
            
            # Combine titles
            for n in l_news[:2]:
                if isinstance(n, dict): headlines.append(n.get('title', ''))
            for n in t_news[:2]:
                if isinstance(n, dict): headlines.append(n.get('title', ''))
                
            # Clean empty strings
            headlines = [h for h in headlines if h]
            return "; ".join(headlines) if headlines else "No major news."
        except: return "News Unavailable"

real_data_loader = RealDataLoader()