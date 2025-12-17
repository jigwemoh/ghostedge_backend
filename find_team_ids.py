#!/usr/bin/env python3
"""
Utility to find correct team IDs for matches
Run this to get the correct team IDs before calling the API
"""

from w5_engine.soccerdata_client import SoccerdataClient
import sys

client = SoccerdataClient()

def find_team_id(team_name: str, league_id: int = None):
    """Find team ID by name"""
    print(f"\n🔍 Searching for team: {team_name}")
    
    results = client.search_team_by_name(team_name, league_id)
    
    if results:
        print(f"✅ Found {len(results)} result(s):\n")
        for i, team in enumerate(results, 1):
            league_info = f" ({team.get('league', 'Unknown League')})" if team.get('league') else ""
            print(f"  {i}. {team['name']} - ID: {team['id']}{league_info}")
        return results
    else:
        print(f"❌ No results found for '{team_name}'")
        return None

def get_team_info(team_id: int):
    """Get detailed info about a team"""
    print(f"\n📋 Fetching team info for ID: {team_id}")
    
    team_info = client.get_team(team_id)
    if team_info:
        print(f"✅ Team: {team_info.get('name')}")
        print(f"   Country: {team_info.get('country')}")
        print(f"   Founded: {team_info.get('founded_year', 'N/A')}")
        return team_info
    else:
        print(f"❌ Could not find team with ID {team_id}")
        return None

def get_stadium_info(team_id: int):
    """Get stadium info for a team"""
    print(f"\n🏟️  Fetching stadium info for team ID: {team_id}")
    
    stadium = client.get_stadium(team_id=team_id)
    if stadium:
        print(f"✅ Stadium: {stadium.get('name', 'Unknown')}")
        print(f"   Capacity: {stadium.get('capacity', 'N/A')}")
        print(f"   Country: {stadium.get('country', 'N/A')}")
        return stadium
    else:
        print(f"❌ Could not find stadium for team ID {team_id}")
        return None

if __name__ == "__main__":
    print("=" * 70)
    print("Team ID Finder - Find correct team IDs for your matches")
    print("=" * 70)
    
    if len(sys.argv) > 1:
        team_name = sys.argv[1]
        league_id = int(sys.argv[2]) if len(sys.argv) > 2 else None
        
        results = find_team_id(team_name, league_id)
        
        if results and len(results) > 0:
            # Get more info for first result
            team_id = results[0]['id']
            get_team_info(team_id)
            get_stadium_info(team_id)
    else:
        # Interactive mode
        print("\nUsage:")
        print("  python find_team_ids.py 'Team Name' [league_id]")
        print("\nExamples:")
        print("  python find_team_ids.py 'Manchester City'")
        print("  python find_team_ids.py 'Liverpool' 39")
        print("  python find_team_ids.py 'West Ham'")
        
        print("\n" + "=" * 70)
        print("Running interactive search...")
        print("=" * 70)
        
        while True:
            team_name = input("\nEnter team name (or 'quit' to exit): ").strip()
            if team_name.lower() == 'quit':
                break
            
            results = find_team_id(team_name)
            
            if results:
                choice = input("\nSelect team number (or press Enter to skip): ").strip()
                if choice.isdigit() and 0 < int(choice) <= len(results):
                    team_id = results[int(choice) - 1]['id']
                    get_team_info(team_id)
                    get_stadium_info(team_id)
    
    print("\n" + "=" * 70)
