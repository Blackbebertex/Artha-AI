"""
ARTHA AI – FastAPI Backend
Integrated Agentic Flow + 7-Step Wealth Prompt Chain
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import datetime
from datetime import timezone
import re
import secrets

from services.customer_snapshot import get_snapshot
from services.behaviour_engine import compute_signals
from services.advisory_engine import get_recommendation
from services.consent_service import check_consent
from services.audit_logger import log_event, log_chain_event
from services.rm_handoff import trigger_handoff
from services.product_catalog import get_catalog_json
from services.session_store import add_session, get_history, get_language, append_turn
from services.pilot_config import is_wealth_chain_enabled, can_run_deep_chain, record_deep_chain
from services.execution_gateway import submit_execution_intent
from services.database import init_db
from agents.ai_orchestrator import generate_response_async
from agents.avatar_voice import synthesize_voice_details
from agents.compliance_guardrails import check_safety
from agents.wealth_chain.router import classify_route
from agents.wealth_chain.orchestrator import run_wealth_chain, get_plan
from agents.wealth_chain.schemas import AuditDecision, ChainMetadata
from agents.llm_telemetry import get_recent_events

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
    mode: Literal["quick", "deep", "auto"] = "auto"

class ChainMetadataResponse(BaseModel):
    confidence: float = 0.0
    decision: str = "approve"
    steps_completed: int = 0
    plan_id: Optional[str] = None
    revise_loops: int = 0
    path: str = "quick"

class MessageResponse(BaseModel):
    reply_text: str
    recommendation_ids: List[str] = []
    recommendation: Optional[dict] = None
    chain_metadata: Optional[ChainMetadataResponse] = None
    avatar_script: Optional[str] = None

class RecommendationFeedbackRequest(BaseModel):
    feedback: str

class VoiceSynthesisRequest(BaseModel):
    text: str
    language: str = "en"

class VoiceSynthesisResponse(BaseModel):
    audio_url: str
    duration_ms: int
    viseme_cues: List[dict]

class ConsentRequest(BaseModel):
    purpose: str = "Personalised wealth advisory"
    scope: List[str] = ["BALANCE", "TRANSACTIONS", "SUMMARY"]

class HandoffRequest(BaseModel):
    reason: str = "Customer requested human advisor"

class WealthPlanRequest(BaseModel):
    session_id: Optional[str] = None
    message_text: str = "Generate my full wealth plan"

VALID_TOKENS = {"demo-token": {"customer_id": "cust_001", "name": "Riya Kapoor"}}


def validate_bank_token(token: str) -> Optional[dict]:
    return VALID_TOKENS.get(token)


async def handle_message(
    session_id: str,
    customer_id: str,
    user_text: str,
    mode: str = "auto",
) -> MessageResponse:
    if not check_consent(customer_id):
        return MessageResponse(
            reply_text="I cannot access your account details due to lack of active data consent. Please authorize sharing first.",
            recommendation_ids=[],
        )

    snapshot = get_snapshot(customer_id)
    transactions = snapshot.get("transactions", [])
    signals = compute_signals(transactions)
    rec = get_recommendation(snapshot)
    history = get_history(session_id)
    language = get_language(session_id)

    lower_text = user_text.lower()
    if re.search(r"\b(rm|advisor|human|priya|talk|connect|escalate)\b", lower_text):
        trigger_handoff(customer_id, "User requested direct relationship manager escalation.")

    route = classify_route(user_text, mode)
    chain_meta = None
    avatar_script = None
    reply = ""
    rec_ids: List[str] = []

    if route == "deep" and is_wealth_chain_enabled(customer_id):
        if not can_run_deep_chain(customer_id):
            reply = "You've reached today's limit for full wealth plans. I can still help with quick questions, or connect you to your RM."
            route = "quick"
        else:
            record_deep_chain(customer_id)
            state, meta = await run_wealth_chain(
                snapshot=snapshot,
                signals=signals,
                recommendation=rec,
                product_catalog=get_catalog_json(),
                user_text=user_text,
                customer_id=customer_id,
            )
            chain_meta = ChainMetadataResponse(**meta.model_dump())
            log_chain_event(
                state.plan_id,
                customer_id,
                state.raw_steps,
                meta.confidence,
                meta.decision,
            )
            if state.step7 and state.step7.decision == AuditDecision.REJECT:
                trigger_handoff(customer_id, state.step7.rejection_reason or "Master auditor rejected plan")
                reply = (
                    "I've reviewed your profile carefully but I'd like your relationship manager to "
                    "take a closer look before we finalise a plan. Shall I connect you now?"
                )
            elif state.step6:
                reply = state.step6.avatar_script
                avatar_script = state.step6.avatar_script
            else:
                reply = state.step7.customer_summary if state.step7 else "Your wealth plan is being prepared."
            if rec.get("recommendation_id"):
                rec_ids = [rec["recommendation_id"]]
    if route == "quick" or not reply:
        reply, rec_ids = await generate_response_async(
            user_text=user_text,
            customer_context=snapshot,
            signals=signals,
            recommendation=rec,
            history=history,
            language=language,
        )
        chain_meta = ChainMetadataResponse(path="quick")

    append_turn(session_id, user_text, reply, language)
    log_event({
        "session_id": session_id,
        "customer_id": customer_id,
        "user_query": user_text,
        "bot_reply": reply,
        "route": route,
        "savings_rate": signals.get("savings_rate"),
        "active_recommendation": rec.get("recommendation_id"),
        "chain_metadata": chain_meta.model_dump() if chain_meta else None,
    })

    rec_details = rec if rec.get("recommendation_id") in rec_ids else None
    return MessageResponse(
        reply_text=reply,
        recommendation_ids=rec_ids,
        recommendation=rec_details,
        chain_metadata=chain_meta,
        avatar_script=avatar_script,
    )


app = FastAPI(title="ARTHA API Gateway", version="2.0.0")

ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:5500",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)


@app.on_event("startup")
def startup():
    init_db()


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    token = credentials.credentials if credentials else None
    user_info = validate_bank_token(token) if token else None
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token. Use 'demo-token' for the demo.",
        )
    return user_info


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ARTHA API Gateway",
        "version": "2.0.0",
        "wealth_chain_enabled": is_wealth_chain_enabled("cust_001"),
        "time": datetime.datetime.now(timezone.utc).isoformat(),
    }


@app.get("/v1/admin/llm-telemetry")
def llm_telemetry(user=Depends(get_current_user)):
    return {"events": get_recent_events(50)}


@app.post("/v1/session/start", response_model=SessionStartResponse)
def start_session(req: SessionStartRequest, user=Depends(get_current_user)):
    session_id = "sess_" + secrets.token_urlsafe(16)
    add_session(session_id, req.language)
    return SessionStartResponse(
        session_id=session_id,
        customer_id=user["customer_id"],
        language=req.language,
    )


@app.get("/v1/customer/snapshot")
def get_customer_snapshot(user=Depends(get_current_user)):
    if not check_consent(user["customer_id"]):
        raise HTTPException(status_code=403, detail="Active consent required")
    try:
        return get_snapshot(user["customer_id"])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/v1/conversation/history")
def conversation_history(session_id: str, user=Depends(get_current_user)):
    return {"session_id": session_id, "turns": get_history(session_id)}


@app.post("/v1/consent/request")
def consent_request(req: ConsentRequest, user=Depends(get_current_user)):
    log_event({
        "event_type": "consent_request",
        "customer_id": user["customer_id"],
        "purpose": req.purpose,
        "scope": req.scope,
    })
    return {
        "status": "pending",
        "message": "Consent request initiated — redirect to Account Aggregator flow",
        "consent_id": f"consent_{secrets.token_hex(4)}",
    }


@app.post("/v1/handoff/rm")
def handoff_rm(req: HandoffRequest, user=Depends(get_current_user)):
    payload = trigger_handoff(user["customer_id"], req.reason)
    log_event({"event_type": "rm_handoff_api", **payload})
    return payload


@app.post("/v1/conversation/message", response_model=MessageResponse)
async def conversation_message(req: MessageRequest, user=Depends(get_current_user)):
    try:
        return await handle_message(
            req.session_id,
            user["customer_id"],
            req.message_text,
            req.mode,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/v1/wealth/plan")
async def wealth_plan(req: WealthPlanRequest, user=Depends(get_current_user)):
    session_id = req.session_id or ("sess_" + secrets.token_urlsafe(8))
    if req.session_id is None:
        add_session(session_id, "en")
    result = await handle_message(session_id, user["customer_id"], req.message_text, "deep")
    plan_id = result.chain_metadata.plan_id if result.chain_metadata else None
    plan = get_plan(plan_id) if plan_id else None
    return {
        "plan_id": plan_id,
        "reply_text": result.reply_text,
        "chain_metadata": result.chain_metadata,
        "plan": plan.raw_steps if plan else None,
    }


@app.get("/v1/wealth/plan/{plan_id}")
def get_wealth_plan(plan_id: str, user=Depends(get_current_user)):
    plan = get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"plan_id": plan_id, "steps": plan.raw_steps}


@app.post("/v1/recommendations/{rec_id}/feedback")
def recommendation_feedback(rec_id: str, req: RecommendationFeedbackRequest, user=Depends(get_current_user)):
    log_event({
        "event_type": "recommendation_feedback",
        "customer_id": user["customer_id"],
        "rec_id": rec_id,
        "feedback": req.feedback,
    })
    return {"status": "recorded", "rec_id": rec_id}


@app.post("/v1/execution/intent")
def execution_intent(product_id: str, action: str, amount: float, user=Depends(get_current_user)):
    return submit_execution_intent(user["customer_id"], product_id, action, amount)


@app.post("/v1/voice/synthesize", response_model=VoiceSynthesisResponse)
async def voice_synthesize(req: VoiceSynthesisRequest, user=Depends(get_current_user)):
    details = synthesize_voice_details(req.text, req.language)
    return VoiceSynthesisResponse(
        audio_url=details["audio_url"],
        duration_ms=details["duration_ms"],
        viseme_cues=details["viseme_cues"],
    )
