#!/usr/bin/env python3
"""
QUICK START: Soccerdata API Integration

Run this script after setting up your API key to test the integration.
"""

import sys
import os
from pathlib import Path

# Add w5_engine to path
sys.path.insert(0, str(Path(__file__).parent))

def check_setup():
    """Verify environment setup"""
    print("🔍 Checking Setup...")
    
    # Check .env file
    env_file = Path('.env')
    if not env_file.exists():
        print("   ❌ .env file not found")
        print("   Create .env with:")
        print("      SOCCERDATA_API_KEY=your_key")
        print("      OPENAI_API_KEY=your_key")
        print("      ANTHROPIC_API_KEY=your_key")
        return False
    
    # Check API key
    from dotenv import load_dotenv
    load_dotenv()
    
    soccerdata_key = os.getenv('SOCCERDATA_API_KEY')
    if not soccerdata_key:
        print("   ❌ SOCCERDATA_API_KEY not set in .env")
        return False
    
    print("   ✅ .env file found")
    print("   ✅ SOCCERDATA_API_KEY set")
    
    return True


def test_client():
    """Test SoccerdataClient"""
    print("\n🧪 Testing SoccerdataClient...")
    
    try:
        from w5_engine.soccerdata_client import SoccerdataClient
        client = SoccerdataClient()
        
        # Test 1: Get standings
        print("   Testing GET STANDING...")
        standing = client.get_standing(league_id=228)
        if standing:
            print("   ✅ League standing fetched")
        else:
            print("   ❌ Failed to fetch standing")
            return False
        
        # Test 2: Get head-to-head
        print("   Testing GET HEAD-TO-HEAD...")
        h2h = client.get_head_to_head(team_1_id=4138, team_2_id=4137)
        if h2h:
            print("   ✅ H2H data fetched")
        else:
            print("   ❌ Failed to fetch H2H")
            return False
        
        print("   ✅ SoccerdataClient working")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False


def test_consensus_engine():
    """Test ConsensusEngine with API"""
    print("\n🤖 Testing ConsensusEngine...")
    
    try:
        from w5_engine.debate import ConsensusEngine
        
        engine = ConsensusEngine()
        print("   ✅ ConsensusEngine initialized")
        
        # Test match data
        match_data = {
            'home_team': 'Liverpool',
            'away_team': 'Manchester United',
            'home_team_id': 4138,
            'away_team_id': 4137,
            'league_id': 228,
        }
        
        print("   Running consensus with API enrichment...")
        result = engine.run_consensus(match_data)
        
        if result and result.get('consensus_prediction'):
            pred = result['consensus_prediction']
            print(f"\n   📊 Prediction Results:")
            print(f"      Home Win: {pred['home_win']:.1%}")
            print(f"      Draw: {pred['draw']:.1%}")
            print(f"      Away Win: {pred['away_win']:.1%}")
            print(f"\n   ✅ ConsensusEngine working with API")
            return True
        else:
            print("   ❌ Failed to get prediction")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main quick start"""
    print("=" * 60)
    print("SOCCERDATA API INTEGRATION - QUICK START")
    print("=" * 60)
    
    # Step 1: Check setup
    if not check_setup():
        print("\n⚠️  Setup incomplete. Please configure .env file.")
        return 1
    
    # Step 2: Test client
    if not test_client():
        print("\n⚠️  SoccerdataClient test failed")
        return 1
    
    # Step 3: Test engine
    if not test_consensus_engine():
        print("\n⚠️  ConsensusEngine test failed")
        return 1
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - READY TO USE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Import ConsensusEngine from w5_engine.debate")
    print("2. Provide match_data with team_id and league_id")
    print("3. Call engine.run_consensus(match_data)")
    print("4. Use predictions and API data in your application")
    print("\nDocumentation:")
    print("- Full guide: SOCCERDATA_API_INTEGRATION.md")
    print("- Examples: w5_engine/api_usage_examples.py")
    print("- API Summary: IMPLEMENTATION_SUMMARY.md")
    print("\n" + "=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
