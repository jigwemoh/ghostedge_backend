import os
from typing import Dict, Any
import json
from dotenv import load_dotenv

load_dotenv()

class LLMAgent:
    def __init__(self, persona_type: str, provider: str = 'openai', model_name: str = 'gpt-4o-mini'):
        self.persona = persona_type
        self.provider = provider
        self.model = model_name
        self.client = self._init_client()

    def _init_client(self):
        """Initialize clients based on provider."""
        # 'soccerdata' provider needs no client, it uses logic.
        if self.provider == 'soccerdata':
            return None

        if self.provider == 'openai':
            from openai import OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                print(f"⚠️ Agent {self.persona}: OPENAI_API_KEY not found in env.")
            return OpenAI(api_key=api_key)
        
        elif self.provider == 'anthropic':
            from anthropic import Anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                print(f"⚠️ Agent {self.persona}: ANTHROPIC_API_KEY not found in env.")
            return Anthropic(api_key=api_key)
            
        return None

    def analyze(self, match_data: Dict[str, Any], blind_mode: bool = True) -> Dict[str, Any]:
        """
        Main analysis function.
        """
        # --- NEW LOGIC: BYPASS LLM FOR PURE DATA AGENTS ---
        if self.provider == 'soccerdata':
            return self._analyze_with_data(match_data)

        # Standard LLM Flow
        system_prompt = self._get_persona_prompt()
        user_prompt = self._build_data_prompt(match_data)

        response_text = self._query_model(system_prompt, user_prompt)
        return self._parse_json(response_text)

    def _analyze_with_data(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministic analysis using hard data (Standings & H2H)
        This replaces the LLM for the 'Statistician' role.
        """
        stats = match_data.get("quantitative_features", {})
        
        # Default probabilities (Draw bias)
        home_prob, draw_prob, away_prob = 0.33, 0.34, 0.33
        reasoning = []

        # 1. ANALYZE STANDINGS (If available)
        standings = stats.get('standings', [])
        home_team = match_data.get('home_team')
        away_team = match_data.get('away_team')
        
        if standings and len(standings) > 0:
            # Helper to find rank
            def get_rank(name):
                for row in standings:
                    if row.get('team') == name or row.get('Squad') == name:
                        return int(row.get('Rk', 10))
                return 10 # Default mid-table

            home_rank = get_rank(home_team)
            away_rank = get_rank(away_team)
            
            diff = away_rank - home_rank # Positive means home is better (lower rank)
            
            if diff > 5: # Home is much better
                home_prob += 0.15; away_prob -= 0.10; draw_prob -= 0.05
                reasoning.append(f"{home_team} is ranked significantly higher (#{home_rank} vs #{away_rank}).")
            elif diff < -5: # Away is much better
                away_prob += 0.15; home_prob -= 0.10; draw_prob -= 0.05
                reasoning.append(f"{away_team} is ranked significantly higher (#{away_rank} vs #{home_rank}).")
            else:
                reasoning.append("Teams are close in league standings.")

        # 2. ANALYZE H2H (Simple keyword check on the summary string)
        h2h_text = stats.get('h2h_summary', '').lower()
        if "meetings" in h2h_text:
            reasoning.append(f"Historical context: {h2h_text}")
        else:
            reasoning.append("No significant H2H data available.")

        # Normalize probabilities to sum to 1.0
        total = home_prob + draw_prob + away_prob
        return {
            "home_win": round(home_prob / total, 2),
            "draw": round(draw_prob / total, 2),
            "away_win": round(away_prob / total, 2),
            "confidence": 0.9, # High confidence because it's hard data
            "reasoning": " ".join(reasoning)
        }

    def _get_persona_prompt(self):
        """Defines HOW the agent thinks."""
        if self.persona == 'statistician':
            return "ROLE: Ruthless Quantitative Analyst..." # (Unused if provider=soccerdata)
        elif self.persona == 'tactician':
            return """
            ROLE: Football Tactical Scout.
            DIRECTIVE: Focus on styles, injuries, and venue. Ignore the league table positions.
            OUTPUT: You must output a valid JSON object.
            LOGIC:
            1. Look at 'Key Threats' - does the opponent have a counter?
            2. Check 'Venue' - is it a fortress (e.g., Anfield)?
            3. Check 'Injuries/News' - is a star player missing?
            """
        elif self.persona == 'sentiment_analyst':
            return """
            ROLE: Market & News Sentiment Tracker.
            DIRECTIVE: Read the 'Qualitative Context'. Look for drama, pressure, or hype.
            OUTPUT: You must output a valid JSON object.
            LOGIC:
            1. If news mentions "Manager Sacked" or "Crisis", fade that team.
            2. If a team has won a major trophy recently, boost their confidence.
            """
        return "You are a helpful sports analyst."

    def _build_data_prompt(self, data):
        """Injects the RAPIDAPI/SoccerData into the prompt."""
        stats = data.get("quantitative_features", {})
        context = data.get("qualitative_context", {})
        
        # Safely get list items or default strings
        top_scorers = stats.get('key_threats', {}).get('top_scorers', [])
        if isinstance(top_scorers, list):
            top_scorers_str = ', '.join(top_scorers)
        else:
            top_scorers_str = str(top_scorers)

        return f"""
        MATCH: {data.get('home_team')} vs {data.get('away_team')}
        
        === QUANTITATIVE DATA (The Numbers) ===
        - Standings: {stats.get('standings_context', 'N/A')}
        - H2H History: {stats.get('h2h_summary', 'N/A')}
        - Home Advantage: {stats.get('home_advantage_context', 'N/A')}
        - Top Scorers: {top_scorers_str}
        
        === QUALITATIVE DATA (The Context) ===
        - Venue: {context.get('venue', 'Unknown')}
        - News Headlines: {context.get('recent_news', 'None')}
        - History: {context.get('historical_pedigree', 'None')}
        
        TASK:
        Based on YOUR specific persona, predict the outcome.
        
        REQUIRED JSON FORMAT:
        {{
            "home_win": 0.45,
            "draw": 0.25,
            "away_win": 0.30,
            "confidence": 0.8,
            "reasoning": "One sentence explaining why."
        }}
        """

    def _query_model(self, system_msg, user_msg):
        """Safe wrapper to call different LLM providers."""
        try:
            # --- OPENAI HANDLER ---
            if self.provider == 'openai':
                if not self.client:
                    raise ValueError("OpenAI Client not initialized (check API Key)")
                    
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                return resp.choices[0].message.content
            
            # --- ANTHROPIC CLAUDE HANDLER ---
            elif self.provider == 'anthropic':
                if not self.client:
                    raise ValueError("Anthropic Client not initialized (check API Key)")
                
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    temperature=0.2,
                    system=system_msg,
                    messages=[
                        {"role": "user", "content": user_msg},
                        {"role": "assistant", "content": "{"} 
                    ]
                )
                return "{" + message.content[0].text

            return "{}" 
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ LLM Error ({self.persona} / {self.provider}): {error_msg}")
            
            fallback_json = json.dumps({
                "home_win": 0.33, 
                "draw": 0.34, 
                "away_win": 0.33, 
                "confidence": 0, 
                "reasoning": f"AI Failure: {error_msg}"
            })
            return fallback_json

    def _parse_json(self, text):
        try:
            cleaned_text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_text)
        except:
            return {"home_win": 0.33, "draw": 0.34, "away_win": 0.33, "confidence": 0.1, "reasoning": "JSON Parse Error", "agent": self.persona}