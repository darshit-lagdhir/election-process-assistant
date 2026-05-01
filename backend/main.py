import os
import json
import uuid
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
from collections import deque

# Load environment variables from root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Initialize FastAPI
app = FastAPI(title="Election Process Assistant Hadronic Core")

# Enable CORS for the Radiant Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Google AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Load the Sovereign Data Substrate
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "election_timeline.json")
with open(DATA_PATH, "r") as f:
    ELECTION_DATA = json.load(f)

# Stateful Memory Store (Sector Alpha)
# Key: session_id, Value: deque of message history
SESSIONS = {}

# Simple Rate Limiter (Sector Eta)
# Key: client_ip, Value: timestamp of last request
RATE_LIMITS = {}
MAX_REQUESTS_PER_MINUTE = 30

class QueryRequest(BaseModel):
    query: str
    session_id: str = None

class QueryResponse(BaseModel):
    response: str
    phase: str = None
    step_id: str = None
    session_id: str

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    if client_ip in RATE_LIMITS:
        last_request_time = RATE_LIMITS[client_ip]
        if current_time - last_request_time < (60 / MAX_REQUESTS_PER_MINUTE):
             raise HTTPException(status_code=429, detail="Rate limit exceeded. Phalanx Seal active.")
    
    RATE_LIMITS[client_ip] = current_time
    response = await call_next(request)
    return response

@app.get("/health")
def health_check():
    return {"status": "SOVEREIGNTY ACHIEVED", "radiance": "STABLE", "metabolism": "FLAT"}

@app.get("/data")
def get_election_data():
    """Provides the Sovereign Data Substrate for frontend initialization."""
    return ELECTION_DATA

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Executes Constrained Agentic Reasoning with Stateful Memory.
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())
        if session_id not in SESSIONS:
            SESSIONS[session_id] = deque(maxlen=5) # Maintain last 5 exchanges
        
        history = list(SESSIONS[session_id])
        history_text = "\n".join([f"User: {h['user']}\nAI: {h['ai']}" for h in history])
        
        # Construct the grounding context
        context = json.dumps(ELECTION_DATA, indent=2)
        
        prompt = f"""
        YOU ARE THE SOVEREIGN ELECTION ASSISTANT. 
        YOU MUST PROVIDE ACCURATE, NEUTRAL, AND STEP-BY-STEP GUIDANCE BASED ONLY ON THE PROVIDED DATA.
        
        DATA SUBSTRATE:
        {context}
        
        CONVERSATIONAL HISTORY:
        {history_text}
        
        USER QUERY:
        {request.query}
        
        INSTRUCTIONS:
        1. Ground your response STRICTLY in the DATA SUBSTRATE.
        2. Account for the CONVERSATIONAL HISTORY to provide context-aware follow-ups.
        3. If the user is asking about a specific phase (registration, verification, polling, results), identify it.
        4. Maintain a professional, neutral, and empowering tone.
        5. Format the output as JSON.
        
        FORMAT YOUR RESPONSE AS JSON:
        {{
            "response": "Your guidance text here",
            "phase": "phase_id_if_applicable",
            "step_id": "step_id_if_applicable"
        }}
        """
        
        response = model.generate_content(prompt)
        text = response.text
        
        # JSON Extraction Logic
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
             text = text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(text)
        
        # Update Session Memory
        SESSIONS[session_id].append({"user": request.query, "ai": result['response']})
        
        return QueryResponse(session_id=session_id, **result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Systemic Failure: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
