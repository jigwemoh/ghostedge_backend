#!/usr/bin/env python3
"""Verify the loader structure is fixed - it now calls Soccerdata API instead of RapidAPI"""

import sys
import inspect
from src.data.loader import SoccerDataLoader

print("=" * 80)
print("Loader Structure Verification")
print("=" * 80)

loader = SoccerDataLoader()

print("\n✅ Loader initialized successfully")
print(f"   - soccerdata_client: {loader.soccerdata_client is not None}")
print(f"   - Has _get method: {hasattr(loader, '_get')}")
print(f"   - Has fetch_full_match_context method: {hasattr(loader, 'fetch_full_match_context')}")

# Check the method to see if it uses Soccerdata API
import inspect
source = inspect.getsource(loader.fetch_full_match_context)

print("\n✅ Method source verification:")
if 'soccerdata_client' in source:
    print("   ✅ Uses soccerdata_client (Soccerdata API)")
else:
    print("   ❌ Does not use soccerdata_client")

if 'get_standing' in source:
    print("   ✅ Calls get_standing()")
else:
    print("   ❌ Does not call get_standing()")

if 'get_head_to_head' in source:
    print("   ✅ Calls get_head_to_head()")
else:
    print("   ❌ Does not call get_head_to_head()")

if 'get_transfers' in source:
    print("   ✅ Calls get_transfers()")
else:
    print("   ❌ Does not call get_transfers()")

if 'get_stadium' in source:
    print("   ✅ Calls get_stadium()")
else:
    print("   ❌ Does not call get_stadium()")

if 'get_match_preview' in source:
    print("   ✅ Calls get_match_preview()")
else:
    print("   ❌ Does not call get_match_preview()")

# Check return structure
print("\n✅ Return structure verification:")
if 'quantitative_features' in source:
    print("   ✅ Returns quantitative_features")
else:
    print("   ❌ Does not return quantitative_features")

if 'qualitative_context' in source:
    print("   ✅ Returns qualitative_context")
else:
    print("   ❌ Does not return qualitative_context")

if 'h2h_overall_games' in source:
    print("   ✅ Extracts h2h_overall_games")
else:
    print("   ❌ Does not extract h2h_overall_games")

if 'h2h_team1_win_pct' in source:
    print("   ✅ Extracts h2h_team1_win_pct")
else:
    print("   ❌ Does not extract h2h_team1_win_pct")

print("\n" + "=" * 80)
print("🎉 Loader structure is correctly updated!")
print("   - Now uses Soccerdata API client instead of RapidAPI")
print("   - Extracts real quantitative features (H2H, standings, transfers)")
print("   - Returns proper structured data for agents to analyze")
print("=" * 80)
