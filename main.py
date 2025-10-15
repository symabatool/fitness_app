from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from collections import Counter


app = FastAPI(title="Fitness Log API", version="1.0.0")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
LOG_NOT_FOUND_MSG = "Log not found"

# Data model
class FitnessEntry(BaseModel):
    id: Optional[int] = None
    activity: str
    duration: int  # in minutes
    intensity: Optional[str] = None  # e.g., Low, Moderate, High
    mood: Optional[str] = None       # e.g., Happy, Tired, Relaxed
    calories_burned: Optional[int] = None
    #date: Optional[date] = None
    notes: Optional[str] = None
    
    

# In-memory storage
fitness_logs: List[FitnessEntry] = []
log_counter = 1

# Helper function
def find_log_by_id(log_id: int) -> Optional[FitnessEntry]:
    return next((log for log in fitness_logs if log.id == log_id), None)

# Create
@app.post("/logs/", response_model=FitnessEntry)
def create_log(entry: FitnessEntry):
    global log_counter
    entry.id = log_counter
    log_counter += 1
    fitness_logs.append(entry)
    return entry

# Read all
@app.get("/logs/", response_model=List[FitnessEntry])
def get_all_logs():
    return fitness_logs

# Read one
@app.get("/logs/{log_id}", response_model=FitnessEntry)
def get_log(log_id: int):
    log = find_log_by_id(log_id)
    if not log:
        raise HTTPException(status_code=404, detail=LOG_NOT_FOUND_MSG)
    return log

# Update
@app.put("/logs/{log_id}", response_model=FitnessEntry)
def update_log(log_id: int, updated: FitnessEntry):
    log = find_log_by_id(log_id)
    if not log:
        raise HTTPException(status_code=404, detail=LOG_NOT_FOUND_MSG)
    log.activity = updated.activity
    log.duration = updated.duration
    log.intensity = updated.intensity
    log.mood = updated.mood
    log.calories_burned = updated.calories_burned
    log.date = updated.date
    log.notes = updated.notes
    return log

# Delete
@app.delete("/logs/{log_id}")
def delete_log(log_id: int):
    global fitness_logs
    for i, log in enumerate(fitness_logs):
        if log.id == log_id:
            fitness_logs.pop(i)
            return {"message": f"Log {log_id} deleted successfully"}
    raise HTTPException(status_code=404, detail=LOG_NOT_FOUND_MSG)

# Progress tracking
@app.get("/progress/")
def get_progress():
    total_duration = sum(e.duration for e in fitness_logs)
    total_calories = sum(e.calories_burned or 0 for e in fitness_logs)
    activities = [e.activity for e in fitness_logs]
    most_common = Counter(activities).most_common(1)
    return {
        "total_duration": total_duration,
        "total_calories": total_calories,
        "most_frequent_activity": most_common[0][0] if most_common else None
    }

# Smart suggestion
@app.get("/suggest/")
def suggest_activity():
    if not fitness_logs:
        return {"suggestion": "Try a light walk to get started!"}
    last_mood = fitness_logs[-1].mood
    if last_mood == "Tired":
        return {"suggestion": "Consider yoga or stretching today."}
    elif last_mood == "Energetic":
        return {"suggestion": "Go for a run or HIIT session!"}
    return {"suggestion": "Keep it balanced with moderate cardio."}

# Root
@app.get("/")
def root():
    return {
        "message": "Welcome to the Fitness Log API",
        "name": "Syma batool",
        "class": "Python Developer"
    }