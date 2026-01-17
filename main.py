from fastapi import FastAPI
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

app = FastAPI()

def get_player_stats(player_name, stat_category):
    # 1. Find Player ID
    nba_players = players.find_players_by_full_name(player_name)
    if not nba_players:
        return {"error": "Player not found"}
    
    player_id = nba_players[0]['id']
    
    # 2. Get Game Log (Last 10 games)
    gamelog = playergamelog.PlayerGameLog(player_id=player_id, season='2025-26')
    df = gamelog.get_data_frames()[0]
    
    # Filter for the specific stat (e.g., PTS, REB, AST)
    recent_stats = df[stat_category.upper()].head(10).tolist()
    avg = sum(recent_stats) / len(recent_stats)
    
    return {
        "player": nba_players[0]['full_name'],
        "recent_history": recent_stats,
        "average": round(avg, 2)
    }

@app.get("/predict")
async def predict(player: str, stat: str, line: float):
    data = get_player_stats(player, stat)
    
    # Simple logic: If avg > line, predict "Over"
    # In a real app, you'd subtract points if playing a top-5 defense
    diff = data['average'] - line
    confidence = min(abs(diff * 10), 95) # Dummy confidence logic
    
    prediction = "OVER" if diff > 0 else "UNDER"
    
    return {
        "player": data['player'],
        "stat": stat,
        "prediction": prediction,
        "confidence": f"{round(confidence, 1)}%",
        "history": data['recent_history']
    }