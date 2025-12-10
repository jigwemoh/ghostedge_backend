from src.data.loader import real_data_loader
import json

def test_pipeline_data():
    print("🕵️‍♂️ Starting Deep Scan of Free API Pipeline...")
    
    # Example: Liverpool vs Man City
    TEST_EVENT_ID = 4621624
    HOME_ID = 8650
    AWAY_ID = 8456
    LEAGUE_ID = 47

    print(f"📡 Calling 14+ Endpoints for Event {TEST_EVENT_ID}...")
    data = real_data_loader.fetch_full_match_context(
        event_id=TEST_EVENT_ID,
        home_id=HOME_ID,
        away_id=AWAY_ID,
        league_id=LEAGUE_ID
    )

    stats = data.get("quantitative_features", {})
    context = data.get("qualitative_context", {})

    print("\n📊 --- DATA CHECK ---")
    
    if stats.get("tactical_setup", {}).get("home_formation") != "Unknown":
        print(f"✅ Lineups: FOUND ({stats['tactical_setup']['home_formation']})")
    else:
        print("❌ Lineups: MISSING")

    if "Rank" in stats.get("standings", ""):
        print(f"✅ Standings: FOUND ({stats['standings']})")
    else:
        print("❌ Standings: MISSING")

    if context.get("news_headlines"):
        print("✅ News: FOUND")
    else:
        print("⚠️ News: EMPTY")

    if stats.get("key_threats"):
        print(f"✅ Top Scorers: FOUND ({stats['key_threats'][0]})")
    else:
        print("❌ Top Scorers: MISSING")

if __name__ == "__main__":
    test_pipeline_data()