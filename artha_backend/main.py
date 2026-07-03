"""
ARTHA AI – FastAPI Backend
Integrated Agentic Flow
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import datetime
from datetime import timezone
import re
import secrets

# Import core engines and agents
from services.customer_snapshot import get_snapshot
from services.behaviour_engine import compute_signals
from services.advisory_engine import get_recommendation
from services.consent_service import check_consent
from services.audit_logger import log_event
from services.rm_handoff import trigger_handoff
from agents.ai_orchestrator import generate_response_async
from agents.avatar_voice import synthesize_voice_details
from agents.compliance_guardrails import check_safety

# ──────────────────────────────────────────────
# Pydantic Schemas
# ──────────────────────────────────────────────
class SessionStartRequest(BaseModel):
    language: str = "en"

class SessionStartResponse(BaseModel):
    session_id: str
    customer_id: str
    language: str

class MessageRequest(BaseModel):
    session_id: str
    message_text: str

class MessageResponse(BaseModel):
    reply_text: str
    recommendation_ids: List[str] = []
    recommendation: Optional[dict] = None

class RecommendationFeedbackRequest(BaseModel):
    feedback: str

class VoiceSynthesisRequest(BaseModel):
    text: str
    language: str = "en"

class VoiceSynthesisResponse(BaseModel):
    audio_url: str
    duration_ms: int
    viseme_cues: List[dict]

# ──────────────────────────────────────────────
# Global Session Memory Store
# ──────────────────────────────────────────────
SESSION_HISTORIES = {}  # session_id -> list of {"user": str, "bot": str}
SESSION_LANGUAGES = {}  # session_id -> language code

def _add_session(session_id: str, language: str):
    if len(SESSION_HISTORIES) >= 100:
        # Evict oldest session
        oldest_key = next(iter(SESSION_HISTORIES))
        SESSION_HISTORIES.pop(oldest_key, None)
        SESSION_LANGUAGES.pop(oldest_key, None)
    SESSION_HISTORIES[session_id] = []
    SESSION_LANGUAGES[session_id] = language

VALID_TOKENS = {"demo-token": {"customer_id": "cust_001", "name": "Riya Kapoor"}}

def validate_bank_token(token: str) -> Optional[dict]:
    """Synchronous token lookup – swap for real JWT verification in production."""
    return VALID_TOKENS.get(token)

async def handle_message(session_id: str, customer_id: str, user_text: str) -> MessageResponse:
    """
    Orchestrates the full agentic flow: snapshot, consent check, behavior signals,
    advisory recommendation, dialogue generation, safety checks, and audit logging.
    """
    # 1. Validate consent
    if not check_consent(customer_id):
        reply = "I cannot access your account details due to lack of active data consent. Please authorize sharing first."
        return MessageResponse(reply_text=reply, recommendation_ids=[])
        
    # 2. Retrieve customer financial profile snapshot
    snapshot = get_snapshot(customer_id)
    
    # 3. Compute behavior analytics signals from transaction logs
    transactions = snapshot.get("transactions", [])
    signals = compute_signals(transactions)
    
    # 4. Generate rules-based recommendation check
    rec = get_recommendation(snapshot)
    
    # 5. Extract session conversation history
    history = SESSION_HISTORIES.get(session_id, [])
    language = SESSION_LANGUAGES.get(session_id, "en")
    
    # 6. Check for manual RM escalation query first
    lower_text = user_text.lower()
    if re.search(r"\b(rm|advisor|human|priya|talk|connect|escalate)\b", lower_text):
        trigger_handoff(customer_id, "User requested direct relationship manager escalation.")
        
    # 7. Generate contextual language model response
    reply, rec_ids = await generate_response_async(
        user_text=user_text,
        customer_context=snapshot,
        signals=signals,
        recommendation=rec,
        history=history,
        language=language
    )
    
    # Update local conversation memory
    if session_id not in SESSION_HISTORIES:
        _add_session(session_id, language)
    SESSION_HISTORIES[session_id].append({"user": user_text, "bot": reply})
    
    # Cap memory window at 8 turns to prevent token drift
    if len(SESSION_HISTORIES[session_id]) > 8:
        SESSION_HISTORIES[session_id] = SESSION_HISTORIES[session_id][-8:]
        
    # 8. Log the event to compliance audit trail
    log_event({
        "session_id": session_id,
        "customer_id": customer_id,
        "user_query": user_text,
        "bot_reply": reply,
        "savings_rate": signals.get("savings_rate"),
        "active_recommendation": rec.get("recommendation_id")
    })
    
    rec_details = rec if rec.get("recommendation_id") in rec_ids else None
    return MessageResponse(reply_text=reply, recommendation_ids=rec_ids, recommendation=rec_details)

# ──────────────────────────────────────────────
# App Setup
# ──────────────────────────────────────────────
app = FastAPI(title="ARTHA API Gateway", version="1.0.0")

ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:5500",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    token = credentials.credentials if credentials else None
    user_info = validate_bank_token(token) if token else None
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token. Use 'demo-token' for the demo."
        )
    return user_info

# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "service": "ARTHA API Gateway", "time": datetime.datetime.now(timezone.utc).isoformat()}

@app.post("/v1/session/start", response_model=SessionStartResponse)
def start_session(req: SessionStartRequest, user=Depends(get_current_user)):
    session_id = "sess_" + secrets.token_urlsafe(16)
    _add_session(session_id, req.language)
    return SessionStartResponse(
        session_id=session_id,
        customer_id=user["customer_id"],
        language=req.language
    )

@app.get("/v1/customer/snapshot")
def get_customer_snapshot(user=Depends(get_current_user)):
    try:
        snapshot = get_snapshot(user["customer_id"])
        return snapshot
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@app.post("/v1/conversation/message", response_model=MessageResponse)
async def conversation_message(req: MessageRequest, user=Depends(get_current_user)):
    # Retrieve customer ID from token details
    customer_id = user["customer_id"]
    try:
        return await handle_message(req.session_id, customer_id, req.message_text)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@app.post("/v1/recommendations/{rec_id}/feedback")
def recommendation_feedback(rec_id: str, req: RecommendationFeedbackRequest, user=Depends(get_current_user)):
    log_event({
        "event_type": "recommendation_feedback",
        "customer_id": user["customer_id"],
        "rec_id": rec_id,
        "feedback": req.feedback
    })
    return {"status": "recorded", "rec_id": rec_id}

@app.post("/v1/voice/synthesize", response_model=VoiceSynthesisResponse)
async def voice_synthesize(req: VoiceSynthesisRequest, user=Depends(get_current_user)):
    details = synthesize_voice_details(req.text, req.language)
    return VoiceSynthesisResponse(
        audio_url=details["audio_url"],
        duration_ms=details["duration_ms"],
        viseme_cues=details["viseme_cues"]
    )
