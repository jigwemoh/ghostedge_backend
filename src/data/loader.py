import os
import json
import pandas as pd
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

# --- CONFIGURATION ---
DATA_DIR = Path(os.getcwd()) / "soccer_data_cache"

try:
    import soccerdata as sd
    SOCCERDATA_AVAILABLE = True
except ImportError:
    SOCCERDATA_AVAILABLE = False

class SoccerDataLoader:
    def __init__(self, league_code: str = "ENG-Premier League", season: str = "2324"):
        # Switched to '2324' (Last full season) to ensure data stability
        self.init_error = None
        
        if not SOCCERDATA_AVAILABLE:
            self.init_error = "Library 'soccerdata' not found."
            print(f"❌ WARNING: {self.init_error}")
            self.scraper = None
            return

        self.league_code = league_code
        self.season = season
        self.scraper = None
        
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"⚠️ Warning: Could not create cache directory: {e}")
        
        print(f"📚 Initializing FBref Scraper for {league_code} ({season})...")
        try:
            self.scraper = sd.FBref(leagues=league_code, seasons=season, data_dir=DATA_DIR)
        except Exception as e:
            self.init_error = str(e)
            print(f"⚠️ Failed to initialize soccerdata scraper: {e}")

    def fetch_full_match_context(self, home_team: Union[str, int] = None, away_team: Union[str, int] = None, *args, **kwargs) -> Dict[str, Any]:
        
        # --- LEGACY ADAPTER ---
        if home_team is None or isinstance(home_team, int):
            print(f"⚠️ API MISMATCH: Defaulting to Liverpool vs Chelsea.")
            home_team = "Liverpool"
            away_team = "Chelsea"

        if not self.scraper:
            # This formatted error PROVES the new code is running
            error_msg = self.init_error if self.init_error else "Unknown initialization error"
            return {"error": f"Scraper initialization failed: {error_msg}"}

        print(f"🔄 Fetching Deep Data for {home_team} vs {away_team}...")

        # 1. FETCH STANDINGS (With Fallback Strategy)
        standings_data = []
        try:
            # Strategy A: Standard method
            if hasattr(self.scraper, 'read_standings'):
                standings_df = self.scraper.read_standings()
                standings_data = standings_df.reset_index().to_dict(orient='records')
            # Strategy B: Fallback to team stats (often contains Rank 'Rk')
            else:
                print("⚠️ 'read_standings' missing. Attempting fallback via 'read_team_season_stats'...")
                stats_df = self.scraper.read_team_season_stats(stat_type="standard")
                if not stats_df.empty and 'Rk' in stats_df.columns:
                    # Simplify the data for the AI
                    simple_df = stats_df[['Rk', 'MP', 'W', 'D', 'L', 'Pts']].copy()
                    standings_data = simple_df.reset_index().to_dict(orient='records')
        except Exception as e:
            print(f"⚠️ Standings Error: {e}")

        # 2. FETCH H2H
        h2h_summary = "No H2H data."
        try:
            schedule = self.scraper.read_schedule()
            h2h_matches = schedule[
                ((schedule['home_team'] == home_team) & (schedule['away_team'] == away_team)) |
                ((schedule['home_team'] == away_team) & (schedule['away_team'] == home_team))
            ]
            if not h2h_matches.empty:
                count = len(h2h_matches)
                last_date = h2h_matches.iloc[-1]['date']
                h2h_summary = f"{count} meetings this season. Last meeting: {last_date}"
            else:
                h2h_summary = "No previous meetings found in this dataset."
        except Exception as e:
            h2h_summary = "No H2H found (check team names)."

        # 3. FORM ANALYSIS
        form_summary = "Data Unavailable"
        try:
            match_stats = self.scraper.read_team_match_stats(stat_type="shooting", team=home_team)
            if not match_stats.empty:
                avg_shots = match_stats['shooting']['Sh'].mean()
                avg_goals = match_stats['shooting']['Gls'].mean()
                form_summary = (f"{home_team} Form: Avg {avg_shots:.1f} shots/game, "
                                f"{avg_goals:.1f} goals/game.")
        except Exception as e:
            pass

        return {
            "match_id": "Generated-ID",
            "quantitative_features": {
                "h2h_summary": h2h_summary,
                "standings": standings_data,
                "home_form": form_summary,
                "tactical_setup": {"home_formation": "Unknown", "away_formation": "Unknown"},
            },
            "qualitative_context": {
                "news_headlines": "News unavailable (Stats-only source)",
                "venue": "Venue info in schedule",
                "referee": "Referee info in schedule"
            }
        }

# --- INSTANTIATE ---
real_data_loader = SoccerDataLoader()