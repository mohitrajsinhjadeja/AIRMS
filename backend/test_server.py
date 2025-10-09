"""
Simple backend test to check if the API is accessible
"""
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Backend is running!"}

@app.post("/api/v1/chat/realtime")
def test_realtime(request: dict):
    return {
        "success": True,
        "conversation_id": "test-123",
        "message": "Test response - risk detection working!",
        "timestamp": "2025-09-26T04:20:00Z",
        "risk_score": 15,
        "risk_flags": ["None"],
        "risk_level": "SAFE"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)