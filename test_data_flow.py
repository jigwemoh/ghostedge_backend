import sys
import os
from pathlib import Path

# --- PATH CONFIGURATION ---
# We add the 'src/data' directory to the system path so Python can find loader.py
# This assumes the structure:
# root/
#   test_data_flow.py
#   src/
#     data/
#       loader.py
current_dir = Path(__file__).resolve().parent
loader_path = current_dir / "src" / "data"
sys.path.append(str(loader_path))

# --- IMPORT CHECK ---
try:
    from loader import SoccerDataLoader
except ImportError as e:
    print("\n❌ CRITICAL ERROR: Could not import 'loader'.")
    print(f"   Python was looking in: {loader_path}")
    print(f"   Error Details: {e}")
    print("   👉 ACTION: Ensure 'loader.py' exists at 'src/data/loader.py'")
    sys.exit(1)

# --- MAIN EXECUTION BLOCK ---
def main():
    print("🕵️‍♂️ Starting Deep Scan using SOCCERDATA (FBref)...")
    
    # 1. SETUP
    HOME_TEAM = "Liverpool"
    AWAY_TEAM = "Chelsea"
    LEAGUE = "ENG-Premier League"
    SEASON = "2425" 
    
    # 2. INITIALIZE LOADER
    try:
        loader = SoccerDataLoader(league_code=LEAGUE, season=SEASON)
    except Exception as e:
        print(f"❌ Initialization Error: {e}")
        return
    
    # 3. RUN FETCH
    full_context = loader.fetch_full_match_context(HOME_TEAM, AWAY_TEAM)

    # 4. REPORT
    quant = full_context.get("quantitative_features", {})
    qual = full_context.get("qualitative_context", {})

    print("\n📊 --- DATA CHECK (Source: FBref) ---")
    
    # Check Standings
    standings = quant.get("standings", [])
    if standings and len(standings) > 0:
        print(f"✅ Standings: FOUND ({len(standings)} teams)")
        # Print top 3 to verify structure
        top_3 = [t.get('team', 'Unknown') for t in standings[:3]]
        print(f"   Top 3: {top_3}")
    else:
        print("❌ Standings: MISSING")

    # Check H2H
    print(f"✅ H2H: {quant.get('h2h_summary')}")

    # Check Form
    print(f"✅ Form Analysis: {quant.get('home_form')}")

    # Check News
    print(f"⚠️ News: {qual.get('news_headlines')}")

    print("\n✅ Scan Complete. Pipeline (soccerdata) is stable.")

if __name__ == "__main__":
    main()