import os
from dotenv import load_dotenv

# 1. FORCE LOAD ENVIRONMENT VARIABLES
# This must happen immediately so the AI agents can find your API keys.
load_dotenv()

# 2. DEBUG: VERIFY KEYS ARE LOADED
openai_key = os.getenv("OPENAI_API_KEY")
rapid_key = os.getenv("RAPIDAPI_KEY")

if openai_key:
    print(f"✅ SYSTEM: OpenAI Key loaded (Starts with {openai_key[:5]}...)")
else:
    print("❌ ERROR: OpenAI Key is MISSING. The AI Debate will fail.")

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
# This allows your Lovable/React frontend to talk to this Python backend.
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
        "mode": "Event-Centric (Free API)", 
        "version": "3.0"
    }

# 6. DATA MODEL
# This matches the JSON payload sent from your Lovable Frontend.
class MatchRequest(BaseModel):
    event_id: int          # CRITICAL: This connects to the Free Live API
    home_team_id: int
    away_team_id: int
    league_id: int
    home_team_name: str
    away_team_name: str

# 7. ANALYSIS ENDPOINT (POST /analyze/consensus)
@app.post("/analyze/consensus")
async def run_consensus(match: MatchRequest):
    try:
        print(f"👻 GhostEdge Analyzing: {match.home_team_name} vs {match.away_team_name} (Event {match.event_id})...")

        # --- STEP A: FETCH REAL DATA ---
        # We call the loader using the 'event_id' which gives us the deep data (lineups, h2h, etc.)
        match_context = real_data_loader.fetch_full_match_context(
            event_id=match.event_id,
            home_id=match.home_team_id,
            away_id=match.away_team_id,
            league_id=match.league_id
        )

        # --- STEP B: PREPARE DATA FOR AI AGENTS ---
        # The W-5 Engine expects a dictionary with 'quantitative' and 'qualitative' buckets.
        # We convert the qualitative dict to a string so the LLM can read it as a text narrative.
        agent_data_packet = {
            "home_team": match.home_team_name,
            "away_team": match.away_team_name,
            "quantitative_features": match_context['quantitative_features'],
            "qualitative_context": str(match_context['qualitative_context'])
        }

        # --- STEP C: RUN THE W-5 DEBATE ENGINE ---
        # Initialize the debate (3 agents: Statistician, Tactician, Sentiment)
        engine = ConsensusEngine(debate_rounds=2, min_agents=3)
        
        # Run the consensus logic
        result = engine.run_consensus(agent_data_packet)

        # --- STEP D: RETURN RESULT TO FRONTEND ---
        return {
            "consensus_prediction": result['consensus_prediction'],
            "confidence": result['confidence'],
            "agreement_score": result.get('agreement_score', 0.5),
            "debate_summary": result['debate_summary'],
            "match_data_used": match_context # Returning this helps you debug the UI
        }

    except Exception as e:
        print(f"❌ SERVER ERROR: {str(e)}")
        # Return a 500 error so the frontend knows to show an error message
        raise HTTPException(status_code=500, detail=str(e))

# Run command reminder:
# python -m uvicorn main:app --reload