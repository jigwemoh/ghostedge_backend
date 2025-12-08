import requests
import os
import json
from typing import Dict, Any

# --- CONFIGURATION ---
# We use the key you provided. In production, move this to .env
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
        Aggregates data from 8+ endpoints to feed the W-5 AI Engine.
        """
        print(f"🔄 Fetching Deep Data for Event {event_id}...")

        # 1. GET TACTICAL DATA (Formations & Lineups)
        # This tells the AI who is actually playing
        home_lineup = self._get("football-get-hometeam-lineup", {"eventid": event_id})
        away_lineup = self._get("football-get-awayteam-lineup", {"eventid": event_id})
        
        # 2. GET MATCH STATS (If live or finished)
        # Possession, Shots, XG (if available)
        stats = self._get("football-get-match-all-stats", {"eventid": event_id})
        
        # 3. GET NEWS & TRENDS (Qualitative Context)
        # This gives the AI the "Vibe" of the match (Injuries, Drama, Transfer rumors)
        team_news = self._get("football-get-team-news", {"teamid": home_id, "page": 1})
        league_news = self._get("football-get-league-news", {"leagueid": league_id, "page": 1})
        
        # 4. GET STAR PLAYERS (Quantitative Context)
        # Who are the dangerous players in this league?
        top_scorers = self._get("football-get-top-players-by-goals", {"leagueid": league_id})
        
        # 5. GET DETAILS (Referee, Venue)
        details = self._get("football-get-match-detail", {"eventid": event_id})
        referee = self._get("football-get-match-referee", {"eventid": event_id})

        # --- BUILD THE PROMPT PACKET ---
        # This dictionary is exactly what the W-5 Engine reads
        return {
            "match_id": event_id,
            "quantitative_features": {
                "match_stats": stats,
                "top_scorers_context": self._parse_top_players(top_scorers),
                "home_formation": self._extract_formation(home_lineup),
                "away_formation": self._extract_formation(away_lineup),
            },
            "qualitative_context": {
                "recent_news": self._summarize_news(team_news, league_news),
                "tactical_setup": f"Home Coach: {self._extract_coach(home_lineup)} vs Away Coach: {self._extract_coach(away_lineup)}",
                "referee": referee.get('referee', {}).get('name', 'Unknown')
            }
        }

    # --- HELPERS TO CLEAN THE DATA FOR AI ---
    
    def _extract_formation(self, lineup_data):
        """Extracts '4-3-3' style string from complex JSON"""
        try:
            return lineup_data.get('response', {}).get('formation', 'Unknown')
        except:
            return "Unknown"

    def _extract_coach(self, lineup_data):
        try:
            return lineup_data.get('response', {}).get('coach', {}).get('name', 'Unknown')
        except:
            return "Unknown"

    def _parse_top_players(self, data):
        """Returns top 3 scorers to help AI identify key threats"""
        try:
            players = data.get('response', {}).get('list', [])[:3]
            return [f"{p['player']['name']} ({p['goals']} goals)" for p in players]
        except:
            return []

    def _summarize_news(self, team_news, league_news):
        """Combines news headlines into a single text block for the LLM"""
        headlines = []
        try:
            # Add Team News
            t_news = team_news.get('response', {}).get('news', [])[:2]
            headlines.extend([n['title'] for n in t_news])
            # Add League News
            l_news = league_news.get('response', {}).get('news', [])[:2]
            headlines.extend([n['title'] for n in l_news])
        except:
            pass
        return ". ".join(headlines)

# Global instance
real_data_loader = RealDataLoader()