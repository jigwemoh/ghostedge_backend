import os
import requests
import logging
from typing import Dict, Any, List, Optional, Union

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
                # print(f"⚠️ API Error {endpoint}: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return {}

    def fetch_full_match_context(self, home_team: Union[str, int], away_team: Union[str, int], *args, **kwargs) -> Dict[str, Any]:
        print(f"🔄 Fetching Data (Free API) for {home_team} vs {away_team}...")

        event_id = kwargs.get('event_id')
        league_id = kwargs.get('league_id')
        
        h2h_summary = "No H2H data found."
        standings_summary = []
        form_summary = "Form Data Unavailable"

        # 1. FETCH H2H
        if event_id:
             h2h_data = self._get("football-get-head-to-head", {"eventid": event_id})
             if h2h_data.get("response"):
                 matches = h2h_data["response"]
                 # Handle dictionary vs list response structure
                 if isinstance(matches, dict) and "h2h" in matches:
                     matches = matches["h2h"]
                 
                 if isinstance(matches, list) and matches:
                     count = len(matches)
                     last_match = matches[0]
                     date = last_match.get("date", "Unknown") if isinstance(last_match, dict) else "Unknown"
                     h2h_summary = f"{count} recent meetings. Last: {date}"

        # 2. FETCH STANDINGS (New Feature)
        if league_id:
            # Note: 47 is Premier League in some mappings, but we use what is passed
            table_data = self._get("football-get-standings", {"leagueid": league_id})
            if table_data.get("response"):
                raw_table = table_data["response"]
                # The API structure can be complex (league -> standings -> array)
                if isinstance(raw_table, dict) and "standings" in raw_table:
                    # Extract top 6 or relevant teams for brevity
                    standings_list = raw_table["standings"][0] if raw_table["standings"] else []
                    # Filter for just our teams if possible, or take top few
                    for row in standings_list[:6]: # Top 6 context
                        standings_summary.append({
                            "rank": row.get("rank"),
                            "team": row.get("team", {}).get("name"),
                            "points": row.get("points")
                        })

        return {
            "match_id": str(event_id) if event_id else "Unknown",
            "quantitative_features": {
                "h2h_summary": h2h_summary,
                "standings": standings_summary, 
                "home_form": form_summary,
                "tactical_setup": {"home_formation": "Unknown", "away_formation": "Unknown"},
            },
            "qualitative_context": {
                "news_headlines": "Live news requires paid tier",
                "venue": "Venue info available in fixture details",
                "referee": "Referee info available in fixture details"
            }
        }

# --- INSTANTIATE ---
real_data_loader = SoccerDataLoader()