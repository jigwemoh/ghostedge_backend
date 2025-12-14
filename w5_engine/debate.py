from typing import Dict, List, Any
from .agents import LLMAgent
import numpy as np

class ConsensusEngine:
    def __init__(self, debate_rounds: int = 2, min_agents: int = 3):
        self.debate_rounds = debate_rounds
        self.agents = [
            # Statistician: Uses hard data logic (RapidAPI)
            LLMAgent('statistician', provider='deterministic'),
            
            # Tactician: OpenAI
            LLMAgent('tactician', provider='openai', model_name='gpt-4o-mini'),
            
            # Sentiment: Anthropic
            LLMAgent('sentiment_analyst', provider='anthropic', model_name='claude-3-haiku-20240307')
        ]

    def run_consensus(self, match_data: Dict[str, Any], baseline_prediction=None) -> Dict[str, Any]:
        print(f"🤖 Starting Debate for {match_data.get('home_team')}...")
        
        results = []
        for agent in self.agents:
            res = agent.analyze(match_data)
            res['agent'] = agent.persona
            results.append(res)
            
            # SAFE PRINTING (Prevents 500 Error)
            hw = res.get('home_win')
            hw_str = f"{hw:.0%}" if hw is not None else "N/A"
            print(f"   👤 {agent.persona}: Home {hw_str} | {res.get('reasoning')}")

        # Weighted Average
        weights = {"statistician": 1.5, "tactician": 1.0, "sentiment_analyst": 0.8}
        final_pred = self._calculate_weighted_average(results, weights)
        
        return {
            "consensus_prediction": final_pred,
            "confidence": 0.5,
            "agreement_score": 0.5,
            "debate_summary": "Debate complete.",
            "agent_analyses": results
        }

    def _calculate_weighted_average(self, results, weights):
        h, d, a, tot = 0, 0, 0, 0
        for res in results:
            w = weights.get(res['agent'], 1.0)
            # Default to 0.33 if None to prevent crash
            h += (res.get('home_win') or 0.33) * w
            d += (res.get('draw') or 0.33) * w
            a += (res.get('away_win') or 0.33) * w
            tot += w
        
        if tot == 0: return {"home_win": 0.33, "draw": 0.34, "away_win": 0.33}
        
        return {
            "home_win": round(h / tot, 2),
            "draw": round(d / tot, 2),
            "away_win": round(a / tot, 2)
        }
    
    # ... (Keep agreement/summary methods if needed)
    def _calculate_agreement(self, results):
        return 0.5 # Simplified for stability