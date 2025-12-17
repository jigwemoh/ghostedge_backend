#!/usr/bin/env python3
"""Test script to verify loader is returning real API data instead of placeholders"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

from src.data.loader import real_data_loader
import json

print("=" * 80)
print("Testing Loader Fix - Real API Data Enrichment")
print("=" * 80)

# Test with Liverpool vs Arsenal (example match)
# You'll need to provide actual team IDs and league ID for your data
test_match = {
    'home_team': 'Liverpool',
    'away_team': 'Arsenal',
    'event_id': 1234567,  # Replace with actual event ID
    'league_id': 39,      # Premier League
    'home_team_id': 64,   # Liverpool
    'away_team_id': 42,   # Arsenal
}

print(f"\n📋 Test Match: {test_match['home_team']} vs {test_match['away_team']}")
print(f"   Event ID: {test_match['event_id']}")
print(f"   League ID: {test_match['league_id']}")
print(f"   Home Team ID: {test_match['home_team_id']}")
print(f"   Away Team ID: {test_match['away_team_id']}")

print("\n🔄 Fetching match context...")
match_context = real_data_loader.fetch_full_match_context(
    home_team=test_match['home_team'],
    away_team=test_match['away_team'],
    event_id=test_match['event_id'],
    league_id=test_match['league_id'],
    home_team_id=test_match['home_team_id'],
    away_team_id=test_match['away_team_id']
)

print("\n✅ Match Context Retrieved:")
print("\n📊 Quantitative Features:")
quant = match_context.get('quantitative_features', {})
for key, value in quant.items():
    if isinstance(value, (list, dict)):
        print(f"   {key}: {json.dumps(value, indent=6)}")
    else:
        print(f"   {key}: {value}")

print("\n💭 Qualitative Context:")
qual = match_context.get('qualitative_context', {})
for key, value in qual.items():
    if isinstance(value, (list, dict)):
        print(f"   {key}: {json.dumps(value, indent=6)}")
    else:
        print(f"   {key}: {value}")

print("\n" + "=" * 80)
print("✅ VERIFICATION RESULTS:")
print("=" * 80)

# Check for real data (not placeholders)
issues = []

if quant.get('h2h_summary') == "No H2H data found.":
    issues.append("❌ H2H data is still a placeholder")
else:
    print("✅ H2H data is real")

if quant.get('home_form') == "Form Data Unavailable":
    issues.append("❌ Form data is still a placeholder")
else:
    print("✅ Form data is real")

if 'h2h_overall_games' in quant:
    print(f"✅ H2H stats extracted: {quant['h2h_overall_games']} games")
else:
    issues.append("❌ H2H stats not extracted")

if 'league_leader_points' in quant:
    print(f"✅ League standing extracted: Leader has {quant['league_leader_points']} points")
else:
    issues.append("❌ League standing not extracted")

if qual.get('news_headlines') == "Live news requires paid tier":
    print("⚠️  News headlines placeholder (expected - paid tier)")
else:
    print(f"✅ News headlines: {qual.get('news_headlines')}")

if issues:
    print("\n⚠️  Issues Found:")
    for issue in issues:
        print(f"   {issue}")
else:
    print("\n🎉 All checks passed! Loader is returning real API data.")

print("\n" + "=" * 80)
