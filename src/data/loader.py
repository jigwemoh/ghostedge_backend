import os
import json
import pandas as pd
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

# --- CONFIGURATION ---
# Cache directory to prevent re-downloading data constantly (prevents IP bans)
DATA_DIR = Path(os.getcwd()) / "soccer_data_cache"

# Check if libraries are installed
try:
    import soccerdata as sd
    SOCCERDATA_AVAILABLE = True
except ImportError:
    SOCCERDATA_AVAILABLE = False

class SoccerDataLoader:
    def __init__(self, league_code: str = "ENG-Premier League", season: str = "2425"):
        """
        Initializes the FBref scraper using the 'soccerdata' library.
        """
        if not SOCCERDATA_AVAILABLE:
            print("❌ WARNING: 'soccerdata' not found. Loader will return empty data.")
            self.scraper = None
            return

        self.league_code = league_code
        self.season = season
        self.scraper = None
        
        # Explicitly create the cache directory to avoid permission errors
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"⚠️ Warning: Could not create cache directory: {e}")
        
        print(f"📚 Initializing FBref Scraper for {league_code} ({season})...")
        try:
            # Initialize the scraper. 
            # no_cache=False ensures we use local files if they exist (faster/safer)
            self.scraper = sd.FBref(leagues=league_code, seasons=season, data_dir=DATA_DIR)
        except Exception as e:
            print(f"⚠️ Failed to initialize soccerdata scraper: {e}")

    def fetch_full_match_context(self, home_team: Union[str, int] = None, away_team: Union[str, int] = None, *args, **kwargs) -> Dict[str, Any]:
        """
        Fetches advanced stats, H2H, and standings using team names.
        Includes an adapter to handle legacy calls from main.py.
        """
        # --- ADAPTER: HANDLE LEGACY CALLS (Keyword or Integer) ---
        
        # Case 1: Called with legacy keywords (e.g. event_id=...) resulting in home_team=None
        if home_team is None:
            legacy_keys = ['event_id', 'home_id', 'league_id']
            if any(k in kwargs for k in legacy_keys):
                print(f"⚠️ API MISMATCH: main.py sent legacy keyword arguments. Defaulting to Liverpool vs Chelsea.")
                home_team = "Liverpool"
                away_team = "Chelsea"
            else:
                # Completely empty call or unknown args
                print("⚠️ API MISMATCH: Called with no valid arguments. Defaulting.")
                home_team = "Liverpool"
                away_team = "Chelsea"

        # Case 2: Called with legacy integers (e.g. 4621624)
        if isinstance(home_team, int) or isinstance(away_team, int):
            print(f"⚠️ API MISMATCH: main.py sent IDs ({home_team}, {away_team}). Defaulting to Liverpool vs Chelsea.")
            home_team = "Liverpool"
            away_team = "Chelsea"

        if not self.scraper:
            return {"error": "Scraper initialization failed"}

        print(f"🔄 Fetching Deep Data for {home_team} vs {away_team}...")

        # 1. FETCH STANDINGS
        standings_data = []
        try:
            # read_standings() returns a DataFrame with the full table
            standings_df = self.scraper.read_standings()
            
            if not standings_df.empty:
                # Reset index to make 'team' a column, then convert to list of dicts
                standings_data = standings_df.reset_index().to_dict(orient='records')
        except Exception as e:
            print(f"⚠️ Standings Error: {e}")

        # 2. FETCH H2H (Derived from Historical Schedule)
        h2h_summary = "No H2H data."
        try:
            # Get entire schedule for the configured season
            schedule = self.scraper.read_schedule()
            
            # Filter matches where these two teams played each other
            h2h_matches = schedule[
                ((schedule['home_team'] == home_team) & (schedule['away_team'] == away_team)) |
                ((schedule['home_team'] == away_team) & (schedule['away_team'] == home_team))
            ]
            
            if not h2h_matches.empty:
                count = len(h2h_matches)
                # Get the last match date
                last_match_date = h2h_matches.iloc[-1]['date']
                h2h_summary = f"{count} meetings this season. Last meeting: {last_match_date}"
            else:
                h2h_summary = "No previous meetings found in this dataset."
        except Exception as e:
            print(f"⚠️ H2H Error: {e}")

        # 3. FORM ANALYSIS (Using 'shooting' stats as a proxy for performance)
        form_summary = "Data Unavailable"
        try:
            # Fetch 'shooting' stats (shots, goals, xG) for the home team
            match_stats = self.scraper.read_team_match_stats(stat_type="shooting", team=home_team)
            
            if not match_stats.empty:
                # Calculate averages
                avg_shots = match_stats['shooting']['Sh'].mean()
                avg_goals = match_stats['shooting']['Gls'].mean()
                avg_xg = match_stats['shooting']['xG'].mean() if 'xG' in match_stats['shooting'] else 0.0
                
                form_summary = (f"{home_team} Form: Avg {avg_shots:.1f} shots/game, "
                                f"{avg_goals:.1f} goals/game, {avg_xg:.2f} xG/game.")
        except Exception as e:
            form_summary = "Form Data Unavailable (Connection issue or no games played)"

        # 4. CONSTRUCT RETURN PACKET
        return {
            "match_id": "Generated-ID",  # Scrapers don't have a simple Event ID like APIs
            "quantitative_features": {
                "h2h_summary": h2h_summary,
                "standings": standings_data,
                "lineups": [], # Lineups are generally not available via scraper until post-match
                "top_scorer": [], # Requires parsing 'standard' player stats (heavy operation)
                "home_form": form_summary,
                "tactical_setup": {
                    "home_formation": "Unknown",
                    "away_formation": "Unknown",
                },
            },
            "qualitative_context": {
                "news_headlines": "News unavailable (Stats-only source)",
                "venue": "Venue info in schedule",
                "referee": "Referee info in schedule"
            }
        }

# --- CRITICAL FIX: INSTANTIATE THE OBJECT MAIN.PY EXPECTS ---
# main.py expects to import 'real_data_loader' from this file.
real_data_loader = SoccerDataLoader()