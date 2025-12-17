import os
from dotenv import load_dotenv

# 1. FORCE LOAD ENVIRONMENT VARIABLES
load_dotenv()

# 2. DEBUG: VERIFY KEYS ARE LOADED
openai_key = os.getenv("OPENAI_API_KEY")
rapid_key = os.getenv("RAPIDAPI_KEY")

if openai_key:
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

# Custom Modules
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

# 5. HEALTH CHECK
@app.get("/")
def health_check():
    return {
        "status": "GhostEdge AI is Online", 
        "mode": "Event-Centric (RapidAPI)", 
        "version": "3.4"
    }

# 6. DATA MODEL
class MatchRequest(BaseModel):
    event_id: int          
    home_team_id: int
    away_team_id: int
    league_id: int
    home_team_name: str    
    away_team_name: str    

# 7. ANALYSIS ENDPOINT
@app.post("/analyze/consensus")
async def run_consensus(match: MatchRequest):
    try:
        print(f"👻 GhostEdge Analyzing: {match.home_team_name} vs {match.away_team_name} (Event {match.event_id})...")

        # --- STEP A: FETCH REAL DATA ---
        # Pass all required IDs for proper API enrichment
        match_context = real_data_loader.fetch_full_match_context(
            home_team=match.home_team_name,
            away_team=match.away_team_name,
            event_id=match.event_id,
            league_id=match.league_id,
            home_team_id=match.home_team_id,
            away_team_id=match.away_team_id
        )

        # --- STEP B: PREPARE DATA FOR AI AGENTS ---
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