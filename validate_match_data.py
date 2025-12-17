#!/usr/bin/env python3
"""
Debug script to validate match data and team IDs
Helps identify data mismatches in the pipeline
"""

from w5_engine.soccerdata_client import SoccerdataClient
import json

client = SoccerdataClient()

def validate_match_data(match_data: dict):
    """
    Validate match data by checking if team IDs match team names
    """
    print("\n" + "=" * 70)
    print("MATCH DATA VALIDATION")
    print("=" * 70)
    
    home_team_name = match_data.get('home_team')
    away_team_name = match_data.get('away_team')
    home_team_id = match_data.get('home_team_id')
    away_team_id = match_data.get('away_team_id')
    league_id = match_data.get('league_id')
    
    print(f"\n📋 Input Data:")
    print(f"   Home: {home_team_name} (ID: {home_team_id})")
    print(f"   Away: {away_team_name} (ID: {away_team_id})")
    print(f"   League ID: {league_id}")
    
    issues = []
    
    # Validate home team
    if home_team_id:
        print(f"\n🔍 Validating Home Team (ID: {home_team_id})...")
        home_info = client.get_team(home_team_id)
        if home_info:
            actual_name = home_info.get('name', 'Unknown')
            print(f"   ✅ Found: {actual_name}")
            
            # Check if name matches
            if home_team_name.lower() not in actual_name.lower() and actual_name.lower() not in home_team_name.lower():
                print(f"   ⚠️  NAME MISMATCH: Expected '{home_team_name}' but got '{actual_name}'")
                issues.append(f"Home team ID {home_team_id} is for {actual_name}, not {home_team_name}")
            else:
                print(f"   ✅ Name matches")
            
            # Check stadium
            home_stadium = client.get_stadium(team_id=home_team_id)
            if home_stadium:
                print(f"   ✅ Stadium: {home_stadium.get('name')}")
            else:
                print(f"   ⚠️  Stadium: Not found")
        else:
            print(f"   ❌ Could not find team with ID {home_team_id}")
            issues.append(f"Invalid home team ID: {home_team_id}")
    
    # Validate away team
    if away_team_id:
        print(f"\n🔍 Validating Away Team (ID: {away_team_id})...")
        away_info = client.get_team(away_team_id)
        if away_info:
            actual_name = away_info.get('name', 'Unknown')
            print(f"   ✅ Found: {actual_name}")
            
            # Check if name matches
            if away_team_name.lower() not in actual_name.lower() and actual_name.lower() not in away_team_name.lower():
                print(f"   ⚠️  NAME MISMATCH: Expected '{away_team_name}' but got '{actual_name}'")
                issues.append(f"Away team ID {away_team_id} is for {actual_name}, not {away_team_name}")
            else:
                print(f"   ✅ Name matches")
            
            # Check stadium
            away_stadium = client.get_stadium(team_id=away_team_id)
            if away_stadium:
                print(f"   ✅ Stadium: {away_stadium.get('name')}")
            else:
                print(f"   ⚠️  Stadium: Not found")
        else:
            print(f"   ❌ Could not find team with ID {away_team_id}")
            issues.append(f"Invalid away team ID: {away_team_id}")
    
    # Summary
    print(f"\n" + "=" * 70)
    if issues:
        print(f"❌ VALIDATION FAILED - {len(issues)} issue(s) found:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        print("\n💡 SOLUTION:")
        print("   Use 'find_team_ids.py' to find correct team IDs:")
        print(f"      python find_team_ids.py '{home_team_name}'")
        print(f"      python find_team_ids.py '{away_team_name}'")
    else:
        print(f"✅ VALIDATION PASSED - All data looks correct!")
    
    print("=" * 70)
    
    return len(issues) == 0

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Load from JSON file
        try:
            with open(sys.argv[1], 'r') as f:
                match_data = json.load(f)
            validate_match_data(match_data)
        except Exception as e:
            print(f"❌ Error loading file: {e}")
    else:
        # Example validation
        print("\nUsage: python validate_match_data.py <match_data.json>")
        print("\nExample with test data:")
        
        test_match = {
            "match_id": "4813541",
            "home_team": "Manchester City",
            "away_team": "West Ham",
            "home_team_id": 8456,      # <- This is wrong
            "away_team_id": 8654,      # <- This is wrong
            "league_id": 47
        }
        
        print(json.dumps(test_match, indent=2))
        validate_match_data(test_match)
