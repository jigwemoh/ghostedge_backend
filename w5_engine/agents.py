import os
from typing import Dict, Any
import json

class LLMAgent:
    def __init__(self, persona_type: str, llm_provider: str = 'openai', model_name: str = 'gpt-4'):
        self.persona = persona_type
        self.provider = llm_provider
        self.model = model_name
        self.client = self._init_client()

    def _init_client(self):
        # Initialize clients based on provider
        if self.provider == 'openai':
            from openai import OpenAI
            return OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        elif self.provider == 'anthropic':
            from anthropic import Anthropic
            return Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        elif self.provider == 'google':
            import google.generativeai as genai
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
            return genai.GenerativeModel('gemini-pro')
        return None

    def analyze(self, match_data: Dict[str, Any], blind_mode: bool = True) -> Dict[str, Any]:
        """
        Main analysis function. 
        blind_mode=True means 'Don't see other agents' opinions yet'.
        """
        system_prompt = self._get_persona_prompt()
        user_prompt = self._build_data_prompt(match_data)

        response_text = self._query_model(system_prompt, user_prompt)
        return self._parse_json(response_text)

    def _get_persona_prompt(self):
        """Defines HOW the agent thinks."""
        if self.persona == 'statistician':
            return """
            ROLE: Ruthless Quantitative Analyst.
            DIRECTIVE: You care ONLY about numbers, xG, trends, and history. Ignore narratives.
            OUTPUT: You must output a valid JSON object.
            LOGIC:
            1. Compare Head-to-Head history (Dominance factor).
            2. Analyze recent form (Last 5 games).
            3. Check league standings gap.
            4. If the Home team is >5 spots higher, they are heavy favorites.
            """
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
        """Injects the RAPIDAPI data into the prompt."""
        stats = data.get("quantitative_features", {})
        context = data.get("qualitative_context", {})
        
        return f"""
        MATCH: {data.get('home_team')} vs {data.get('away_team')}
        
        === QUANTITATIVE DATA (The Numbers) ===
        - Standings: {stats.get('standings_context', 'N/A')}
        - H2H History: {stats.get('h2h_summary', 'N/A')}
        - Home Advantage: {stats.get('home_advantage_context', 'N/A')}
        - Top Scorers: {', '.join(stats.get('key_threats', {}).get('top_scorers', []))}
        
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
            if self.provider == 'openai':
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
                    temperature=0.2, # Low temperature for accuracy
                    response_format={"type": "json_object"}
                )
                return resp.choices[0].message.content
            
            # (Add Anthropic/Google blocks here if needed, keeping OpenAI as default for now)
            return "{}" 
        except Exception as e:
            print(f"❌ LLM Error: {e}")
            return '{"home_win": 0.33, "draw": 0.33, "away_win": 0.33, "confidence": 0, "reasoning": "Error"}'

    def _parse_json(self, text):
        try:
            return json.loads(text)
        except:
            # Fallback if LLM returns bad JSON
            return {"home_win": 0.34, "draw": 0.33, "away_win": 0.33, "confidence": 0.1, "reasoning": "Parse Error", "agent": self.persona}