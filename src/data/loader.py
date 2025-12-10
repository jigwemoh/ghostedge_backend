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
        CRITICAL FIX: Always returns a Dictionary, even if API gives a List.
        """
        try:
            url = f"{BASE_URL}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # FIX 1: If API returns a top-level list, wrap it
                if isinstance(data, list):
                    return {"response": data}
                
                # FIX 2: If API returns empty or null, return empty dict
                if data is None:
                    return {}
                    
                return data
                
            print(f"⚠️ API Error {endpoint}: {response.status_code}")
            return {}
        except Exception as e:
            print(f"❌ Connection Error {endpoint}: {str(e)}")
            return {}

    def _safe_extract(self, data: Dict, keys: List[str], default="Unknown"):
        """
        Safely digs through nested JSON without crashing.
        Usage: _safe_extract(data, ['response', 0, 'coach', 'name'])
        """
        try:
            current = data
            for key in keys:
                if isinstance(current, dict):
                    current = current.get(key)
                elif isinstance(current, list):
                    # If looking for index (int)
                    if isinstance(key, int):
                        if len(current) > key:
                            current = current[key]
                        else:
                            return default
                    else:
                        # If list but key is string, try first item
                        if len(current) > 0:
                            current = current[0].get(key)
                        else:
                            return default
                
                if current is None:
                    return default
            return current
        except:
            return default

    def fetch_full_match_context(self, event_id: int, home_id: int, away_id: int, league_id: int):
        print(f"🔄 Fetching Deep Data for Event {event_id}...")

        # --- FETCH RAW DATA ---
        home_lineup = self._get("football-get-hometeam-lineup", {"eventid": event_id})
        away_lineup = self._get("football-get-awayteam-lineup", {"eventid": event_id})
        h2h_data = self._get("football-get-head-to-head", {"eventid": event_id})
        standing_all = self._get("football-get-standing-all", {"leagueid": league_id})
        standing_home = self._get("football-get-standing-home", {"leagueid": league_id})
        details = self._get("football-get-match-detail", {"eventid": event_id})
        location = self._get("football-get-match-location", {"eventid": event_id})
        top_goals = self._get("football-get-top-players-by-goals", {"leagueid": league_id})
        league_news = self._get("football-get-league-news", {"leagueid": league_id, "page": 1})
        team_news = self._get("football-get-team-news", {"teamid": home_id, "page": 1})

        # --- BUILD PACKET SAFEGUARDS ---
        return {
            "match_id": event_id,
            "quantitative_features": {
                "standings": self._parse_standings(standing_all, home_id, away_id),
                "home_form": self._parse_form(standing_home, home_id),
                "h2h_summary": f"{len(h2h_data.get('response', []))} recent meetings.",
                "tactical_setup": {
                    "home_formation": self._safe_extract(home_lineup, ['response', 0, 'formation']),
                    "away_formation": self._safe_extract(away_lineup, ['response', 0, 'formation']),
                    "home_coach": self._safe_extract(home_lineup, ['response', 0, 'coach', 'name']),
                    "away_coach": self._safe_extract(away_lineup, ['response', 0, 'coach', 'name'])
                },
                "top_scorer": self._safe_extract(top_goals, ['response', 'list', 0, 'player', 'name'])
            },
            "qualitative_context": {
                "venue": self._safe_extract(location, ['response', 0, 'stadium']),
                "referee": self._safe_extract(details, ['response', 'referee']),
                "news_headlines": self._merge_news(league_news, team_news)
            }
        }

    # --- PARSING HELPERS ---

    def _parse_standings(self, data, home_id, away_id):
        try:
            # Safely navigate to standings list
            # usually: response[0]['league']['standings'][0] -> list of teams
            resp = data.get('response', [])
            if not resp: return "N/A"
            
            # Navigate nested structure
            if isinstance(resp, list): resp = resp[0]
            if 'league' in resp: resp = resp['league']
            if 'standings' in resp: resp = resp['standings']
            if isinstance(resp, list) and len(resp) > 0 and isinstance(resp[0], list): resp = resp[0]

            h_rank = next((t.get('rank') for t in resp if t.get('team', {}).get('id') == home_id), "?")
            a_rank = next((t.get('rank') for t in resp if t.get('team', {}).get('id') == away_id), "?")
            return f"Home Rank: {h_rank} | Away Rank: {a_rank}"
        except:
            return "Standings Unavailable"

    def _parse_form(self, data, home_id):
        try:
            resp = data.get('response', [])
            if not resp: return "N/A"
            if isinstance(resp, list): resp = resp[0]
            if 'league' in resp: resp = resp['league']
            if 'standings' in resp: resp = resp['standings']
            if isinstance(resp, list) and len(resp) > 0 and isinstance(resp[0], list): resp = resp[0]
            
            stats = next((t for t in resp if t.get('team', {}).get('id') == home_id), None)
            if stats: return f"{stats.get('points', 0)} pts in home games"
            return ""
        except: return ""

    def _merge_news(self, league, team):
        try:
            l = self._safe_extract(league, ['response', 'news'], []) or []
            t = self._safe_extract(team, ['response', 'news'], []) or []
            # Ensure they are lists
            if not isinstance(l, list): l = []
            if not isinstance(t, list): t = []
            
            titles = [x.get('title') for x in l[:2] if isinstance(x, dict)] + \
                     [x.get('title') for x in t[:2] if isinstance(x, dict)]
            return "; ".join(titles) if titles else "No major news."
        except: return "News Unavailable"

real_data_loader = RealDataLoader()