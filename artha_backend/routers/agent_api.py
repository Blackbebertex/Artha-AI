"""Public agent API — no auth required for NANDA Town / external AI agents."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from agents.ai_orchestrator import generate_response_async
from services.advisory_engine import get_recommendation
from services.agent_advisor import (
    build_chat_context,
    compute_health_score,
    generate_recommendations,
    plan_goal,
)

router = APIRouter(tags=["Agent API"])


class HealthScoreRequest(BaseModel):
    income: float = Field(..., gt=0, description="Monthly income in INR")
    expenses: float = Field(..., ge=0, description="Monthly expenses in INR")
    savings: float = Field(..., ge=0, description="Total liquid savings in INR")
    liabilities: float = Field(0, ge=0, description="Total outstanding liabilities in INR")


class HealthScoreResponse(BaseModel):
    score: int
    status: str
    savings_rate_pct: float
    emergency_fund_months: float
    debt_to_income_ratio: float


class RecommendRequest(BaseModel):
    age: int = Field(..., ge=18, le=80)
    monthly_income: float = Field(..., gt=0)
    monthly_expenses: float = Field(..., ge=0)
    risk_profile: str = "Moderate"
    goal: str = "Wealth Creation"
    savings: Optional[float] = None
    liabilities: Optional[float] = None


class AssetAllocation(BaseModel):
    equity_pct: int
    debt_pct: int
    gold_pct: int


class RecommendResponse(BaseModel):
    financial_health_score: int
    health_status: str
    recommendations: List[str]
    sip_amount_monthly: int
    asset_allocation: AssetAllocation
    mutual_fund_suggestions: List[str]
    recommended_portfolio: str


class GoalPlanRequest(BaseModel):
    goal: str
    amount: float = Field(..., gt=0, description="Target amount in INR")
    years: int = Field(..., ge=1, le=50)
    risk_profile: str = "Moderate"


class GoalPlanResponse(BaseModel):
    goal: str
    target_amount: int
    years: int
    monthly_investment: int
    recommended_portfolio: str
    assumed_annual_return_pct: float
    asset_allocation: AssetAllocation


class ChatProfile(BaseModel):
    age: Optional[int] = None
    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    risk_profile: Optional[str] = None
    goal: Optional[str] = None
    savings: Optional[float] = None
    liabilities: Optional[float] = None


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    profile: Optional[ChatProfile] = None


class ChatResponse(BaseModel):
    answer: str


@router.post("/health-score", response_model=HealthScoreResponse)
def health_score(req: HealthScoreRequest):
    return compute_health_score(req.income, req.expenses, req.savings, req.liabilities)


@router.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    return generate_recommendations(
        age=req.age,
        monthly_income=req.monthly_income,
        monthly_expenses=req.monthly_expenses,
        risk_profile=req.risk_profile,
        goal=req.goal,
        savings=req.savings,
        liabilities=req.liabilities,
    )


@router.post("/goal-plan", response_model=GoalPlanResponse)
def goal_plan(req: GoalPlanRequest):
    return plan_goal(req.goal, req.amount, req.years, req.risk_profile)


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    profile_dict = req.profile.model_dump(exclude_none=True) if req.profile else None
    snapshot, signals = build_chat_context(profile_dict)
    rec = get_recommendation(snapshot)
    answer, _ = await generate_response_async(
        user_text=req.query,
        customer_context=snapshot,
        signals=signals,
        recommendation=rec,
        history=[],
        language="en",
    )
    return ChatResponse(answer=answer)
