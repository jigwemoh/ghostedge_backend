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
        Safely fetches data. Ensures return value is ALWAYS a Dict.
        """
        try:
            url = f"{BASE_URL}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except:
                    return {"response": [], "error": "Invalid JSON"}

                # SAFETY CHECKS:
                if isinstance(data, str):
                    return {"response": [], "message": data}
                if isinstance(data, list):
                    return {"response": data}
                if data is None:
                    return {}
                return data
            
            print(f"⚠️ API Error {endpoint}: {response.status_code}")
            return {"response": []}
        except Exception as e:
            print(f"❌ Connection Error {endpoint}: {str(e)}")
            return {"response": []}

    def fetch_full_match_context(self, event_id: int, home_id: int, away_id: int, league_id: int):
        print(f"🔄 Fetching ONLY H2H & News for Event {event_id}...")

        # 1. FETCH ONLY THE REQUESTED ENDPOINTS
        # We ignore standings, lineups, etc. to stop the crashes.
        raw_h2h = self._get("football-get-head-to-head", {"eventid": event_id})
        raw_team_news = self._get("football-get-team-news", {"teamid": home_id, "page": 1})
        # Adding away news too for balance
        raw_away_news = self._get("football-get-team-news", {"teamid": away_id, "page": 1})

        # 2. RETURN SIMPLIFIED PACKET
        # We fill missing fields with "Disabled" so the AI Agents don't crash.
        return {
            "match_id": event_id,
            "quantitative_features": {
                "h2h_summary": self._parse_h2h(raw_h2h),
                # Placeholders for removed endpoints
                "standings": "Data Feed Disabled",
                "home_form": "Data Feed Disabled",
                "tactical_setup": {
                    "home_formation": "Unknown",
                    "away_formation": "Unknown",
                    "home_coach": "Unknown",
                    "away_coach": "Unknown"
                },
                "top_scorer": "Unknown"
            },
            "qualitative_context": {
                "news_headlines": self._merge_news(raw_team_news, raw_away_news),
                # Placeholders
                "venue": "Unknown Stadium",
                "referee": "Unknown Referee"
            }
        }

    # --- PARSING HELPERS ---

    def _parse_h2h(self, data):
        try:
            # Path: response (list)
            resp = data.get('response')
            if isinstance(resp, list):
                count = len(resp)
                return f"{count} recent meetings found between these teams."
            return "No H2H data."
        except: return "No H2H data."

    def _merge_news(self, home_data, away_data):
        headlines = []
        try:
            # Helper to extract news safely
            def get_titles(d):
                titles = []
                # Check if 'response' exists and is a list
                resp = d.get('response')
                if isinstance(resp, list) and len(resp) > 0:
                    # Check if the first item has 'news' list
                    news_list = resp[0].get('news')
                    if isinstance(news_list, list):
                        for item in news_list[:2]:
                            if isinstance(item, dict):
                                t = item.get('title')
                                if t: titles.append(t)
                return titles

            headlines.extend(get_titles(home_data))
            headlines.extend(get_titles(away_data))

            return "; ".join(headlines) if headlines else "No major news found."
        except Exception as e: 
            return "News Parsing Error"

real_data_loader = RealDataLoader()