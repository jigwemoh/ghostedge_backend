#!/usr/bin/env python3
"""
Test the automatic team ID correction feature
"""

from src.data.loader import real_data_loader
import json

print("=" * 70)
print("AUTOMATIC TEAM ID CORRECTION TEST")
print("=" * 70)

# Test with WRONG team IDs (like your data)
test_match_wrong = {
    "home_team": "Manchester City",
    "away_team": "West Ham",
    "event_id": 1234567,
    "league_id": 39,  # Premier League
    "home_team_id": 8456,  # ← WRONG ID (Worgl)
    "away_team_id": 8654,  # ← WRONG ID (Asenovets)
}

print("\n📋 Test Match (with WRONG team IDs):")
print(f"   Home: {test_match_wrong['home_team']} (Given ID: 8456 - WRONG)")
print(f"   Away: {test_match_wrong['away_team']} (Given ID: 8654 - WRONG)")
print(f"   League: 39 (Premier League)")

print("\n" + "=" * 70)
print("Running loader with auto-correction enabled...")
print("=" * 70)

match_context = real_data_loader.fetch_full_match_context(
    home_team=test_match_wrong['home_team'],
    away_team=test_match_wrong['away_team'],
    event_id=test_match_wrong['event_id'],
    league_id=test_match_wrong['league_id'],
    home_team_id=test_match_wrong['home_team_id'],
    away_team_id=test_match_wrong['away_team_id']
)

print("\n" + "=" * 70)
print("✅ RESULT AFTER AUTO-CORRECTION:")
print("=" * 70)

print("\n🏟️ VENUES:")
print(f"   Home: {match_context['qualitative_context'].get('home_venue', 'N/A')}")
print(f"   Away: {match_context['qualitative_context'].get('away_venue', 'N/A')}")

print("\n👥 TRANSFERS:")
quant = match_context['quantitative_features']
print(f"   Home Recent Signings: {quant.get('home_recent_signings', 'N/A')}")
print(f"   Away Recent Signings: {quant.get('away_recent_signings', 'N/A')}")

if 'h2h_overall_games' in quant:
    print("\n🔄 HEAD-TO-HEAD:")
    print(f"   Total Games: {quant.get('h2h_overall_games', 'N/A')}")
    print(f"   {test_match_wrong['home_team']} Wins: {quant.get('h2h_team1_wins', 'N/A')}")
    print(f"   Win %: {quant.get('h2h_team1_win_pct', 'N/A')}%")

print("\n" + "=" * 70)
print("Full Response:")
print("=" * 70)
print(json.dumps(match_context, indent=2))
