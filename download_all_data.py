import soccerdata as sd
import logging
import time
from pathlib import Path

# --- CONFIGURATION ---
# List of leagues to download
LEAGUES = [
    "ENG-Premier League",
    "ESP-La Liga",
    "ITA-Serie A",
    "GER-Bundesliga",
    "FRA-Ligue 1"
]

# Seasons to download (e.g., "1819" to "2324")
SEASONS = ["2021", "2122", "2223", "2324", "2425"]

# Cache Directory (Same as your loader.py)
DATA_DIR = Path.cwd() / "soccer_data_cache"

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("bulk_downloader")

def download_league_data(league, season):
    """
    Initializes a scraper for a specific league/season and fetches key datasets.
    This triggers the download and caching process.
    """
    logger.info(f"⬇️ Starting download for {league} ({season})...")
    
    try:
        # Initialize scraper (This creates the cache folder structure)
        # no_cache=False is default, meaning it will download if missing, or read from disk if present.
        scraper = sd.FBref(leagues=league, seasons=season, data_dir=DATA_DIR)
        
        # 1. Fetch Schedule (Match list & scores)
        logger.info(f"   📅 Fetching Schedule...")
        scraper.read_schedule()
        
        # 2. Fetch Standings (League tables)
        # Note: Some older seasons might use read_standings, newer might need read_league_table logic
        # We try standard first
        logger.info(f"   🏆 Fetching Standings...")
        try:
            if hasattr(scraper, 'read_standings'):
                scraper.read_standings()
            else:
                scraper.read_team_season_stats(stat_type="standard")
        except Exception as e:
            logger.warning(f"      ⚠️ Standings fetch issue: {e}")

        # 3. Fetch Team Match Stats (Detailed shot/possession data)
        # This is heavy! It fetches stats for every match.
        logger.info(f"   📊 Fetching Team Match Stats (Shooting)...")
        try:
            scraper.read_team_match_stats(stat_type="shooting")
        except Exception as e:
            logger.warning(f"      ⚠️ Stats fetch issue: {e}")

        logger.info(f"✅ Completed {league} ({season})")
        
    except Exception as e:
        logger.error(f"❌ Critical failure for {league} {season}: {e}")

def main():
    logger.info("🚀 STARTING BULK DATA DOWNLOAD")
    logger.info(f"📂 Cache Directory: {DATA_DIR}")
    
    total_tasks = len(LEAGUES) * len(SEASONS)
    completed = 0
    
    for league in LEAGUES:
        for season in SEASONS:
            download_league_data(league, season)
            completed += 1
            logger.info(f"Progress: {completed}/{total_tasks} segments done.\n")
            
            # Sleep to be polite to the server and avoid rate limits
            time.sleep(3)

    logger.info("🏁 ALL DOWNLOADS COMPLETE.")
    logger.info("You can now run your app offline using this cached data.")

if __name__ == "__main__":
    main()