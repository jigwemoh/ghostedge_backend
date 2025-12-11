import os
from typing import Dict, Any
import json
from dotenv import load_dotenv

# Force load environment variables early
load_dotenv()

class LLMAgent:
    def __init__(self, persona_type: str, provider: str = 'openai', model_name: str = 'gpt-4o-mini'):
        self.persona = persona_type
        self.provider = provider
        self.model = model_name
        self.client = self._init_client()

    def _init_client(self):
        """Initialize clients based on provider."""
        # 1. SOCCERDATA (No Client needed)
        if self.provider == 'soccerdata':
            return None

        # 2. OPENAI
        if self.provider == 'openai':
            from openai import OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                print(f"⚠️ Agent {self.persona}: OPENAI_API_KEY not found in env.")
            return OpenAI(api_key=api_key)
        
        # 3. ANTHROPIC (CLAUDE)
        elif self.provider == 'anthropic':
            from anthropic import Anthropic
            # FIX: Explicitly get key from environment to prevent 'Could not resolve auth' errors
            api_key = os.getenv('ANTHROPIC_API_KEY')
            
            if not api_key:
                print(f"❌ CRITICAL ERROR: Agent {self.persona}: ANTHROPIC_API_KEY is MISSING in environment variables.")
                return None
            else:
                # DEBUG: Print first 4 chars to confirm key is loaded in Render logs
                # print(f"✅ Agent {self.persona}: Anthropic Key Loaded ({api_key[:4]}...)")
                pass
            
            return Anthropic(api_key=api_key)
            
        return None

    def analyze(self, match_data: Dict[str, Any], blind_mode: bool = True) -> Dict[str, Any]:
        """Main analysis function."""
        
        # SPECIAL CASE: Pure Data Agent (Statistician)
        if self.provider == 'soccerdata':
            return self._analyze_with_data(match_data)

        # STANDARD AI AGENTS
        system_prompt = self._get_persona_prompt()
        user_prompt = self._build_data_prompt(match_data)

        response_text = self._query_model(system_prompt, user_prompt)
        return self._parse_json(response_text)

    def _analyze_with_data(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deterministic analysis using hard data (Standings & H2H)."""
        stats = match_data.get("quantitative_features", {})
        
        # Default probabilities (Draw bias)
        home_prob, draw_prob, away_prob = 0.33, 0.34, 0.33
        reasoning = []

        # 1. ANALYZE STANDINGS
        standings = stats.get('standings', [])
        home_team = match_data.get('home_team')
        away_team = match_data.get('away_team')
        
        if standings and len(standings) > 0:
            def get_rank(name):
                for row in standings:
                    # Check both 'team' and 'Squad' keys as naming varies
                    if row.get('team') == name or row.get('Squad') == name:
                        return int(row.get('Rk', 10))
                return 10 # Default mid-table

            home_rank = get_rank(home_team)
            away_rank = get_rank(away_team)
            
            diff = away_rank - home_rank 
            
            if diff > 5: 
                home_prob += 0.15; away_prob -= 0.10; draw_prob -= 0.05
                reasoning.append(f"{home_team} is ranked significantly higher (#{home_rank} vs #{away_rank}).")
            elif diff < -5: 
                away_prob += 0.15; home_prob -= 0.10; draw_prob -= 0.05
                reasoning.append(f"{away_team} is ranked significantly higher (#{away_rank} vs #{home_rank}).")
            else:
                reasoning.append(f"Teams are close in standings (#{home_rank} vs #{away_rank}).")
        else:
            reasoning.append("No live standings data available.")

        # 2. ANALYZE H2H
        h2h_text = str(stats.get('h2h_summary', '')).lower()
        if "meetings" in h2h_text:
            reasoning.append(f"H2H Factor: {h2h_text}")
        else:
            reasoning.append("No significant H2H history.")

        total = home_prob + draw_prob + away_prob
        return {
            "home_win": round(home_prob / total, 2),
            "draw": round(draw_prob / total, 2),
            "away_win": round(away_prob / total, 2),
            "confidence": 0.85, 
            "reasoning": " ".join(reasoning)
        }

    def _get_persona_prompt(self):
        if self.persona == 'statistician':
            return "ROLE: Quantitative Analyst." # Unused for soccerdata provider
        elif self.persona == 'tactician':
            return """
            ROLE: Football Tactical Scout.
            DIRECTIVE: Focus on styles, formations, and venue advantage.
            OUTPUT: Valid JSON with probabilities.
            """
        elif self.persona == 'sentiment_analyst':
            return """
            ROLE: Market & News Sentiment Tracker.
            DIRECTIVE: Analyze the 'Qualitative Context'. Look for morale, pressure, or crisis.
            OUTPUT: Valid JSON with probabilities.
            """
        return "You are a sports analyst."

    def _build_data_prompt(self, data):
        stats = data.get("quantitative_features", {})
        context = data.get("qualitative_context", {})
        
        return f"""
        MATCH: {data.get('home_team')} vs {data.get('away_team')}
        
        NUMBERS:
        - Standings: {len(stats.get('standings', []))} rows available.
        - H2H: {stats.get('h2h_summary', 'N/A')}
        - Form: {stats.get('home_form', 'N/A')}
        
        CONTEXT:
        - Venue: {context.get('venue', 'Unknown')}
        - News: {context.get('news_headlines', 'None')}
        
        TASK: Predict outcome as JSON {{ "home_win": 0.X, "draw": 0.X, "away_win": 0.X, "confidence": 0.X, "reasoning": "..." }}
        """

    def _query_model(self, system_msg, user_msg):
        try:
            # --- OPENAI ---
            if self.provider == 'openai':
                if not self.client: raise ValueError("OpenAI Client missing")
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                return resp.choices[0].message.content
            
            # --- ANTHROPIC (CLAUDE) ---
            elif self.provider == 'anthropic':
                if not self.client: raise ValueError("Anthropic Client missing (Check API Key)")
                
                # Claude SDK Call
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    temperature=0.2,
                    system=system_msg,
                    messages=[
                        {"role": "user", "content": user_msg},
                        # Prefill assistant response to force JSON
                        {"role": "assistant", "content": "{"} 
                    ]
                )
                # Re-attach the opening brace we forced
                return "{" + message.content[0].text

            return "{}" 
            
        except Exception as e:
            print(f"❌ LLM Error ({self.persona}): {e}")
            return json.dumps({
                "home_win": 0.33, "draw": 0.34, "away_win": 0.33, 
                "confidence": 0, "reasoning": f"AI Failure: {str(e)}"
            })

    def _parse_json(self, text):
        try:
            # Cleanup for robust parsing
            cleaned = text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        except:
            return {"home_win": 0.33, "draw": 0.34, "away_win": 0.33, "confidence": 0, "reasoning": "JSON Parse Error"}