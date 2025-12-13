import os
from typing import Dict, Any
import json
from dotenv import load_dotenv

load_dotenv()

class LLMAgent:
    # We standardized the parameter name to 'provider' here
    def __init__(self, persona_type: str, provider: str = 'openai', model_name: str = 'claude-3-opus-20240229'):
        self.persona = persona_type
        self.provider = provider
        self.model = model_name
        self.client = self._init_client()

    def _init_client(self):
        # Initialize clients based on provider
        if self.provider == 'openai':
            from openai import OpenAI
            return OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        elif self.provider == 'anthropic':
            from anthropic import Anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                print(f"❌ CRITICAL: ANTHROPIC_API_KEY is missing for {self.persona}")
            return Anthropic(api_key=api_key)
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
            # --- OPENAI CALL ---
            if self.provider == 'openai':
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
                    temperature=0.2, 
                    response_format={"type": "json_object"}
                )
                return resp.choices[0].message.content
            
            # --- ANTHROPIC CALL (FIXED) ---
            elif self.provider == 'anthropic':
                # Claude doesn't use 'response_format={"type": "json_object"}' natively like OpenAI yet
                # We prompt it explicitly and parse the text.
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    temperature=0.2,
                    system=system_msg,
                    messages=[
                        {"role": "user", "content": user_msg},
                        # Pre-filling the assistant message enforces JSON structure start
                        {"role": "assistant", "content": "{"} 
                    ]
                )
                # We add the '{' back because pre-fill doesn't include it in the output content
                return "{" + message.content[0].text

            # --- GOOGLE CALL ---
            elif self.provider == 'google':
                response = self.client.generate_content(f"{system_msg}\n\nDATA:\n{user_msg}")
                return response.text

            return "{}" 
        except Exception as e:
            print(f"❌ LLM Error ({self.provider}): {e}")
            # Return a valid JSON string as fallback
            return '{"home_win": 0.33, "draw": 0.34, "away_win": 0.33, "confidence": 0, "reasoning": "Error calling AI provider"}'

    def _parse_json(self, text):
        try:
            # Clean up potential markdown formatting from Claude/Gemini
            cleaned_text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_text)
        except:
            return {"home_win": 0.33, "draw": 0.34, "away_win": 0.33, "confidence": 0.1, "reasoning": "JSON Parse Error", "agent": self.persona}