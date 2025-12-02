from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from roboflow import Roboflow
import random

app = FastAPI()

# --- CONFIGURATION ---
# 1. Allow Lovable to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. ROBOFLOW SETUP (Replace these with your keys)
ROBOFLOW_API_KEY = "YOUR_ROBOFLOW_API_KEY"
rf = Roboflow(api_key=ROBOFLOW_API_KEY)
# These come from your Roboflow URL: app.roboflow.com/WORKSPACE/PROJECT/VERSION
PROJECT_ID = "your-project-name" 
VERSION_NUMBER = 1 

# --- DATA MODELS ---
class PropRequest(BaseModel):
    player_name: str
    stat_category: str = "PTS"

class VisionRequest(BaseModel):
    image_url: str # The frontend sends a URL of the video frame

# --- ENDPOINTS ---

@app.get("/")
def home():
    return {"status": "GhostEdge Brain is Online"}

# 1. THE PROP MASTER (NBA Stats)
@app.post("/analyze/prop")
async def analyze_prop(request: PropRequest):
    try:
        # Get Player ID
        player_dict = players.find_players_by_full_name(request.player_name)
        if not player_dict: return {"error": "Player not found"}
        player_id = player_dict[0]['id']

        # Get Last 5 Games
        gamelog = playergamelog.PlayerGameLog(player_id=player_id, season='2024-25')
        df = gamelog.get_data_frames()[0].head(5)
        
        if df.empty: return {"error": "No stats available"}

        # Calculate Average
        avg_stat = df[request.stat_category].mean()
        
        # Simulated "Edge" Logic
        defense_rating = random.randint(100, 120) 
        edge_multiplier = 1.05 if defense_rating > 110 else 0.95
        prediction = avg_stat * edge_multiplier
        
        return {
            "player": request.player_name,
            "stat": request.stat_category,
            "avg_last_5": round(avg_stat, 1),
            "prediction": round(prediction, 1),
            "edge": "High Value" if prediction > avg_stat else "Pass",
            "narrative": f"Opponent defense is rated {defense_rating}. Trends suggest a {round((edge_multiplier-1)*100)}% shift."
        }
    except Exception as e:
        return {"error": str(e)}

# 2. THE GHOST VISION (Roboflow AI)
@app.post("/analyze/vision")
async def analyze_vision(request: VisionRequest):
    try:
        # Load your specific model
        project = rf.workspace().project(PROJECT_ID)
        model = project.version(VERSION_NUMBER).model
        
        # Send the image URL to Roboflow's Cloud (Not your server RAM)
        # This keeps your Render server from crashing
        prediction = model.predict(request.image_url, confidence=40, overlap=30).json()
        
        # Parse the result
        detected_objects = [p['class'] for p in prediction['predictions']]
        
        return {
            "detected": detected_objects,
            "raw_data": prediction,
            "alert": "CORNER KICK" if "corner_kick" in detected_objects else "No Signal"
        }
    except Exception as e:
        return {"error": str(e)}