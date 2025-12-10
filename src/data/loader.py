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

    # --- 1. THE SAFETY CORE ---
    
    def _get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict:
        """
        Fetches data and sanitizes it so it is ALWAYS a Dictionary.
        Prevents 'str has no attribute get' at the source.
        """
        try:
            url = f"{BASE_URL}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except:
                    # If API returns non-JSON text (e.g. HTML error), wrap it
                    return {"response": [], "error": "Invalid JSON from API"}

                # SAFETY CHECKS:
                # 1. If API returned a bare string (e.g. "Server Busy"), wrap it.
                if isinstance(data, str):
                    return {"response": [], "message": data}
                
                # 2. If API returned a list [ ... ], wrap it.
                if isinstance(data, list):
                    return {"response": data}
                
                # 3. If API returned None, return empty dict.
                if data is None:
                    return {}
                    
                return data
            
            # Non-200 Status
            print(f"⚠️ API Error {endpoint}: {response.status_code}")
            return {"response": []}
            
        except Exception as e:
            print(f"❌ Connection Error {endpoint}: {str(e)}")
            return {"response": []}

    def drill(self, data: Any, path: List[Any], default="Unknown"):
        """
        The 'Diamond Drill'.
        Safely navigates deep JSON structures. If ANY step fails (e.g. hitting a 
        string instead of a dict), it bails out safely instead of crashing.
        
        Usage: self.drill(data, ['response', 0, 'coach', 'name'])
        """
        try:
            current = data
            for key in path:
                # If we hit a dead end
                if current is None:
                    return default

                # If the current item is a STRING, we can't dig deeper. 
                # This is what fixes your 'str has no attribute get' error.
                if isinstance(current, str):
                    return default

                # If looking for a dictionary key
                if isinstance(key, str):
                    if isinstance(current, dict):
                        current = current.get(key)
                    else:
                        return default
                
                # If looking for a list index
                elif isinstance(key, int):
                    if isinstance(current, list):
                        if len(current) > key:
                            current = current[key]
                        else:
                            return default
                    else:
                        return default
            
            # Success! Return the value found (or default if it's None)
            return current if current is not None else default
        except:
            return default

    # --- 2. MAIN LOGIC ---

    def fetch_full_match_context(self, event_id: int, home_id: int, away_id: int, league_id: int):
        print(f"🔄 Fetching Deep Data for Event {event_id}...")

        # A. Fetch Raw Data (Guaranteed to be Dictionaries by _get)
        raw = {
            "h_lineup": self._get("football-get-hometeam-lineup", {"eventid": event_id}),
            "a_lineup": self._get("football-get-awayteam-lineup", {"eventid": event_id}),
            "h2h": self._get("football-get-head-to-head", {"eventid": event_id}),
            "st_all": self._get("football-get-standing-all", {"leagueid": league_id}),
            "st_home": self._get("football-get-standing-home", {"leagueid": league_id}),
            "detail": self._get("football-get-match-detail", {"eventid": event_id}),
            "loc": self._get("football-get-match-location", {"eventid": event_id}),
            "scorers": self._get("football-get-top-players-by-goals", {"leagueid": league_id}),
            "l_news": self._get("football-get-league-news", {"leagueid": league_id, "page": 1}),
            "t_news": self._get("football-get-team-news", {"teamid": home_id, "page": 1})
        }

        # B. Extract Safely using Drill
        # Note: We pass paths like ['response', 0, 'formation']
        
        return {
            "match_id": event_id,
            "quantitative_features": {
                "standings": self._parse_standings(raw['st_all'], home_id, away_id),
                "home_form": self._parse_form(raw['st_home'], home_id),
                "h2h_summary": self._parse_h2h(raw['h2h']),
                "tactical_setup": {
                    "home_formation": self.drill(raw['h_lineup'], ['response', 0, 'formation']),
                    "away_formation": self.drill(raw['a_lineup'], ['response', 0, 'formation']),
                    "home_coach": self.drill(raw['h_lineup'], ['response', 0, 'coach', 'name']),
                    "away_coach": self.drill(raw['a_lineup'], ['response', 0, 'coach', 'name'])
                },
                "top_scorer": self.drill(raw['scorers'], ['response', 'list', 0, 'player', 'name'])
            },
            "qualitative_context": {
                "venue": self.drill(raw['loc'], ['response', 0, 'stadium'], "Unknown Stadium"),
                "referee": self.drill(raw['detail'], ['response', 'referee'], "Unknown Referee"),
                "news_headlines": self._merge_news(raw['l_news'], raw['t_news'])
            }
        }

    # --- 3. COMPLEX PARSING ---

    def _parse_h2h(self, data):
        # We assume data is a dict because of _get
        # Path: response -> (list)
        resp = self.drill(data, ['response'], [])
        if isinstance(resp, list):
            return f"{len(resp)} recent meetings."
        return "No H2H data."

    def _parse_standings(self, data, home_id, away_id):
        # Standings structure is notoriously deep and unstable
        # Path: response[0] -> league -> standings[0] -> list of teams
        try:
            # Step 1: Get the league object safely
            league = self.drill(data, ['response', 0, 'league'])
            if league == "Unknown": return "Standings Unavailable"

            # Step 2: Get the standings list
            # Note: Sometimes standings is a list of lists (groups)
            standings_group = self.drill(league, ['standings', 0], [])
            if not isinstance(standings_group, list): return "Standings Unavailable"

            # Step 3: Search for our teams
            h_rank, a_rank = "?", "?"
            for t in standings_group:
                if not isinstance(t, dict): continue
                tid = self.drill(t, ['team', 'id'], -1)
                
                if tid == home_id:
                    h_rank = self.drill(t, ['rank'], '?')
                if tid == away_id:
                    a_rank = self.drill(t, ['rank'], '?')
            
            return f"Home Rank: {h_rank} | Away Rank: {a_rank}"
        except:
            return "Standings Unavailable"

    def _parse_form(self, data, home_id):
        # Reusing the drill logic from standings
        try:
            standings_group = self.drill(data, ['response', 0, 'league', 'standings', 0], [])
            if not isinstance(standings_group, list): return ""
            
            for t in standings_group:
                if isinstance(t, dict):
                    tid = self.drill(t, ['team', 'id'], -1)
                    if tid == home_id:
                        pts = self.drill(t, ['points'], 0)
                        return f"{pts} pts in home games"
            return ""
        except: return ""

    def _merge_news(self, league, team):
        try:
            # Drill to the news lists
            l_news = self.drill(league, ['response', 0, 'news'], [])
            t_news = self.drill(team, ['response', 0, 'news'], [])
            
            # Ensure they are lists
            if not isinstance(l_news, list): l_news = []
            if not isinstance(t_news, list): t_news = []
            
            titles = []
            # Extract titles safely
            for item in l_news[:2]:
                if isinstance(item, dict): titles.append(item.get('title', ''))
            for item in t_news[:2]:
                if isinstance(item, dict): titles.append(item.get('title', ''))
            
            # Filter empty
            valid = [t for t in titles if t]
            return "; ".join(valid) if valid else "No major news."
        except: return "News Unavailable"

real_data_loader = RealDataLoader()