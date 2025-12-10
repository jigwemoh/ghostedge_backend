import os
from dotenv import load_dotenv

# 1. FORCE LOAD ENVIRONMENT VARIABLES
# This loads keys from the .env file automatically
load_dotenv()

# 2. DEBUG: VERIFY KEYS ARE LOADED
openai_key = os.getenv("OPENAI_API_KEY")
rapid_key = os.getenv("RAPIDAPI_KEY")

if openai_key:
    # We print only the first 5 chars to avoid leaking it in logs
    print(f"✅ SYSTEM: OpenAI Key loaded (Starts with {openai_key[:5]}...)")
else:
    print("❌ ERROR: OpenAI Key is MISSING. Check your .env file.")

if rapid_key:
    print(f"✅ SYSTEM: RapidAPI Key loaded.")
else:
    print("⚠️ WARNING: RapidAPI Key is MISSING. Data loader will return empty.")

# 3. IMPORTS
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Custom Modules (Ensure these files exist in your folder structure)
from src.data.loader import real_data_loader
from w5_engine.debate import ConsensusEngine

app = FastAPI()

# 4. CORS SETUP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. HEALTH CHECK (GET /)
@app.get("/")
def health_check():
    return {
        "status": "GhostEdge AI is Online", 
        "mode": "Event-Centric (SoccerData/FBref)", 
        "version": "3.2"
    }

# 6. DATA MODEL
class MatchRequest(BaseModel):
    event_id: int          # Kept for frontend compatibility
    home_team_id: int
    away_team_id: int
    league_id: int
    home_team_name: str    # CRITICAL: We now use this for data fetching
    away_team_name: str    # CRITICAL: We now use this for data fetching

# 7. ANALYSIS ENDPOINT (POST /analyze/consensus)
@app.post("/analyze/consensus")
async def run_consensus(match: MatchRequest):
    try:
        print(f"👻 GhostEdge Analyzing: {match.home_team_name} vs {match.away_team_name}...")

        # --- STEP A: FETCH REAL DATA ---
        match_context = real_data_loader.fetch_full_match_context(
            home_team=match.home_team_name,
            away_team=match.away_team_name
        )

        # --- STEP B: PREPARE DATA FOR AI AGENTS ---
        # FIX: We must pass 'qualitative_context' as a DICT, not a STRING.
        # The agents.py file expects to use .get('venue'), which requires a dictionary.
        agent_data_packet = {
            "home_team": match.home_team_name,
            "away_team": match.away_team_name,
            "quantitative_features": match_context.get('quantitative_features', {}),
            "qualitative_context": match_context.get('qualitative_context', {}) 
        }

        # --- STEP C: RUN THE W-5 DEBATE ENGINE ---
        engine = ConsensusEngine(debate_rounds=2, min_agents=3)
        result = engine.run_consensus(agent_data_packet)

        # --- STEP D: RETURN RESULT TO FRONTEND ---
        return {
            "consensus_prediction": result['consensus_prediction'],
            "confidence": result['confidence'],
            "agreement_score": result.get('agreement_score', 0.5),
            "debate_summary": result['debate_summary'],
            "match_data_used": match_context
        }

    except Exception as e:
        print(f"❌ SERVER ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))