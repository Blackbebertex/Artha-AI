"""Pydantic schemas for the 7-step wealth prompt chain."""
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AuditDecision(str, Enum):
    APPROVE = "approve"
    REVISE = "revise"
    REJECT = "reject"


class RedFlag(BaseModel):
    code: str
    severity: str
    description: str


class Step1Output(BaseModel):
    risk_profile: str
    income_stability: str
    red_flags: List[RedFlag] = Field(default_factory=list)
    category_breakdown: Dict[str, float] = Field(default_factory=dict)
    savings_rate: float = 0.0
    summary: str = ""


class SmartGoal(BaseModel):
    goal_id: str
    name: str
    target_amount: float
    current_amount: float
    target_date: str
    monthly_sip_required: float = 0.0
    feasibility_score: float = Field(ge=0, le=100, default=50.0)


class Step2Output(BaseModel):
    goals: List[SmartGoal] = Field(default_factory=list)
    goal_hierarchy_notes: str = ""


class Allocation(BaseModel):
    product_id: str
    product_name: str
    allocation_pct: float
    rationale: str


class Step3Output(BaseModel):
    allocations: List[Allocation] = Field(default_factory=list)
    tax_notes: List[str] = Field(default_factory=list)
    sebi_disclaimer: str = (
        "This is personalised information and guidance, not regulated investment advice."
    )


class Step4Output(BaseModel):
    risks: List[str] = Field(default_factory=list)
    portfolio_flaws: List[str] = Field(default_factory=list)
    behavioral_traps: List[str] = Field(default_factory=list)


class Nudge(BaseModel):
    trigger: str
    message: str
    channel: str = "in_app"


class Step5Output(BaseModel):
    nudges: List[Nudge] = Field(default_factory=list)
    automation_rules: List[str] = Field(default_factory=list)
    defense_protocols: List[str] = Field(default_factory=list)


class ObjectionHandler(BaseModel):
    objection: str
    response: str


class Step6Output(BaseModel):
    avatar_script: str
    objection_handlers: List[ObjectionHandler] = Field(default_factory=list)
    disclosures: List[str] = Field(default_factory=list)
    language: str = "en"


class AuditCheck(BaseModel):
    name: str
    passed: bool
    detail: str


class Step7Output(BaseModel):
    decision: AuditDecision
    confidence: float = Field(ge=0, le=100)
    checks: List[AuditCheck] = Field(default_factory=list)
    fix_targets: List[int] = Field(default_factory=list)
    customer_summary: str = ""
    rejection_reason: Optional[str] = None


class ChainMetadata(BaseModel):
    confidence: float = 0.0
    decision: str = "approve"
    steps_completed: int = 7
    plan_id: Optional[str] = None
    revise_loops: int = 0
    path: str = "deep"


class ChainState(BaseModel):
    step1: Optional[Step1Output] = None
    step2: Optional[Step2Output] = None
    step3: Optional[Step3Output] = None
    step4: Optional[Step4Output] = None
    step5: Optional[Step5Output] = None
    step6: Optional[Step6Output] = None
    step7: Optional[Step7Output] = None
    plan_id: str = ""
    raw_steps: Dict[str, Any] = Field(default_factory=dict)
