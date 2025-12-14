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
        # 1. SOCCERDATA (Deterministic Logic)
        if self.provider == 'soccerdata':
            return None

        # 2. OPENAI
        if self.provider == 'openai':
            from openai import OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key: print(f"⚠️ {self.persona}: OPENAI_API_KEY missing")
            return OpenAI(api_key=api_key)
        
        # 3. ANTHROPIC (CLAUDE)
        elif self.provider == 'anthropic':
            from anthropic import Anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key: print(f"⚠️ {self.persona}: ANTHROPIC_API_KEY missing")
            return Anthropic(api_key=api_key)
            
        return None

    def analyze(self, match_data: Dict[str, Any], blind_mode: bool = True) -> Dict[str, Any]:
        # Logic Path
        if self.provider == 'soccerdata':
            return self._analyze_with_data(match_data)

        # AI Path
        system_prompt = self._get_persona_prompt()
        user_prompt = self._build_data_prompt(match_data)
        response_text = self._query_model(system_prompt, user_prompt)
        return self._parse_json(response_text)

    def _analyze_with_data(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deterministic analysis using hard data."""
        stats = match_data.get("quantitative_features", {})
        h2h = str(stats.get('h2h_summary', ''))
        form = str(stats.get('home_form', ''))
        
        reasoning = f"Analysis based on hard data. H2H: {h2h}. Form: {form}."
        
        # Simple Logic
        home_prob = 0.33
        if "meetings" in h2h.lower(): home_prob += 0.1
        if "W-W" in form: home_prob += 0.1
        
        return {
            "home_win": round(home_prob, 2),
            "draw": 0.33,
            "away_win": round(1.0 - home_prob - 0.33, 2),
            "confidence": 0.8,
            "reasoning": reasoning
        }

    def _get_persona_prompt(self):
        if self.persona == 'tactician':
            return "ROLE: Tactical Scout. Focus on style and venue."
        elif self.persona == 'sentiment_analyst':
            return "ROLE: Sentiment Tracker. Focus on news and pressure."
        return "You are a sports analyst."

    def _build_data_prompt(self, data):
        stats = data.get("quantitative_features", {})
        return f"Match: {data.get('home_team')} vs {data.get('away_team')}. Stats: {stats}"

    def _query_model(self, system_msg, user_msg):
        try:
            if self.provider == 'openai':
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                return resp.choices[0].message.content
            
            # FIX: Added actual Anthropic Call
            elif self.provider == 'anthropic':
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
            print(f"❌ Error: {e}")
            return '{"home_win": 0.33, "draw": 0.34, "away_win": 0.33, "confidence": 0, "reasoning": "AI Provider Error"}'

    def _parse_json(self, text):
        try:
            return json.loads(text.replace("```json", "").replace("```", "").strip())
        except:
            return {"home_win": 0.33, "draw": 0.34, "away_win": 0.33, "confidence": 0, "reasoning": "JSON Parse Error"}