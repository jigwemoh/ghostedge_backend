import os
import requests
import logging
from typing import Dict, Any, List, Optional, Union

# --- CONFIGURATION ---
# We use the standard API-Football endpoint which is robust and supports the IDs you have
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "api-football-v1.p.rapidapi.com"
BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"

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
                return {}
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return {}

    def fetch_full_match_context(self, home_team: Union[str, int], away_team: Union[str, int], *args, **kwargs) -> Dict[str, Any]:
        print(f"🔄 Fetching Data (API-Football) for {home_team} vs {away_team}...")

        # 1. Get IDs (Prefer explicit IDs from main.py)
        event_id = kwargs.get('event_id')
        league_id = kwargs.get('league_id')
        
        h2h_summary = "No H2H data found."
        standings_summary = []
        form_summary = "Form Data Unavailable"

        # 2. FETCH MATCH DETAILS (If we have event_id)
        if event_id:
            # Get fixture details to confirm teams and get IDs if strings were passed
            fixture_data = self._get("fixtures", {"id": event_id})
            if fixture_data.get("response"):
                fixture = fixture_data["response"][0]
                h_id = fixture["teams"]["home"]["id"]
                a_id = fixture["teams"]["away"]["id"]
                
                # Now fetch H2H using these IDs
                h2h_data = self._get("fixtures/headtohead", {"h2h": f"{h_id}-{a_id}"})
                if h2h_data.get("response"):
                    matches = h2h_data["response"]
                    count = len(matches)
                    last = matches[0]
                    date = last["fixture"]["date"][:10]
                    score = f"{last['goals']['home']}-{last['goals']['away']}"
                    h2h_summary = f"{count} past meetings. Last: {date} ({score})"
                
                # Fetch Form (Last 5 games for home team)
                form_data = self._get("fixtures", {"team": h_id, "last": 5})
                if form_data.get("response"):
                    results = []
                    for m in form_data["response"]:
                        # Simple W/D/L calc
                        gh = m['goals']['home']
                        ga = m['goals']['away']
                        if m['teams']['home']['id'] == h_id:
                            res = "W" if gh > ga else ("D" if gh == ga else "L")
                        else:
                            res = "W" if ga > gh else ("D" if ga == gh else "L")
                        results.append(res)
                    form_summary = f"Last 5: {'-'.join(results)}"

        # 3. FETCH STANDINGS
        if league_id:
            table_data = self._get("standings", {"league": league_id, "season": 2024})
            if table_data.get("response"):
                league_table = table_data["response"][0]["league"]["standings"][0]
                # Extract top 6 for context
                for row in league_table[:6]:
                    standings_summary.append({
                        "rank": row["rank"],
                        "team": row["team"]["name"],
                        "points": row["points"],
                        "form": row["form"]
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