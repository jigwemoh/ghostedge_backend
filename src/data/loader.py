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
        self.season = int(season[:4]) if len(season) == 4 else 2024
        
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
                print(f"⚠️ API Error {endpoint}: {response.status_code} {response.text}")
                return {}
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return {}

    def _get_team_id(self, team_name: str) -> Optional[int]:
        """Finds the API-Football Team ID from a name."""
        # Note: Endpoint might differ for this specific API, checking documentation is advised if this fails.
        # Assuming standard 'teams' endpoint exists or similar structure.
        # For free-api-live-football-data, endpoints are different. 
        # Usually it's /football-get-all-teams-by-league-id but we don't have league ID easily.
        # Fallback to search if available or keep generic.
        
        # NOTE: The previous API had a search. This one might require specific endpoints.
        # Leaving as generic fetch for now, but be aware this might need endpoint adjustment based on specific API docs.
        return None 

    def fetch_full_match_context(self, home_team: Union[str, int], away_team: Union[str, int], *args, **kwargs) -> Dict[str, Any]:
        print(f"🔄 Fetching Data (Free API) for {home_team} vs {away_team}...")

        # The Free API works differently. It often needs event IDs directly or specific endpoints.
        # If we have event_id in kwargs, use it.
        event_id = kwargs.get('event_id')
        
        h2h_summary = "H2H data unavailable in free tier without event ID."
        standings_summary = []
        form_summary = "Form Data Unavailable"

        if event_id:
             # Fetch H2H using event ID if possible
             # Endpoint: football-get-head-to-head?eventid={id}
             h2h_data = self._get("football-get-head-to-head", {"eventid": event_id})
             if h2h_data.get("response"):
                 matches = h2h_data["response"]
                 # Check if the response is a list or a dict containing list
                 if isinstance(matches, dict) and "h2h" in matches:
                     matches = matches["h2h"]
                 
                 if isinstance(matches, list) and matches:
                     count = len(matches)
                     h2h_summary = f"{count} recent meetings found."
                     # Try to get details of the last match
                     last_match = matches[0]
                     if isinstance(last_match, dict):
                         score = last_match.get("score", "N/A")
                         date = last_match.get("date", "Unknown Date")
                         h2h_summary += f" Last: {date} ({score})"

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