import os
from dotenv import load_dotenv

# 1. LOAD KEYS
load_dotenv()

# 2. IMPORTS
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.data.loader import real_data_loader
from w5_engine.debate import ConsensusEngine

app = FastAPI()

# 3. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. DATA MODEL
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
        print(f"👻 Analyzing {match.home_team_name} vs {match.away_team_name} (Event {match.event_id})...")

        # A. FETCH DEEP DATA (Lineups, News, Trophies)
        match_context = real_data_loader.fetch_full_match_context(
            event_id=match.event_id,
            home_id=match.home_team_id,
            away_id=match.away_team_id,
            league_id=match.league_id
        )

        # B. PREPARE AGENT PACKET
        agent_data_packet = {
            "home_team": match.home_team_name,
            "away_team": match.away_team_name,
            "quantitative_features": match_context['quantitative_features'],
            "qualitative_context": str(match_context['qualitative_context'])
        }

        # C. RUN DEBATE
        engine = ConsensusEngine(debate_rounds=2, min_agents=3)
        result = engine.run_consensus(agent_data_packet)

        # D. RETURN TO FRONTEND
        return {
            "consensus_prediction": result['consensus_prediction'],
            "confidence": result['confidence'],
            "debate_summary": result['debate_summary'],
            "match_data_used": match_context
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))