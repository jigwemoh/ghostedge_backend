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
        Safely fetches data. Always returns a Dict.
        """
        try:
            url = f"{BASE_URL}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except:
                    return {} # Handle non-JSON response

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

    def _safe_extract(self, data: Any, keys: List[Any], default="Unknown"):
        """
        Recursively digs for data.
        Prevents 'str has no attribute get' by checking types at every step.
        """
        try:
            current = data
            for key in keys:
                # If current is None, stop
                if current is None:
                    return default

                # If we need a Dict key (str)
                if isinstance(key, str):
                    if isinstance(current, dict):
                        current = current.get(key)
                    else:
                        # We expected a dict but got something else (like a str or list)
                        return default

                # If we need a List index (int)
                elif isinstance(key, int):
                    if isinstance(current, list):
                        if len(current) > key:
                            current = current[key]
                        else:
                            return default
                    else:
                        return default
                
            # Final check: If we ended up with None, return default
            return current if current is not None else default
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

        # --- BUILD PACKET ---
        return {
            "match_id": event_id,
            "quantitative_features": {
                "standings": self._parse_standings(standing_all, home_id, away_id),
                "home_form": self._parse_form(standing_home, home_id),
                "h2h_summary": self._parse_h2h_length(h2h_data),
                "tactical_setup": {
                    "home_formation": self._safe_extract(home_lineup, ['response', 'formation'], 'Unknown'),
                    "away_formation": self._safe_extract(away_lineup, ['response', 'formation'], 'Unknown'),
                    "home_coach": self._safe_extract(home_lineup, ['response', 'coach', 'name'], 'Unknown'),
                    "away_coach": self._safe_extract(away_lineup, ['response', 'coach', 'name'], 'Unknown')
                },
                "top_scorer": self._safe_extract(top_goals, ['response', 'list', 0, 'player', 'name'], 'Unknown')
            },
            "qualitative_context": {
                "venue": self._safe_extract(location, ['response', 0, 'stadium'], 'Unknown Stadium'),
                "referee": self._safe_extract(details, ['response', 'referee'], 'Unknown Referee'),
                "news_headlines": self._merge_news(league_news, team_news)
            }
        }

    # --- PARSING HELPERS ---

    def _parse_h2h_length(self, data):
        # Safely check if response is a list
        resp = data.get('response')
        if isinstance(resp, list):
            return f"{len(resp)} recent meetings found."
        return "No H2H data."

    def _parse_standings(self, data, home_id, away_id):
        try:
            # Standings are nested deep. We use safe extract to get to the team list.
            # Path: response -> [0] -> league -> standings -> [0] -> [Teams]
            
            # First, try to get the 'league' object
            league_obj = self._safe_extract(data, ['response', 0, 'league'])
            if not league_obj: return "Standings Unavailable"
            
            # Now find the standings list
            standings_list = self._safe_extract(league_obj, ['standings', 0], [])
            
            if not isinstance(standings_list, list): return "Standings Unavailable"

            # Find ranks
            h_rank = "?"
            a_rank = "?"
            
            for t in standings_list:
                if not isinstance(t, dict): continue
                tid = self._safe_extract(t, ['team', 'id'])
                if tid == home_id:
                    h_rank = t.get('rank', '?')
                if tid == away_id:
                    a_rank = t.get('rank', '?')

            return f"Home Rank: {h_rank} | Away Rank: {a_rank}"
        except:
            return "Standings Unavailable"

    def _parse_form(self, data, home_id):
        try:
            # Same logic as standings
            league_obj = self._safe_extract(data, ['response', 0, 'league'])
            if not league_obj: return "N/A"
            
            standings_list = self._safe_extract(league_obj, ['standings', 0], [])
            if not isinstance(standings_list, list): return "N/A"

            for t in standings_list:
                if not isinstance(t, dict): continue
                if self._safe_extract(t, ['team', 'id']) == home_id:
                    return f"{t.get('points', 0)} pts in home games"
            return ""
        except: return ""

    def _merge_news(self, league, team):
        try:
            l_news = self._safe_extract(league, ['response', 'news'], [])
            t_news = self._safe_extract(team, ['response', 'news'], [])
            
            # Ensure they are lists before iterating
            if not isinstance(l_news, list): l_news = []
            if not isinstance(t_news, list): t_news = []
            
            titles = []
            for item in l_news[:2]:
                if isinstance(item, dict): titles.append(item.get('title', ''))
            for item in t_news[:2]:
                if isinstance(item, dict): titles.append(item.get('title', ''))
            
            # Filter empty strings
            titles = [t for t in titles if t]
            
            return "; ".join(titles) if titles else "No major news."
        except: return "News Unavailable"

real_data_loader = RealDataLoader()