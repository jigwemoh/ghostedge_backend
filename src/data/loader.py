import os
import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from difflib import get_close_matches

# --- SILENCE NOISE ---
logging.getLogger("soccerdata").setLevel(logging.WARNING)

# --- CONFIGURATION ---
if os.environ.get("RENDER"):
    DATA_DIR = Path("/tmp/soccer_data_cache")
else:
    DATA_DIR = Path(os.getcwd()) / "soccer_data_cache"

# --- DIRECT IMPORT ---
try:
    import soccerdata as sd
    SOCCERDATA_AVAILABLE = True
except ImportError as e:
    print(f"❌ CRITICAL IMPORT ERROR: {e}")
    SOCCERDATA_AVAILABLE = False

class SoccerDataLoader:
    def __init__(self, season: str = "2425"):
        self.init_error = None
        self.season = season
        self.scraper = None
        self.standings_df = pd.DataFrame()
        self.all_teams = []
        
        # Ensure cache dir exists
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"⚠️ Warning: Could not create cache directory: {e}")
        
        if SOCCERDATA_AVAILABLE:
            # DEFINING FALLBACK STRATEGIES
            # If one configuration fails (e.g. invalid league ID), we automatically try the next.
            league_configs = [
                # 1. Broadest Coverage (May fail if Championship ID is invalid)
                ["ENG-Premier League", "ENG-Championship", "ESP-La Liga", "ITA-Serie A", "GER-Bundesliga", "FRA-Ligue 1"],
                # 2. Safe List (Big 5 Only - Known to be stable)
                ["ENG-Premier League", "ESP-La Liga", "ITA-Serie A", "GER-Bundesliga", "FRA-Ligue 1"],
                # 3. Minimal Fallback
                ["ENG-Premier League"]
            ]

            for i, leagues in enumerate(league_configs):
                try:
                    print(f"📚 Initializing FBref Scraper (Attempt {i+1}/{len(league_configs)})...")
                    self.scraper = sd.FBref(leagues=leagues, seasons=season, data_dir=DATA_DIR)
                    
                    # Pre-fetch standings to build a name index
                    print("   ...Pre-fetching team names index")
                    self.standings_df = self.scraper.read_standings()
                    self.all_teams = self._extract_all_teams(self.standings_df)
                    
                    # If we reach here, initialization succeeded
                    print("✅ Scraper Initialized Successfully.")
                    break
                except Exception as e:
                    print(f"   ⚠️ Attempt {i+1} failed: {e}")
                    # If this was the last attempt, record the error
                    if i == len(league_configs) - 1:
                        self.init_error = str(e)
                        print("❌ All initialization attempts failed.")
        else:
            self.init_error = "Library 'soccerdata' missing."

    def _extract_all_teams(self, df):
        """Extracts a flat list of all valid team names from standings."""
        if df is None or df.empty:
            return []
        # 'team' is usually in the index or a column depending on pandas version/soccerdata
        teams = []
        if 'team' in df.columns:
            teams = df['team'].unique().tolist()
        elif 'Squad' in df.columns:
            teams = df['Squad'].unique().tolist()
        else:
            # If team is in index
            teams = df.index.get_level_values('team').unique().tolist()
        return teams

    def _find_canonical_name(self, input_name: str):
        """
        Finds the exact FBref team name using fuzzy matching.
        Solves 'Man Utd' vs 'Manchester United' issues.
        """
        if not self.all_teams:
            return input_name # Fallback
            
        # 1. Exact Match (Case insensitive)
        for team in self.all_teams:
            if team.lower() == input_name.lower():
                return team
                
        # 2. Fuzzy Match
        matches = get_close_matches(input_name, self.all_teams, n=1, cutoff=0.6)
        if matches:
            print(f"   🔍 Name Map: '{input_name}' -> '{matches[0]}'")
            return matches[0]
            
        return input_name

    def fetch_full_match_context(self, home_team: Union[str, int] = None, away_team: Union[str, int] = None, *args, **kwargs) -> Dict[str, Any]:
        
        # --- LEGACY ADAPTER ---
        if home_team is None or isinstance(home_team, int):
            print(f"⚠️ API MISMATCH: Defaulting to Liverpool vs Chelsea.")
            home_team = "Liverpool"
            away_team = "Chelsea"

        if not self.scraper:
            return {"error": f"Scraper initialization failed: {self.init_error}"}

        # --- NORMALIZE NAMES ---
        # This is the secret sauce. We switch to the "Real" names before asking the scraper.
        real_home = self._find_canonical_name(str(home_team))
        real_away = self._find_canonical_name(str(away_team))

        print(f"🔄 Fetching Data for {real_home} vs {real_away}...")

        # 1. FETCH STANDINGS
        standings_data = []
        try:
            # Filter the pre-fetched standings for these specific teams
            # We look for rows where the index (or column) matches our teams
            if not self.standings_df.empty:
                # Reset index to make searching easier
                df_reset = self.standings_df.reset_index()
                # Filter for relevant rows
                mask = df_reset['team'].isin([real_home, real_away])
                relevant_df = df_reset[mask]
                standings_data = relevant_df.to_dict(orient='records')
        except Exception as e:
            print(f"⚠️ Standings Error: {e}")

        # 2. FETCH H2H
        h2h_summary = "No H2H data."
        try:
            schedule = self.scraper.read_schedule()
            # Robust filtering using the canonical names
            h2h_matches = schedule[
                ((schedule['home_team'] == real_home) & (schedule['away_team'] == real_away)) |
                ((schedule['home_team'] == real_away) & (schedule['away_team'] == real_home))
            ]
            
            if not h2h_matches.empty:
                count = len(h2h_matches)
                last_date = h2h_matches.iloc[-1]['date']
                # Get last result if available
                last_home = h2h_matches.iloc[-1]['home_team']
                last_score = f"{h2h_matches.iloc[-1]['home_score']}-{h2h_matches.iloc[-1]['away_score']}"
                h2h_summary = f"{count} meetings this season. Last: {last_date} ({last_home} {last_score})"
            else:
                h2h_summary = "No previous meetings found in this dataset."
        except Exception as e:
            print(f"⚠️ H2H Error: {e}")

        # 3. FORM ANALYSIS
        form_summary = "Data Unavailable"
        try:
            # Try detailed shooting stats first
            match_stats = self.scraper.read_team_match_stats(stat_type="shooting", team=real_home)
            if not match_stats.empty:
                avg_shots = match_stats['shooting']['Sh'].mean()
                avg_goals = match_stats['shooting']['Gls'].mean()
                form_summary = f"{real_home} Form: {avg_shots:.1f} shots/pg, {avg_goals:.1f} goals/pg."
            else:
                # Fallback to basic schedule results if shooting data is missing
                form_summary = "Detailed stats missing, check standings for form."
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