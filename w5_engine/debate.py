from typing import Dict, List, Any
from .agents import LLMAgent
import numpy as np

class ConsensusEngine:
    def __init__(self, debate_rounds: int = 2, min_agents: int = 3):
        self.debate_rounds = debate_rounds
        
        # --- AGENT CONFIGURATION ---
        self.agents = [
            # 1. Statistician (OpenAI GPT-4o-mini)
            LLMAgent('statistician', provider='openai', model_name='gpt-4o-mini'),
            
            # 2. Tactician (OpenAI GPT-4o-mini)
            LLMAgent('tactician', provider='openai', model_name='gpt-4o-mini'),
            
            # 3. Sentiment Analyst (Google Gemini 1.0 Pro)
            # FIX: Trying 'gemini-1.0-pro' as a stable alternative to 1.5-flash/pro
            LLMAgent('sentiment_analyst', provider='google', model_name='gemini-1.0-pro')
        ]

    def run_consensus(self, match_data: Dict[str, Any], baseline_prediction=None) -> Dict[str, Any]:
        print(f"🤖 Starting W-5 Consensus Debate for {match_data.get('home_team')}...")

        # --- ROUND 1: BLIND VOTE ---
        # Agents analyze in isolation so they don't copy each other
        round1_results = []
        for agent in self.agents:
            analysis = agent.analyze(match_data, blind_mode=True)
            analysis['agent'] = agent.persona
            round1_results.append(analysis)
            print(f"   👤 {agent.persona.title()} ({agent.provider}): Home {analysis.get('home_win'):.0%} | {analysis.get('reasoning')}")

        # --- AGGREGATION (Meta-Learning Logic) ---
        # We don't just average them. We weigh them based on reliability.
        weights = {
            "statistician": 1.5,      # Hard data is king
            "tactician": 1.0,         # Tactical fit is secondary
            "sentiment_analyst": 0.8  # Narrative is tertiary
        }

        final_pred = self._calculate_weighted_average(round1_results, weights)
        
        # --- GENERATE SUMMARY ---
        debate_summary = self._generate_summary(round1_results, final_pred)

        return {
            "consensus_prediction": final_pred,
            "confidence": np.mean([r.get('confidence', 0.5) for r in round1_results]),
            "agreement_score": self._calculate_agreement(round1_results),
            "debate_summary": debate_summary,
            "agent_analyses": round1_results
        }

    def _calculate_weighted_average(self, results, weights):
        home_score, draw_score, away_score, total_weight = 0, 0, 0, 0
        
        for res in results:
            w = weights.get(res['agent'], 1.0)
            home_score += res.get('home_win', 0.33) * w
            draw_score += res.get('draw', 0.33) * w
            away_score += res.get('away_win', 0.33) * w
            total_weight += w
            
        return {
            "home_win": round(home_score / total_weight, 2),
            "draw": round(draw_score / total_weight, 2),
            "away_win": round(away_score / total_weight, 2)
        }

    def _calculate_agreement(self, results):
        # Calculate standard deviation of the Home Win probability
        home_probs = [r.get('home_win', 0.33) for r in results]
        std_dev = np.std(home_probs)
        # Low variance = High agreement. Scale 0-1.
        return max(0, 1.0 - (std_dev * 2))

    def _generate_summary(self, results, final_pred):
        try:
            winner = max(final_pred, key=final_pred.get).replace('_', ' ').title()
            prob = final_pred[max(final_pred, key=final_pred.get)]
            
            summary = f"VERDICT: {winner} ({prob:.0%})\n\n"
            for res in results:
                summary += f"• {res['agent'].title()}: {res.get('reasoning', 'No reasoning provided')}\n"
            
            return summary
        except Exception as e:
            return "Summary generation failed."