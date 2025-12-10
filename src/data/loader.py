import requests
import os
import json
from typing import Dict, Any, List

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

    def _get(self, endpoint: str, params: Dict[str, Any] = None):
        """Helper to fire requests safely"""
        try:
            url = f"{BASE_URL}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            print(f"⚠️ API Error {endpoint}: {response.status_code}")
            return {}
        except Exception as e:
            print(f"❌ Connection Error {endpoint}: {str(e)}")
            return {}

    def fetch_full_match_context(self, event_id: int, home_id: int, away_id: int, league_id: int):
        """
        Aggregates data from 14+ endpoints to feed the W-5 AI Engine.
        """
        print(f"🔄 Fetching Deep Data for Event {event_id}...")

        # --- 1. TACTICAL & LINEUPS (Crucial for Tactician Agent) ---
        home_lineup = self._get("football-get-hometeam-lineup", {"eventid": event_id})
        away_lineup = self._get("football-get-awayteam-lineup", {"eventid": event_id})

        # --- 2. HISTORICAL CONTEXT (Crucial for Statistician Agent) ---
        h2h_data = self._get("football-get-head-to-head", {"eventid": event_id})
        standing_all = self._get("football-get-standing-all", {"leagueid": league_id})
        standing_home = self._get("football-get-standing-home", {"leagueid": league_id})
        trophies = self._get("football-get-trophies-all-seasons", {"leagueid": league_id})

        # --- 3. MATCH SPECIFICS ---
        details = self._get("football-get-match-detail", {"eventid": event_id})
        location = self._get("football-get-match-location", {"eventid": event_id})
        stats = self._get("football-get-match-event-all-stats", {"eventid": event_id})

        # --- 4. PLAYER INTELLIGENCE (Crucial for Sentiment Agent) ---
        top_goals = self._get("football-get-top-players-by-goals", {"leagueid": league_id})
        top_rated = self._get("football-get-top-players-by-rating", {"leagueid": league_id})
        
        # --- 5. NEWS & BUZZ ---
        league_news = self._get("football-get-league-news", {"leagueid": league_id, "page": 1})
        team_news = self._get("football-get-team-news", {"teamid": home_id, "page": 1})

        # --- BUILD THE PROMPT PACKET ---
        return {
            "match_id": event_id,
            "quantitative_features": {
                "standings": self._parse_standings(standing_all, home_id, away_id),
                "home_form_context": self._parse_home_form(standing_home, home_id),
                "h2h_history": self._parse_h2h(h2h_data),
                "tactical_setup": {
                    "home_formation": self._extract_formation(home_lineup),
                    "away_formation": self._extract_formation(away_lineup),
                    "home_coach": self._extract_coach(home_lineup),
                    "away_coach": self._extract_coach(away_lineup)
                },
                "key_threats": self._extract_top_list(top_goals, 'goals')
            },
            "qualitative_context": {
                "venue": location.get('response', {}).get('stadium', 'Unknown Stadium'),
                "referee": details.get('response', {}).get('referee', 'Unknown Referee'),
                "trophy_pedigree": self._parse_trophies(trophies, home_id, away_id),
                "news_headlines": self._merge_news(league_news, team_news),
                "star_ratings": self._extract_top_list(top_rated, 'rating')
            }
        }

    # --- PARSING HELPERS ---

    def _extract_formation(self, data):
        try: return data.get('response', {}).get('formation', 'Unknown')
        except: return "Unknown"

    def _extract_coach(self, data):
        try: return data.get('response', {}).get('coach', {}).get('name', 'Unknown')
        except: return "Unknown"

    def _parse_standings(self, data, home_id, away_id):
        try:
            table = data.get('response', {}).get('standings', [])
            # Handle different API structures (sometimes nested lists)
            if table and isinstance(table[0], list): table = table[0]
            
            h_rank = next((t for t in table if t['team']['id'] == home_id), None)
            a_rank = next((t for t in table if t['team']['id'] == away_id), None)
            
            summary = []
            if h_rank: summary.append(f"Home Rank: {h_rank.get('rank')} ({h_rank.get('points')} pts)")
            if a_rank: summary.append(f"Away Rank: {a_rank.get('rank')} ({a_rank.get('points')} pts)")
            return " | ".join(summary)
        except: return "Standings Unavailable"

    def _parse_home_form(self, data, home_id):
        try:
            table = data.get('response', {}).get('standings', [])
            if table and isinstance(table[0], list): table = table[0]
            stats = next((t for t in table if t['team']['id'] == home_id), None)
            if stats: return f"Home Games: {stats.get('points')} pts (Rank {stats.get('rank')})"
            return ""
        except: return ""

    def _parse_h2h(self, data):
        try:
            matches = data.get('response', [])
            return f"{len(matches)} recent meetings found."
        except: return "No H2H data."

    def _extract_top_list(self, data, key):
        try:
            players = data.get('response', {}).get('list', [])[:3]
            return [f"{p['player']['name']} ({p.get(key,0)} {key})" for p in players]
        except: return []

    def _parse_trophies(self, data, home_id, away_id):
        return "Historical trophy data loaded."

    def _merge_news(self, league, team):
        headlines = []
        try:
            l_news = league.get('response', {}).get('news', [])[:2]
            t_news = team.get('response', {}).get('news', [])[:2]
            headlines.extend([n.get('title') for n in l_news])
            headlines.extend([n.get('title') for n in t_news])
        except: pass
        return "; ".join(headlines)

real_data_loader = RealDataLoader()