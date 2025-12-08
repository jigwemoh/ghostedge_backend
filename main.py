import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel  # <--- THIS WAS MISSING
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Import our custom modules
# Make sure these folders exist: src/data/ and w5_engine/
from src.data.loader import real_data_loader
from w5_engine.debate import ConsensusEngine

load_dotenv()

app = FastAPI()
# ... imports ...

# --- ADD THIS BLOCK ---
@app.get("/")
def health_check():
    return {"status": "GhostEdge AI is Online", "version": "1.0"}
# ----------------------

# ... rest of your code ...
# Enable CORS so Lovable can talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the data we expect from the Frontend
class MatchRequest(BaseModel):
    event_id: int 
    home_team_id: int
    away_team_id: int
    league_id: int
    home_team_name: str
    away_team_name: str

@app.post("/analyze/consensus")
async def run_consensus(match: MatchRequest):
    try:
        print(f"👻 Analyzing Event {match.event_id} with Deep Data...")

        # 1. FETCH REAL DATA (From RapidAPI)
        match_context = real_data_loader.fetch_full_match_context(
            event_id=match.event_id,
            home_id=match.home_team_id,
            away_id=match.away_team_id,
            league_id=match.league_id
        )

        # 2. RUN W-5 ENGINE (The AI Debate)
        engine = ConsensusEngine(debate_rounds=2, min_agents=3)
        
        # Structure the data for the Agents
        agent_data_packet = {
            "home_team": match.home_team_name,
            "away_team": match.away_team_name,
            "quantitative_features": match_context['quantitative_features'],
            "qualitative_context": str(match_context['qualitative_context'])
        }

        # Start the debate
        result = engine.run_consensus(agent_data_packet)

        return {
            "consensus_prediction": result['consensus_prediction'],
            "confidence": result['confidence'],
            "debate_summary": result['debate_summary'],
            "match_data_used": match_context
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))