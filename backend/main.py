import os
import json
import uuid
import time
import hashlib
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
from collections import deque

# Load environment variables from root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Initialize FastAPI
app = FastAPI(title="Election Process Assistant")

# Enable CORS for the Radiant Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Google AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

# Load election data
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "election_timeline.json")
def load_substrate():
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
        checksum = hashlib.sha256(json.dumps(data).encode()).hexdigest()
        return data, checksum

ELECTION_DATA, DATA_CHECKSUM = load_substrate()

# Background Polling Simulation (Sector Epsilon)
def poll_updates():
    global ELECTION_DATA, DATA_CHECKSUM
    # In a production environment, this would hit an external API
    # For this genesis, we simulate a check every 300 seconds
    while True:
        time.sleep(300)
        ELECTION_DATA, DATA_CHECKSUM = load_substrate()

@app.on_event("startup")
async def startup_event():
    import threading
    threading.Thread(target=poll_updates, daemon=True).start()

# Stateful Memory Store (Sector Alpha)
# Key: session_id, Value: deque of message history
SESSIONS = {}

# Semantic Cache for common queries (Sector Epsilon)
COMMON_QUERIES = {
    "how to register": "To register to vote, you must fill out the official registration form and submit it to your local election office with a valid ID.",
    "registration deadline": "The registration deadline is typically 30 days before the election day. Please check your specific local phase for exact dates.",
    "what do i need to vote": "You generally need a government-issued photo ID and proof of residence. Specific requirements are listed in the 'Verification' phase."
}

# Rate limiting
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
             raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    
    RATE_LIMITS[client_ip] = current_time
    response = await call_next(request)
    return response

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/data")
def get_election_data():
    """Provides the election data with an integrity checksum."""
    return {
        "data": ELECTION_DATA,
        "checksum": DATA_CHECKSUM,
        "timestamp": time.time()
    }

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process user queries based on election data.
    """
    try:
        # Input Sanitization
        sanitized_query = request.query.strip().lower()[:500]

        # Sector Epsilon: Sub-millisecond Cache Check
        if sanitized_query in COMMON_QUERIES:
             return QueryResponse(
                 response=COMMON_QUERIES[sanitized_query],
                 phase="registration",
                 session_id=request.session_id or str(uuid.uuid4())
             )
        
        session_id = request.session_id or str(uuid.uuid4())
        if session_id not in SESSIONS:
            SESSIONS[session_id] = deque(maxlen=5) # Maintain last 5 exchanges
        
        history = list(SESSIONS[session_id])
        history_text = "\n".join([f"User: {h['user']}\nAI: {h['ai']}" for h in history])
        
        # Construct the grounding context
        context = json.dumps(ELECTION_DATA, indent=2)
        
        prompt = f"""
        Provide accurate guidance based on the following election data.
        
        DATA SUBSTRATE:
        {context}
        
        CONVERSATIONAL HISTORY:
        {history_text}
        
        USER QUERY:
        {sanitized_query}
        
        INSTRUCTIONS:
        1. Ground your response STRICTLY in the provided election data.
        2. Neutrality Shield: Use a formal, dispassionate, and professional tone. Avoid bias, adjectives of opinion, or political commentary.
        3. Adaptive Verbosity: If the user asks for a summary, be brief. If they ask for details, provide a comprehensive breakdown.
        4. Resilience: If the data does not contain the answer, do not hallucinate. Direct the user to official government portals.
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
