"""
Test script to demonstrate the enhanced debate engine with detailed summary output
"""
import json
from w5_engine.debate import ConsensusEngine

def test_debate_with_summary():
    """Test the debate engine with enhanced summary output"""
    
    print("\n" + "="*80)
    print("🤖 GHOSTEDGE AI DEBATE ENGINE - ENHANCED SUMMARY TEST")
    print("="*80 + "\n")
    
    engine = ConsensusEngine()
    
    # Match data with real statistics
    match_data = {
        "match_id": "1234567",
        "home_team": "Manchester City",
        "away_team": "West Ham",
        "home_team_id": 50,
        "away_team_id": 48,
        "league_id": 39,
        "quantitative_features": {
            "h2h_overall_games": 48,
            "h2h_team1_wins": 26,
            "h2h_team2_wins": 10,
            "h2h_draws": 12,
            "h2h_team1_win_pct": 54.17,
            "h2h_team1_home_wins": 16,
            "league_leader_points": 45
        },
        "qualitative_context": {
            "home_venue": "Etihad Stadium",
            "home_capacity": 55097,
            "away_venue": "London Stadium",
            "away_capacity": 62500,
            "weather": "Sunny, 15°C",
            "excitement_rating": 7.2,
            "home_recent_signings": 4,
            "away_recent_signings": 3
        }
    }
    
    # Run consensus debate
    print("Starting debate with all three agents...\n")
    result = engine.run_consensus(match_data)
    
    # Print the detailed debate summary
    print("\n" + result["debate_summary"])
    
    # Print additional metrics
    print("\n" + "="*80)
    print("📊 AGREEMENT & CONFIDENCE METRICS")
    print("="*80)
    print(f"Confidence Score: {result['confidence']:.0%}")
    print(f"Agreement Score: {result['agreement_score']:.0%}")
    
    # Print detailed agent analyses
    print("\n" + "="*80)
    print("📋 DETAILED AGENT ANALYSES")
    print("="*80)
    for analysis in result["agent_analyses"]:
        print(f"\n{analysis['agent'].upper()} (Weight: {analysis['weight']}):")
        print(f"  Prediction: H={analysis['prediction']['home_win']:.0%} " +
              f"D={analysis['prediction']['draw']:.0%} " +
              f"A={analysis['prediction']['away_win']:.0%}")
        print(f"  Confidence: {analysis['confidence']:.0%}")
        print(f"  Weighted Contribution: H={analysis['weighted_contribution']['home_win']:.3f} " +
              f"D={analysis['weighted_contribution']['draw']:.3f} " +
              f"A={analysis['weighted_contribution']['away_win']:.3f}")
        print(f"  Reasoning: {analysis['reasoning']}")
    
    # Print final JSON response
    print("\n" + "="*80)
    print("📤 FULL API RESPONSE")
    print("="*80)
    response = {
        "consensus_prediction": result["consensus_prediction"],
        "confidence": result["confidence"],
        "agreement_score": result["agreement_score"],
        "agent_analyses": result["agent_analyses"]
    }
    print(json.dumps(response, indent=2))

if __name__ == "__main__":
    test_debate_with_summary()
